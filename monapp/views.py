import pickle
import base64
from django.shortcuts import render, redirect
from django.http import JsonResponse
from langchain_groq import ChatGroq
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from django.conf import settings
import os
import requests

def home(request):
    groq_api_key = settings.GROQ_API
    model = 'mixtral-8x7b-32768'
    
    # Tentative de récupération de la mémoire de la conversation depuis la session
    encoded_memory = request.session.get('encoded_memory', None)
    if encoded_memory:
        pickled_memory = base64.b64decode(encoded_memory)
        memory = pickle.loads(pickled_memory)
    else:
        memory = ConversationBufferMemory(k=10)

    groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model)
    conversation = ConversationChain(llm=groq_chat, memory=memory)
    
    if request.method == 'POST':
        user_question = request.POST.get('question', '')
        if user_question:
            response = conversation.predict(input=f"{user_question}\n\nla langue qui doit être utilisée pour répondre est le français")
            
            chat_history = request.session.get('chat_history', [])
            chat_history.append({'human': user_question, 'AI': response})
            request.session['chat_history'] = chat_history
            
            pickled_memory = pickle.dumps(memory)
            encoded_memory = base64.b64encode(pickled_memory).decode('utf-8')
            request.session['encoded_memory'] = encoded_memory
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'human': user_question, 'AI': response})
            return redirect('home')  # Redirection pour forcer le rafraîchissement si non-AJAX
            
    chat_history = request.session.get('chat_history', [])
    return render(request, 'home.html', {'chat_history': chat_history})

def clear_memory(request):
    if request.method == 'POST':
        request.session.pop('encoded_memory', None)
        request.session.pop('chat_history', None)
    return redirect('home')


def get_speech_from_openai(text):
    openai_api_key = settings.OPENAI_API  # Assurez-vous d'avoir défini votre clé API dans les variables d'environnement

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
