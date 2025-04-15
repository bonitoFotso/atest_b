# apps/inspections/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.inspections.views.GenerateArcFlashLabelsView import GenerateArcFlashLabelsView
from apps.inspections.views.GenerateEtiquettesView import GenerateEtiquettesView
from apps.inspections.views.LotViews import EtiquetteLotView
from apps.inspections.views.views import (
    InspectionTypeViewSet, LotEtiquetteViewSet, EtiquetteViewSet,
    RapportViewSet, ArcFlashLabelViewSet
)

router = DefaultRouter()
router.register(r'inspection-types', InspectionTypeViewSet)
router.register(r'lot-etiquettes', LotEtiquetteViewSet)
router.register(r'etiquettes', EtiquetteViewSet)
router.register(r'rapports', RapportViewSet)
router.register(r'arcflash-labels', ArcFlashLabelViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('etiquette/generate/', GenerateEtiquettesView.as_view(), name='generate-etiquettes'),
    path('arcflash/', GenerateArcFlashLabelsView.as_view(), name='generate_arcflash_labels'),
    path('lots/', EtiquetteLotView.as_view(), name = "lot d'etiquettes")

]
