"""
URL configuration for chatbot2024 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from monapp import views
from monapp.ollama_chat_view import ollama_chat, clear_memory
from monapp.image_view import image_view
urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.home, name='home'),  # Supposons que la vue s'appelle 'home'
    # ... autres patterns d'url ...
    path('clear_memory/', views.clear_memory, name='clear_memory'),
    path('ollama_chat/', ollama_chat, name='ollama_chat'),
    path('image/', image_view, name='image_view'),


]
