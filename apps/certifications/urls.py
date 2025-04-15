# apps/certifications/urls.py
from apps.certifications.views.GenerateCertificateView import GenerateCertificateView
from apps.certifications.views.HabilitationGenerateView import HabilitationGenerateView
from apps.certifications.views.views import (
    CertificaTypeViewSet, SessionViewSet, CertificatViewSet, ImageUploadView,
 ParticipantViewSet
)
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'participants', ParticipantViewSet)



router.register(r'certificat-types', CertificaTypeViewSet)
router.register(r'sessions', SessionViewSet)
router.register(r'certificats', CertificatViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('generate-habilitation/', HabilitationGenerateView.as_view(), name='generate_habilitation'),
    path('upload/', ImageUploadView.as_view(), name='image-upload'),
    path('certificat/', GenerateCertificateView.as_view(), name='generate_certificate'),

]
