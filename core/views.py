
from datetime import datetime
import os
import time
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import pytz



def index(request):
    date = datetime.today()

    return render(request, "index.html", {"date": date})

# def get_file_by_uuid(request, uuid):
#     file_link = get_object_or_404(FileLink, uuid=uuid)
#     return redirect(file_link.file_url)


class CurrentDateTimeView(APIView):
    permission_classes = []
    def get(self, request, *args, **kwargs):
        # Récupérer la date et l'heure actuelles
        current_time = datetime.now(pytz.timezone('Europe/Paris'))  # Par exemple, en heure de Paris
        # Formater la date et l'heure pour la réponse
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')

        # Retourner la réponse
        return Response({"current_datetime": formatted_time}, status=status.HTTP_200_OK)


def file_metadata_view(request):
    context = {}
    
    if request.method == "POST" and request.FILES.get('uploaded_file'):
        # Récupérer le fichier uploadé
        uploaded_file = request.FILES['uploaded_file']
        
        # Sauvegarder le fichier sur le serveur (dossier temporaire)
        file_path = f'/tmp/{uploaded_file.name}'
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # Récupérer les métadonnées du fichier
        file_info = os.stat(file_path)
        print(file_info)
        
        # Préparer les données pour le template
        context = {
            "file_name": os.path.basename(file_path),
            "file_size": file_info.st_size,
            "creation_time": time.ctime(file_info.st_ctime),
            "modification_time": time.ctime(file_info.st_mtime),
            "permissions": oct(file_info.st_mode),
        }

    return render(request, "file_metadata.html", context)
