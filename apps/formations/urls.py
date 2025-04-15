# urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.formations.views.views import ParticipantViewSet, FormationViewSet

router = DefaultRouter()
router.register(r'participantss', ParticipantViewSet)
router.register(r'formations', FormationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
