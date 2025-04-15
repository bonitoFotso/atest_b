from django.urls import path
from .views import GenerateArcFlashLabelsView, ArcFlashLabelListCreateView

urlpatterns = [
    # Autres URL ici...
    path('arcflash/', GenerateArcFlashLabelsView.as_view(), name='generate_arcflash_labels'),
    path('arcflash/list/', ArcFlashLabelListCreateView.as_view(), name='arcflash-list-create'),

]
