import pickle
import base64
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from langchain_community.chat_models import ChatOllama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import os
import requests
from django.conf import settings
import mimetypes
from io import BytesIO

def ollama_chat(request):
    model_name = 'mistral'

    encoded_memory = request.session.get('encoded_memory', None)
    if encoded_memory:
        pickled_memory = base64.b64decode(encoded_memory.encode('utf-8'))
        memory = pickle.loads(pickled_memory)
    else:
        memory = ConversationBufferMemory(
            memory_key='history',
            input_key='input'
        )

    chat = ChatOllama(model=model_name, max_new_tokens=80)
    conversation = ConversationChain(
        llm=chat,
        memory=memory,
    )

    if request.method == 'POST':
        user_input = request.POST.get('question', '')
        if user_input:
            chat_history = memory.load_memory_variables({}).get('history', [])
            response = conversation.predict(input=user_input, history=chat_history)

            pickled_memory = pickle.dumps(memory)
            encoded_memory = base64.b64encode(pickled_memory).decode('utf-8')
            request.session['encoded_memory'] = encoded_memory

            # Récupérer le contenu audio à partir de l'API OpenAI
            audio_content = get_speech_from_openai(response)
            print("Contenu audio reçu de l'API OpenAI :")
            print(audio_content)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Encoder le contenu audio en base64 pour l'inclure dans la réponse JSON
                audio_base64 = base64.b64encode(audio_content).decode('utf-8')
                return JsonResponse({'human': user_input, 'AI': response, 'audio': audio_base64})
            else:
                # Jouer l'audio directement dans la vue
                audio_bytesio = BytesIO(audio_content)
                mime_type, _ = mimetypes.guess_type('response.mp3')
                response = HttpResponse(streaming_content=iter(lambda: audio_bytesio.read(8192), b''), content_type=mime_type)
                response['Content-Disposition'] = 'inline; filename="response.mp3"'
                return response

    chat_history = memory.load_memory_variables({}).get('history', [])
    openai_api_key = settings.OPENAI_API
    return render(request, 'ollama_chat.html', {'chat_history': chat_history, 'openai_api_key': openai_api_key})

def clear_memory(request):
    if request.method == 'POST':
        request.session.pop('encoded_memory', None)
    return redirect('ollama_chat')

def get_speech_from_openai(text):
    openai_api_key = settings.OPENAI_API

    if not openai_api_key:
        raise ValueError("La clé API OpenAI n'est pas définie")

    request_body = {
        "model": "tts-1",
        "input": text,
        "voice": "nova"
    }

    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post("https://api.openai.com/v1/audio/speech", headers=headers, json=request_body)

    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Erreur lors de la récupération de la réponse vocale: {response.text}")