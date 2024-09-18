import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests

WHATSAPP_API_URL = 'https://graph.facebook.com/v16.0/+554184209376/messages'
ACCESS_TOKEN = 'EAB1oK7ZAIcN8BO45PZBBwwwvfIbkLw38tFzN1TNsFmL1IzvlgdDrYIetVQiwrcZCHPKeMsLQrqHLLuBkwdMalfjemDApPvcqmMIuBIVZBhlbi0ZCm7KcF9iofeQa7fi41jSiZBAkWsJSnkznxifZC378lz4v5UoaxSo0fQYpbrPjy9P0ApoF19dztYgDlEurkd4TliIZA0WMRlznAVU3XjI0JMIznRgZD'
VERIFY_TOKEN = 'jdsajdbvhjbsdhbsdfvafvf'

#python manage.py runserver 0.0.0.0:8000 INICIAR O SERVIDOR
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
            
            # Lógica para responder automaticamente às mensagens
            if message_body.strip().lower() == "estou testando a api do whatsapp":
                response_message = "Sua mensagem foi recebida com sucesso! Como posso ajudar?"
            else:
                response_message = f"Mensagem recebida: {message_body}"

            # Enviar resposta automática
            send_message(from_number, response_message)

            return JsonResponse({'status': 'success'}, status=200)
        except (KeyError, IndexError) as e:
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