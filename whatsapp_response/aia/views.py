import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from openai import OpenAI


WHATSAPP_API_URL = 'https://graph.facebook.com/v20.0/418446388022428/messages'
ACCESS_TOKEN = 'EAB1oK7ZAIcN8BOyxTE77as9qqFeZA4XSzXzTRnVUNZBrurQqjkoZAmwylf28Vyu8aoLyTF0Mh597VVmLK7gD1smyvEs4fdefhZAJKKk8MfNbdp6FNEo1ZBygA078d8R59EqZAvBK73h9PcSQGBO9ZBaUCvh9ZAZAlK0XQRDghAPl3ZAPUxyNNZA6op51GKwZBOZCKx9FVq9lUZD'
VERIFY_TOKEN = 'hsdfbvhbsd2458@hvb'

#python manage.py runserver 0.0.0.0:8000 INICIAR O SERVIDOR
# Configure sua chave de API da OpenAI
client = OpenAI(api_key='sk-svcacct-za6uPwnTgcLBhsFQEMastiWByHViVQEaWERWpNtSkVmMTMKmxBDz1dCiSUy3mlyGfT3BlbkFJ-6C-GkvXVeRnC6aCXVP7yDf3xc_kjNsKQwaBByej4oGMnrJ7TfqJIY3_dz9jUQpLgA')
OPENAI_API_KEY = 'sk-svcacct-za6uPwnTgcLBhsFQEMastiWByHViVQEaWERWpNtSkVmMTMKmxBDz1dCiSUy3mlyGfT3BlbkFJ-6C-GkvXVeRnC6aCXVP7yDf3xc_kjNsKQwaBByej4oGMnrJ7TfqJIY3_dz9jUQpLgA'
OpenAI.api_key = OPENAI_API_KEY

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        incoming_message = json.loads(request.body.decode('utf-8'))
        try:
            from_number = incoming_message['entry'][0]['changes'][0]['value']['messages'][0]['from']
            message_body = incoming_message['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']

            # Exibe a mensagem recebida no terminal
            print(f"Mensagem recebida de {from_number}: {message_body}")

            # Determina o papel com base no conteúdo da mensagem
            if "criador de conteúdo" in message_body.lower():
                role = "criador_de_conteudo"
            elif "acompanhamento profissional" in message_body.lower():
                role = "acompanhamento_profissional"
            else:
                role = "atendente"  # Valor padrão

            # Enviar a mensagem para o ChatGPT e obter a resposta
            response_message = get_chatgpt_response(message_body, role)

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


def handle_whatsapp_request(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        role = request.POST.get('role')  # Exemplo: 'atendente', 'criador_de_conteudo', etc.

        # Obtenha a resposta da função de chat
        chat_response = get_chatgpt_response(user_message, role)

        return JsonResponse({"response": chat_response})

    return JsonResponse({"error": "Invalid request method"}, status=400)


def get_chatgpt_response(user_message, role):
    try:
        # Mapeamento de papéis para diferentes configurações do sistema
        roles = {
            "atendente": "Você é um atendente virtual, pronto para responder perguntas de clientes e resolver suas dúvidas.",
            "criador_de_conteudo": "Você é um criador de conteúdo criativo, capaz de produzir textos envolventes, posts para redes sociais, e artigos.",
            "acompanhamento_profissional": "Você é um mentor especializado em acompanhamento profissional, oferecendo conselhos sobre carreira, produtividade e desenvolvimento pessoal."
        }

        # Escolhe o papel correto com base no parâmetro role
        system_message = roles.get(role, "Você é um assistente útil.")

        # Chamada para o modelo OpenAI usando a nova interface
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Ajuste o modelo de acordo com a necessidade
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,
            temperature=0.7,
            logprobs=True,  # Incluindo logprobs para maior controle, se necessário
            top_logprobs=2
        )

        # Extração da resposta do modelo
        chat_response = response['choices'][0]['message']['content'].strip()
        return chat_response

    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"
