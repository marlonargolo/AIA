import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from openai import OpenAI 
from django.shortcuts import render
from .models import Message

WHATSAPP_API_URL = 'https://graph.facebook.com/v20.0/418446388022428/messages'
ACCESS_TOKEN = 'EAB1oK7ZAIcN8BOZB4hMYto3ZBaVRicB2I2JaxzdrSBik6QvAp6iqHWZAGd7sNNnyN9yyhwCbqI204GNviZANTDXBNNJcTTT94ieYFBzkqg7yZCPvNKT7DaM5KipOcDeMgPYZCPRGAO7ZBXOxonnmVZANd7dvbg6q9h4jUWtoFUzeciUTGlu0JTQeUqNMeqs2xcQoRgZAAZD'
VERIFY_TOKEN = 'token_@verify123123'


WHATSAPP_API_URL = 'https://graph.facebook.com/v20.0/418446388022428/messages'
ACCESS_TOKEN = 'EAB1oK7ZAIcN8BO0Fuo1CAHaJcyZCSNuf9GUCGRiSqYUZAExPDp8dZBQq9ZCePauKn0CigXY8DPV44VffwLxUmJg4zHbxnEo6L1F8VIdOAF6SK5eZB1JKcJJX9JSPEsMTWVGoDHW0KKDqCKZAK3roNZBXodRZBpJg6LJe6nvKt11wO7ZBTy2xiaBbLJNnsTbe2jVmZBWu3UZD'
VERIFY_TOKEN = 'hsdfbvhbsd2458@hvb'

#python manage.py runserver 0.0.0.0:8000 INICIAR O SERVIDOR
# Configure sua chave de API da OpenAI
client = OpenAI(api_key='sk-svcacct-za6uPwnTgcLBhsFQEMastiWByHViVQEaWERWpNtSkVmMTMKmxBDz1dCiSUy3mlyGfT3BlbkFJ-6C-GkvXVeRnC6aCXVP7yDf3xc_kjNsKQwaBByej4oGMnrJ7TfqJIY3_dz9jUQpLgA')
OPENAI_API_KEY = 'sk-svcacct-za6uPwnTgcLBhsFQEMastiWByHViVQEaWERWpNtSkVmMTMKmxBDz1dCiSUy3mlyGfT3BlbkFJ-6C-GkvXVeRnC6aCXVP7yDf3xc_kjNsKQwaBByej4oGMnrJ7TfqJIY3_dz9jUQpLgA'
OpenAI.api_key = OPENAI_API_KEY
# Variável para armazenar IDs de mensagens já processadas (idealmente, isso seria um banco de dados)
processed_message_ids = set()

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        try:
            # Decodifica o corpo da mensagem recebida
    if request.method == 'GET':
        verify_token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        if verify_token == VERIFY_TOKEN:
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse('Erro de verificação do token.', status=403)

    elif request.method == 'POST':
        try:
            incoming_message = json.loads(request.body.decode('utf-8'))

            # Verifique se 'messages' está presente no JSON recebido
            entry = incoming_message.get('entry', [])
            if not entry:
                print("Evento sem 'entry'. Ignorado.")
                return JsonResponse({'status': 'ignored', 'message': "'entry' não encontrado"}, status=200)

            changes = entry[0].get('changes', [])
            if not changes:
                print("Evento sem 'changes'. Ignorado.")
                return JsonResponse({'status': 'ignored', 'message': "'changes' não encontrado"}, status=200)

            value = changes[0].get('value', {})
            if 'messages' not in value:
                print("Evento sem 'messages'. Ignorado.")
                return JsonResponse({'status': 'ignored', 'message': "'messages' não encontrado"}, status=200)

            # Extraia as informações da mensagem
            message = value['messages'][0]
            from_number = message.get('from')
            message_body = message.get('text', {}).get('body')

            # Salva a mensagem recebida
            Message.objects.create(sender=from_number, body=message_body, direction='received')

            if not message_body:
                raise KeyError("'body' não encontrado na mensagem")

            # Exibe a mensagem recebida no terminal
            print(f"Mensagem recebida de {from_number}: {message_body}")

            # Lógica para definir o papel
            if "criador de conteúdo" in message_body.lower():
                role = "criador_de_conteudo"
            elif "acompanhamento profissional" in message_body.lower():
                role = "acompanhamento_profissional"
            else:
                role = "atendente"  # Valor padrão

            # Envia a mensagem para o ChatGPT e obtém a resposta
            response_message = get_chatgpt_response(message_body, role)
            Message.objects.create(sender='bot', body=response_message, direction='sent')

            # Enviar resposta automática
            send_message(from_number, response_message)

            return JsonResponse({'status': 'success'}, status=200)

        except (KeyError, IndexError) as e:
            print(f"Erro ao processar a mensagem: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'Method not allowed'}, status=405)


def atendimento(request):
    return render(request, 'inicio.html')

def acompanhamento(request):
    return render(request, 'index.html')


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
            model="gpt-4",  # Ajuste o modelo de acordo com a necessidade
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,
            temperature=0.7,
            logprobs=True,  # Incluindo logprobs para maior controle, se necessário
            top_logprobs=2
        )

        # Extração da resposta correta da API
        # O erro ocorre aqui, porque a resposta deve ser acessada diretamente via `.content` no atributo `choices`
        chat_response = response.choices[0].message.content.strip()  # Corrigido para acessar o conteúdo corretamente
        return chat_response

    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"
    

def get_messages(request):
    messages = Message.objects.all().order_by('timestamp')
    messages_data = [{"sender": msg.sender, "body": msg.body, "direction": msg.direction, "timestamp": msg.timestamp} for msg in messages]
    return JsonResponse(messages_data, safe=False)

def home(request):
    return render(request, 'home.html')

def cadastro(request):
    return render(request, 'cadastro.html')

def login(request):
    return render(request, 'login.html')

def perfil(request):
    return render(request, 'perfil.html')

