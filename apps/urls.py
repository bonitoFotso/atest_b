from django.urls import path, include

urlpatterns = [
    path('', include('apps.geography.urls')),
    path('', include('apps.clients.urls')),
    path('', include('apps.inspections.urls')),
    path('', include('apps.certifications.urls')),
    path('', include('apps.documents.urls')),
    path('', include('apps.habilitations.urls')),
    path('', include('apps.formations.urls')),

]