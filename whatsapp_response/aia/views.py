import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import openai

WHATSAPP_API_URL = 'https://graph.facebook.com/v20.0/418446388022428/messages'
ACCESS_TOKEN = 'EAB1oK7ZAIcN8BOyxTE77as9qqFeZA4XSzXzTRnVUNZBrurQqjkoZAmwylf28Vyu8aoLyTF0Mh597VVmLK7gD1smyvEs4fdefhZAJKKk8MfNbdp6FNEo1ZBygA078d8R59EqZAvBK73h9PcSQGBO9ZBaUCvh9ZAZAlK0XQRDghAPl3ZAPUxyNNZA6op51GKwZBOZCKx9FVq9lUZD'
VERIFY_TOKEN = 'hsdfbvhbsd2458@hvb'

#python manage.py runserver 0.0.0.0:8000 INICIAR O SERVIDOR
# Configure sua chave de API da OpenAI
OPENAI_API_KEY = 'sk-sWRHirl0JFEqwGx3CkHimusnbptw10qbKMOhbiEPAlT3BlbkFJdJE-EEFtw-1Co6wJIYd0pJodIFfXXzhmASjT0OoCUA'
openai.api_key = OPENAI_API_KEY

@csrf_exempt
def webhook(request):
    if request.method == 'GET':
        # Verificação do token
        hub_mode = request.GET.get('hub.mode')
        hub_challenge = request.GET.get('hub.challenge')
        hub_verify_token = request.GET.get('hub.verify_token')

        if hub_mode == 'subscribe' and hub_verify_token == VERIFY_TOKEN:
            return HttpResponse(hub_challenge, status=200)
        else:
            return HttpResponse('Error, invalid token', status=403)

    elif request.method == 'POST':
        # Processar a mensagem recebida via POST
        incoming_message = json.loads(request.body.decode('utf-8'))
        try:
            from_number = incoming_message['entry'][0]['changes'][0]['value']['messages'][0]['from']
            message_body = incoming_message['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']

            # Exibe a mensagem recebida no terminal
            print(f"Mensagem recebida de {from_number}: {message_body}")

            # Enviar a mensagem para o ChatGPT e obter a resposta
            response_message = get_chatgpt_response(message_body)

            # Enviar resposta automática
            send_message(from_number, response_message)

            return JsonResponse({'status': 'success'}, status=200)
        except (KeyError, IndexError) as e:
            print(f"Erro ao processar a mensagem: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'Method not allowed'}, status=405)

def send_message(to_number, message):
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Mensagem enviada para {to_number}: {message}")
        return response.json()
    else:
        print(f"Erro ao enviar mensagem para {to_number}: {response.text}")
        return {'status': 'error', 'message': response.text}


def get_chatgpt_response(user_message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Alterado para gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,
            temperature=0.7,
        )

        chat_response = response.choices[0].message['content'].strip()
        return chat_response

    except openai.error.AuthenticationError:
        print("Erro de autenticação com a API da OpenAI. Verifique sua chave de API.")
        return "Desculpe, ocorreu um erro de autenticação."
    except openai.error.PermissionError:
        print("Permissão negada para acessar o modelo especificado.")
        return "Desculpe, não tenho permissão para acessar o modelo solicitado."
    except Exception as e:
        print(f"Erro ao obter resposta do ChatGPT: {e}")
        return "Desculpe, ocorreu um erro ao processar sua solicitação."