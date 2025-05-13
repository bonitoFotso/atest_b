from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
import zipfile
import os
import shutil
from django.conf import settings
import uuid
from PIL import Image
import logging
import json
from django.db import transaction

logger = logging.getLogger(__name__)

class PhotoZipUploadView(APIView):
    """
    Vue pour traiter un fichier ZIP contenant des photos organisées par dossiers de référence 
    et les enregistrer en préservant la structure
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
        session_id = str(uuid.uuid4())
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', session_id)
        os.makedirs(temp_dir, exist_ok=True)
        
        # Structure pour stocker les informations sur les photos traitées
        processed_data = {
            'references': {}
        }
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                # Liste tous les fichiers dans le ZIP pour analyse
                zip_file_list = zip_ref.namelist()
                
                # Détecter la structure du ZIP
                reference_folders = set()
                logos = {}
                
                for file_path in zip_file_list:
                    parts = file_path.split('/')
                    if len(parts) > 1 and parts[0] and not file_path.endswith('/'):
                        reference_folders.add(parts[0])
                        
                        # Identifier les logos dans chaque dossier
                        if parts[-1].lower() in ['logo.png', 'logo.jpg', 'logo.jpeg']:
                            logos[parts[0]] = file_path
                
                # Extraire tous les fichiers dans le dossier temporaire
                zip_ref.extractall(temp_dir)
                
                # Traiter les fichiers par référence
                for reference in reference_folders:
                    reference_temp_dir = os.path.join(temp_dir, reference)
                    if not os.path.isdir(reference_temp_dir):
                        continue
                    
                    # Utiliser la référence comme nom du projet
                    project_name = reference
                    
                    # Créer le dossier de référence qui est aussi le dossier du projet
                    project_dir = os.path.join(settings.MEDIA_ROOT, 'photos', project_name)
                    os.makedirs(project_dir, exist_ok=True)
                    
                    # Initialiser les données pour cette référence
                    processed_data['references'][reference] = {
                        'photos': [],
                        'has_logo': False
                    }
                    
                    # Traiter le logo s'il existe dans ce dossier
                    if reference in logos:
                        logo_temp_path = os.path.join(temp_dir, logos[reference])
                        if os.path.exists(logo_temp_path):
                            try:
                                # Vérifier si c'est une image valide
                                with Image.open(logo_temp_path) as img:
                                    logo_save_path = os.path.join(project_dir, 'logo.png')
                                    
                                    # Optimiser le logo et le convertir en PNG si nécessaire
                                    logo_img = img.convert('RGBA')
                                    logo_img.save(logo_save_path, 'PNG', optimize=True)
                                    
                                    processed_data['references'][reference]['has_logo'] = True
                                    processed_data['references'][reference]['logo_path'] = os.path.relpath(
                                        logo_save_path, settings.MEDIA_ROOT
                                    )
                            except Exception as e:
                                logger.error(f"Erreur lors du traitement du logo dans {reference}: {str(e)}")
                    
                    # Traiter les photos dans ce dossier de référence
                    for file_name in os.listdir(reference_temp_dir):
                        # Ignorer les logos déjà traités
                        if file_name.lower() in ['logo.png', 'logo.jpg', 'logo.jpeg']:
                            continue
                        
                        file_path = os.path.join(reference_temp_dir, file_name)
                        file_ext = os.path.splitext(file_name)[1].lower()
                        
                        # Vérifier si c'est une image
                        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                            try:
                                # Vérifier si c'est une image valide avec PIL
                                with Image.open(file_path) as img:
                                    # Conserver le nom original du fichier
                                    save_path = os.path.join(project_dir, file_name)
                                    
                                    # Si un fichier avec le même nom existe déjà, le supprimer
                                    if os.path.exists(save_path):
                                        os.remove(save_path)
                                    
                                    # Optimiser et enregistrer l'image
                                    if file_ext in ['.jpg', '.jpeg']:
                                        img.save(save_path, 'JPEG', quality=85, optimize=True)
                                    elif file_ext == '.png':
                                        img.save(save_path, 'PNG', optimize=True)
                                    else:
                                        img.save(save_path)
                                    
                                    # Extraire les métadonnées du nom de fichier
                                    # Format attendu: Nom_Prenom_Reference.ext
                                    metadata = self._extract_metadata_from_filename(file_name)
                                    
                                    # Ajouter à la liste des photos traitées
                                    processed_data['references'][reference]['photos'].append({
                                        'name': os.path.basename(save_path),
                                        'path': os.path.relpath(save_path, settings.MEDIA_ROOT),
                                        'metadata': metadata
                                    })
                            except Exception as e:
                                logger.error(f"Erreur lors du traitement de l'image {file_name}: {str(e)}")
                                continue
                
                    # Créer un fichier metadata.json dans le dossier du projet
                    try:
                        with open(os.path.join(project_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
                            # Créer un sous-ensemble de données pour ce projet spécifique
                            project_data = {
                                'project_name': project_name,
                                'reference': reference,
                                'photos': processed_data['references'][reference]['photos'],
                                'has_logo': processed_data['references'][reference]['has_logo']
                            }
                            
                            if processed_data['references'][reference]['has_logo']:
                                project_data['logo_path'] = processed_data['references'][reference]['logo_path']
                                
                            json.dump(project_data, f, ensure_ascii=False, indent=2)
                    except Exception as e:
                        logger.error(f"Erreur lors de la création du fichier metadata.json pour {reference}: {str(e)}")
                
                # Compter le nombre total de photos traitées
                total_photos = sum(
                    len(ref_data['photos']) 
                    for ref_data in processed_data['references'].values()
                )
                
                # Créer une structure résumée pour la réponse
                response_data = {
                    'message': f'{total_photos} photos ont été extraites et enregistrées avec succès',
                    'references_processed': len(reference_folders),
                    'references': {
                        ref: {
                            'photo_count': len(ref_data['photos']),
                            'has_logo': ref_data['has_logo']
                        }
                        for ref, ref_data in processed_data['references'].items()
                    },
                    'total_photos': total_photos
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
        except zipfile.BadZipFile:
            logger.error(f"Fichier ZIP corrompu: {zip_file.name}")
            return Response({'error': 'Fichier ZIP corrompu ou invalide'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Erreur lors du traitement du ZIP: {str(e)}")
            return Response({'error': f'Une erreur est survenue: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        finally:
            # Nettoyer le dossier temporaire
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage du dossier temporaire: {str(e)}")
    
    def _extract_metadata_from_filename(self, filename):
        """
        Extrait les métadonnées (nom, prénom, référence) à partir du nom de fichier.
        Format attendu: Nom_Prenom_Reference.ext
        """
        base_name = os.path.splitext(filename)[0]
        parts = base_name.split('_')
        
        metadata = {
            'last_name': parts[0] if len(parts) > 0 else '',
            'first_name': parts[1] if len(parts) > 1 else '',
            'reference': parts[2] if len(parts) > 2 else ''
        }
        
        return metadata


class PhotoProjectListView(APIView):
    """
    Vue pour lister tous les projets de photos disponibles
    """
    def get(self, request, *args, **kwargs):
        projects_dir = os.path.join(settings.MEDIA_ROOT, 'photos')
        
        if not os.path.exists(projects_dir):
            return Response({'projects': []}, status=status.HTTP_200_OK)
        
        projects = []
        for project_name in os.listdir(projects_dir):
            project_path = os.path.join(projects_dir, project_name)
            
            if os.path.isdir(project_path):
                # Vérifier s'il y a un fichier metadata.json
                metadata_path = os.path.join(project_path, 'metadata.json')
                project_info = {
                    'name': project_name,
                    'path': os.path.relpath(project_path, settings.MEDIA_ROOT),
                    'reference_count': 0,
                    'photo_count': 0
                }
                
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            project_info['reference_count'] = len(metadata.get('references', {}))
                            project_info['photo_count'] = sum(
                                len(ref_data.get('photos', [])) 
                                for ref_data in metadata.get('references', {}).values()
                            )
                    except Exception as e:
                        logger.error(f"Erreur lors de la lecture du fichier metadata.json pour {project_name}: {str(e)}")
                else:
                    # Compter manuellement s'il n'y a pas de metadata.json
                    reference_count = 0
                    photo_count = 0
                    
                    for item in os.listdir(project_path):
                        item_path = os.path.join(project_path, item)
                        if os.path.isdir(item_path):
                            reference_count += 1
                            for file in os.listdir(item_path):
                                if os.path.splitext(file)[1].lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                                    photo_count += 1
                    
                    project_info['reference_count'] = reference_count
                    project_info['photo_count'] = photo_count
                
                projects.append(project_info)
        
        return Response({'projects': projects}, status=status.HTTP_200_OK)


class PhotoProjectDetailView(APIView):
    """
    Vue pour obtenir les détails d'un projet spécifique
    """
    def get(self, request, project_name, *args, **kwargs):
        project_dir = os.path.join(settings.MEDIA_ROOT, 'photos', project_name)
        
        if not os.path.exists(project_dir) or not os.path.isdir(project_dir):
            return Response({'error': 'Projet non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifier s'il y a un fichier metadata.json
        metadata_path = os.path.join(project_dir, 'metadata.json')
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                    return Response(project_data, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Erreur lors de la lecture du fichier metadata.json pour {project_name}: {str(e)}")
        
        # Si pas de metadata.json ou erreur, construire les données manuellement
        project_data = {
            'project_name': project_name,
            'references': {}
        }
        
        for reference in os.listdir(project_dir):
            reference_path = os.path.join(project_dir, reference)
            
            if os.path.isdir(reference_path):
                photos = []
                has_logo = False
                logo_path = None
                
                for file_name in os.listdir(reference_path):
                    file_path = os.path.join(reference_path, file_name)
                    file_ext = os.path.splitext(file_name)[1].lower()
                    
                    if file_name.lower() in ['logo.png', 'logo.jpg', 'logo.jpeg']:
                        has_logo = True
                        logo_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
                        continue
                    
                    if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                        metadata = self._extract_metadata_from_filename(file_name)
                        photos.append({
                            'name': file_name,
                            'path': os.path.relpath(file_path, settings.MEDIA_ROOT),
                            'metadata': metadata
                        })
                
                project_data['references'][reference] = {
                    'photos': photos,
                    'has_logo': has_logo
                }
                
                if has_logo and logo_path:
                    project_data['references'][reference]['logo_path'] = logo_path
        
        return Response(project_data, status=status.HTTP_200_OK)
    
    def _extract_metadata_from_filename(self, filename):
        """
        Extrait les métadonnées (nom, prénom, référence) à partir du nom de fichier.
        Format attendu: Nom_Prenom_Reference.ext
        """
        base_name = os.path.splitext(filename)[0]
        parts = base_name.split('_')
        
        metadata = {
            'last_name': parts[0] if len(parts) > 0 else '',
            'first_name': parts[1] if len(parts) > 1 else '',
            'reference': parts[2] if len(parts) > 2 else ''
        }
        
        return metadata