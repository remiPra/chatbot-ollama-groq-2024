from django.shortcuts import render
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
import base64
from io import BytesIO
from PIL import Image
from django.shortcuts import render
from langchain_community.chat_models import ChatOllama

def image_view(request):
    if request.method == 'POST':
        # Récupérer l'image envoyée dans la requête
        image_file = request.FILES.get('image')
        if image_file:
            # Ouvrir l'image avec Pillow
            pil_image = Image.open(image_file)

            # Convertir l'image en base64
            buffered = BytesIO()
            pil_image.save(buffered, format="JPEG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

            # Initialiser le modèle ChatOllama
            model_name = 'llava:latest'
            llm = ChatOllama(model=model_name, temperature=0)

            def prompt_func(data):
                text = "extract text of image"
                image = data["image"]

                image_part = {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{image}",
                }

                content_parts = []

                text_part = {"type": "text", "text": text}

                content_parts.append(image_part)
                content_parts.append(text_part)

                return [HumanMessage(content=content_parts)]

            chain = prompt_func | llm | StrOutputParser()

            # Générer une réponse à partir de l'image et du texte
            response = chain.invoke({"text": "", "image": image_base64})

            # Rendre le template avec la réponse et l'image
            return render(request, 'image_view.html', {'response': response, 'image_base64': image_base64})

    # Rendre le template vide pour la première requête
    return render(request, 'image_view.html')