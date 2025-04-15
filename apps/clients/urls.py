from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, AffaireViewSet, StatutViewSet

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'affaires', AffaireViewSet)
router.register(r'statuts', StatutViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
