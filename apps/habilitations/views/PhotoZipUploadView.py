from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
import zipfile
import os
from django.conf import settings
import uuid
from PIL import Image

class PhotoZipUploadView(APIView):
    """
    Vue pour traiter un fichier ZIP contenant des photos et les enregistrer
    """
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        # Vérifiez si un fichier est fourni dans la requête
        if 'zip_file' not in request.FILES:
            return Response({'error': 'Aucun fichier ZIP fourni'}, status=status.HTTP_400_BAD_REQUEST)
        
        zip_file = request.FILES['zip_file']
        
        # Vérifier si c'est un fichier ZIP
        if not zip_file.name.endswith('.zip'):
            return Response({'error': 'Le fichier doit être au format ZIP'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer un dossier temporaire pour extraire les fichiers
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', str(uuid.uuid4()))
        os.makedirs(temp_dir, exist_ok=True)
        
        # Dossier où les photos seront finalement stockées
        photos_dir = os.path.join(settings.MEDIA_ROOT, 'photos')
        os.makedirs(photos_dir, exist_ok=True)
        
        # Liste pour stocker les chemins des photos enregistrées
        saved_photos = []
        
        # Extraire et traiter le contenu du ZIP
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                # Extraire tous les fichiers dans le dossier temporaire
                zip_ref.extractall(temp_dir)
                
                # Parcourir tous les fichiers extraits
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_ext = os.path.splitext(file)[1].lower()
                        
                        # Vérifier si c'est une image
                        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                            try:
                                # Vérifier si c'est une image valide avec PIL
                                with Image.open(file_path) as img:
                                    # Conserver le nom original du fichier
                                    save_path = os.path.join(photos_dir, file)
                                    
                                    # Gérer le cas où un fichier avec le même nom existe déjà
                                    if os.path.exists(save_path):
                                        base_name, ext = os.path.splitext(file)
                                        counter = 1
                                        while os.path.exists(save_path):
                                            save_path = os.path.join(photos_dir, f"{base_name}_{counter}{ext}")
                                            counter += 1
                                    
                                    # Enregistrer l'image
                                    img.save(save_path)
                                    saved_photos.append({
                                        'name': os.path.basename(save_path),
                                        'path': os.path.relpath(save_path, settings.MEDIA_ROOT)
                                    })
                            except Exception as e:
                                # Si on ne peut pas ouvrir le fichier comme une image, on continue
                                continue
                
                # Supprimer le dossier temporaire après traitement
                for root, dirs, files in os.walk(temp_dir, topdown=False):
                    for file in files:
                        os.remove(os.path.join(root, file))
                    for dir in dirs:
                        os.rmdir(os.path.join(root, dir))
                os.rmdir(temp_dir)
                
                return Response({
                    'message': f'{len(saved_photos)} photos ont été extraites et enregistrées avec succès',
                    'photos': saved_photos
                }, status=status.HTTP_201_CREATED)
                
        except zipfile.BadZipFile:
            # Nettoyer le dossier temporaire en cas d'erreur
            if os.path.exists(temp_dir):
                for root, dirs, files in os.walk(temp_dir, topdown=False):
                    for file in files:
                        os.remove(os.path.join(root, file))
                    for dir in dirs:
                        os.rmdir(os.path.join(root, dir))
                os.rmdir(temp_dir)
            
            return Response({'error': 'Fichier ZIP corrompu ou invalide'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Nettoyer le dossier temporaire en cas d'erreur
            if os.path.exists(temp_dir):
                for root, dirs, files in os.walk(temp_dir, topdown=False):
                    for file in files:
                        os.remove(os.path.join(root, file))
                    for dir in dirs:
                        os.rmdir(os.path.join(root, dir))
                os.rmdir(temp_dir)
            
            return Response({'error': f'Une erreur est survenue: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Configuration dans urls.py
"""
from django.urls import path
from .views import PhotoZipUploadView

urlpatterns = [
    path('upload-photos-zip/', PhotoZipUploadView.as_view(), name='upload-photos-zip'),
]
"""

# Exemple d'utilisation avec un client
"""
import requests

url = 'http://votre-domaine.com/api/upload-photos-zip/'
files = {'zip_file': open('photos.zip', 'rb')}
response = requests.post(url, files=files)
print(response.json())
"""