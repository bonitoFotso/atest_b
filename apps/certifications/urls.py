# apps/certifications/urls.py
from apps.certifications.views.GenerateCertificateView import GenerateCertificateView
from apps.certifications.views.views import ( ImageUploadView,
)
from django.urls import path, include
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('upload/', ImageUploadView.as_view(), name='image-upload'),
    path('certificat/', GenerateCertificateView.as_view(), name='generate_certificate'),

]
