# apps/certifications/urls.py


from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.habilitations.views.HabilitationGenerateView import HabilitationGenerateView
#from apps.certifications.views.HabilitationGenerateView import HabilitationGenerateView
from apps.habilitations.views.PhotoZipUploadView import PhotoZipUploadView
from apps.habilitations.views.generate_traveaux_hauteur_avis import GenerateHabilitationTitlesTHView
from apps.habilitations.views.views import EmployeurViewSet, ResponsableViewSet, ParticipantViewSet, \
    HabilitationViewSet, InscriptionViewSet, ImageUploadView

router = DefaultRouter()
router.register(r'employeurs', EmployeurViewSet)
router.register(r'responsables', ResponsableViewSet)
router.register(r'participants', ParticipantViewSet)
router.register(r'habilitations', HabilitationViewSet)
router.register(r'inscriptions', InscriptionViewSet)


urlpatterns = [
    #path('', include(router.urls)),
    path('generate-habilitation/', HabilitationGenerateView.as_view(), name='generate_habilitation'),
    path('h/upload/', ImageUploadView.as_view(), name='image-upload'),
    path('traveaux_hauteur/', GenerateHabilitationTitlesTHView.as_view(), name='add-text-to-image'),
    path('upload-photos-zip/', PhotoZipUploadView.as_view(), name='upload-photos-zip'),


]
