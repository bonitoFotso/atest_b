# apps/geography/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.geography.views import RegionViewSet, CityViewSet, SiteViewSet

router = DefaultRouter()
router.register(r'regions', RegionViewSet)
router.register(r'cities', CityViewSet)
router.register(r'sites', SiteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
