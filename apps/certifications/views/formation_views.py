from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
import xlsxwriter
from io import BytesIO
from datetime import datetime

from ..models import Formation, H_Electrique, H_Traveaux_Hauteur
from ..serializers import FormationSerializer, H_ElectriqueSerializer, H_Traveaux_HauteurSerializer, ParticipantSerializer, ParticipantSerializerDetail

class FormationViewSet(viewsets.ModelViewSet):
    queryset = Formation.objects.all()
    serializer_class = FormationSerializer


    @action(detail=True, methods=['get'])
    def export_participants_excel(self, request, pk=None):
        try:
            formation = self.get_object()
            
            # Créer un buffer en mémoire
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet()

            # Définir les styles
            header_style = workbook.add_format({
                'bold': True,
                'bg_color': '#4F81BD',
                'color': 'white',
                'align': 'center',
            })

            # Écrire les en-têtes
            headers = ['Nom', 'Prénom', 'Fonction', 'Entreprise']
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_style)

            # Écrire les données des participants
            for row, participant in enumerate(formation.participants.all(), start=1):
                worksheet.write(row, 0, participant.nom)
                worksheet.write(row, 1, participant.prenom)
                worksheet.write(row, 2, participant.fonction)
                worksheet.write(row, 3, participant.client.raison_sociale)

            # Ajuster la largeur des colonnes
            worksheet.set_column(0, 3, 20)

            workbook.close()
            
            # Préparer la réponse HTTP
            output.seek(0)
            filename = f"participants_formation_{formation.nom}_{datetime.now().strftime('%Y%m%d')}.xlsx"
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def export_participants_electrique_excel(self, request, pk=None):
        try:
            formation = self.get_object()
            
            # Vérifier si c'est une formation électrique
            if formation.type_formation != 'ELEC':
                return Response(
                    {'error': 'Cette fonction est uniquement pour les formations électriques'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet()

            # Style pour les en-têtes
            header_style = workbook.add_format({
                'bold': True,
                'bg_color': '#4F81BD',
                'color': 'white',
                'align': 'center',
                'text_wrap': True,
                'valign': 'vcenter'
            })

            # Définir les en-têtes
            headers = [
                'Nom', 'Prénom', 'Fonction', 'Client', 'BP', 'Lieu Formations',
                'Durée de Formation', 'Date', 'Date début', 'Date fin',
                'Numéro de Titre', 'Titre', 'Lieu', 'Fonction 2',
                'Nom Employeur', 'Fonction Employeur', 'Prénom Employeur',
                'Date Employeur', 'Validité', 'Référence',
                'Installations Concernées', 'Indications',
                'B0', 'H0', 'H0V', 'B1', 'B1V', 'B2', 'B2V', 'B2V Essais',
                'BC', 'BR', 'H1', 'H1V', 'H2', 'H2V', 'H2V Essais', 'HC'
            ]

            # Écrire les en-têtes
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_style)

            # Écrire les données des participants
            row = 1
            for participant in formation.participants.all():
                try:
                    habilitation = H_Electrique.objects.get(
                        participant=participant,
                        formation=formation
                    )
                    
                    # Données de base
                    worksheet.write(row, 0, participant.nom)
                    worksheet.write(row, 1, participant.prenom)
                    worksheet.write(row, 2, participant.fonction)
                    worksheet.write(row, 3, participant.client.raison_sociale)
                    worksheet.write(row, 4, '')  # BP (à ajouter au modèle si nécessaire)
                    worksheet.write(row, 5, formation.lieu)
                    worksheet.write(row, 6, formation.duree)
                    worksheet.write(row, 7, formation.date_debut.strftime('%d/%m/%Y'))
                    worksheet.write(row, 8, formation.date_debut.strftime('%d/%m/%Y'))
                    worksheet.write(row, 9, formation.date_fin.strftime('%d/%m/%Y'))
                    
                    # Données d'habilitation
                    worksheet.write(row, 10, habilitation.numero_titre)
                    worksheet.write(row, 11, formation.nom)
                    worksheet.write(row, 12, formation.lieu)
                    worksheet.write(row, 13, participant.fonction)
                    
                    # Données employeur
                    worksheet.write(row, 14, participant.client.nom_employeur)
                    worksheet.write(row, 15, participant.client.fonction_employeur)
                    worksheet.write(row, 16, participant.client.prenom_employeur)
                    worksheet.write(row, 17, formation.date_debut.strftime('%d/%m/%Y'))
                    worksheet.write(row, 18, formation.validite.strftime('%d/%m/%Y'))
                    worksheet.write(row, 19, participant.client.reference_employeur)
                    
                    # Données spécifiques électriques
                    worksheet.write(row, 20, habilitation.installation)
                    worksheet.write(row, 21, habilitation.indication)
                    
                    # Habilitations électriques
                    col = 22
                    for hab in ['B0', 'H0', 'H0V', 'B1', 'B1V', 'B2', 'B2V', 
                               'B2V_Essais', 'BC', 'BR', 'H1', 'H1V', 'H2', 
                               'H2V', 'H2V_Essais', 'HC']:
                        worksheet.write(row, col, 'X' if getattr(habilitation, hab) else '')
                        col += 1
                    
                    row += 1
                    
                except H_Electrique.DoesNotExist:
                    continue

            # Ajuster la largeur des colonnes
            worksheet.set_column(0, len(headers)-1, 15)

            workbook.close()
            
            # Préparer la réponse HTTP
            output.seek(0)
            filename = f"participants_habilitation_electrique_{formation.nom}_{datetime.now().strftime('%Y%m%d')}.xlsx"
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def export_participants_hauteur_excel(self, request, pk=None):
        try:
            formation = self.get_object()
            
            # Vérifier si c'est une formation travaux en hauteur
            if formation.type_formation != 'HAUT':
                return Response(
                    {'error': 'Cette fonction est uniquement pour les formations travaux en hauteur'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet()

            # Style pour les en-têtes
            header_style = workbook.add_format({
                'bold': True,
                'bg_color': '#4F81BD',
                'color': 'white',
                'align': 'center',
                'text_wrap': True,
                'valign': 'vcenter'
            })

            # Définir les en-têtes
            headers = [
                'Nom', 'Prénom', 'Titulaire', 'Employeur', 'Client', 'Fonction',
                'Poste d\'affectation', 'BP', 'Tel', 'Date de la formation',
                'Fin de la formation', 'Date d\'expiration', 'Date de délivrance',
                'Classe 1', 'Classe 2', 'Classe 3', 'Classe 4', 'Classe 5', 'Classe 6',
                'Nacelles élévatrices automotrices', 'Nacelles élévatrices sur porteur',
                'Plates-formes sur mât', 'Plates-formes suspendues',
                'Nacelles de nettoyage de façade', 'Nacelles articulées tractables',
                'Nacelles pour travaux sur réseaux', 'Nacelles araignées',
                'Plates-formes de travail sur mât',
                'Plates-formes suspendues à niveau variable',
                'Ascenseurs et plates-formes de transport',
                'Ligne de vie (Toitures, Charpentes, Terrasses)',
                'Échelles, escabeaux et marchepieds'
            ]

            # Écrire les en-têtes
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_style)

            # Écrire les données des participants
            row = 1
            for participant in formation.participants.all():
                try:
                    habilitation = H_Traveaux_Hauteur.objects.get(
                        participant=participant,
                        formation=formation
                    )
                    
                    # Données de base
                    worksheet.write(row, 0, participant.nom)
                    worksheet.write(row, 1, participant.prenom)
                    worksheet.write(row, 2, f"{participant.nom} {participant.prenom}")  # Titulaire
                    worksheet.write(row, 3, participant.client.raison_sociale)  # Employeur
                    worksheet.write(row, 4, participant.client.raison_sociale)  # Client
                    worksheet.write(row, 5, participant.fonction)
                    worksheet.write(row, 6, participant.fonction)  # Poste d'affectation
                    worksheet.write(row, 7, '')  # BP
                    worksheet.write(row, 8, participant.client.telephone)
                    worksheet.write(row, 9, formation.date_debut.strftime('%d/%m/%Y'))
                    worksheet.write(row, 10, formation.date_fin.strftime('%d/%m/%Y'))
                    worksheet.write(row, 11, formation.validite.strftime('%d/%m/%Y'))
                    worksheet.write(row, 12, habilitation.date_delivrance.strftime('%d/%m/%Y'))

                    # Classes
                    col = 13
                    for classe in ['Classe_1', 'Classe_2', 'Classe_3', 'Classe_4', 'Classe_5', 'Classe_6']:
                        worksheet.write(row, col, 'Apte' if getattr(habilitation, classe) else 'Sans objet')
                        col += 1

                    # Types de nacelles et équipements
                    equipements = [
                        'Nacelles_elevatrices_automotrices',
                        'Nacelles_elevatrices_sur_porteur',
                        'Plates_formes_sur_mat',
                        'Plates_formes_suspendues',
                        'Nacelles_de_nettoyage_de_faade',
                        'Nacelles_articulees_tractables',
                        'Nacelles_pour_travaux_sur_reseaux',
                        'Nacelles_araignees',
                        'Plates_formes_de_travail_sur_mat',
                        'Plates_formes_suspendues_a_niveau_variable',
                        'Ascenseurs_et_plates_formes_de_transport',
                        'Ligne_de_vie_Toitures_Charpentes_Terrasses',
                        'Echelles_escabeaux_et_marchepieds'
                    ]

                    for equipement in equipements:
                        worksheet.write(row, col, 'X' if getattr(habilitation, equipement) else '')
                        col += 1

                    row += 1
                    
                except H_Traveaux_Hauteur.DoesNotExist:
                    continue

            # Ajuster la largeur des colonnes
            worksheet.set_column(0, len(headers)-1, 15)

            workbook.close()
            
            # Préparer la réponse HTTP
            output.seek(0)
            filename = f"participants_habilitation_hauteur_{formation.nom}_{datetime.now().strftime('%Y%m%d')}.xlsx"
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )