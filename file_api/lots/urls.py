from django.urls import path

from .views import LotEtiquetteCreateView, DownloadLotEtiquettesView, \
    EtiquetteListCreateView, EtiquetteDetailView, GenerateEtiquettesView

urlpatterns = [

    path('lots/create/', LotEtiquetteCreateView.as_view(), name='lot-etiquette-create'),
    path('lots/<int:lot_id>/', DownloadLotEtiquettesView.as_view(), name='download_lot'),

path('etiquettes/', EtiquetteListCreateView.as_view(), name='etiquette-list-create'),
    path('etiquettes/<int:pk>/', EtiquetteDetailView.as_view(), name='etiquette-detail'),
    # path('etiquettes/generate/', GenerateEtiquettesView.as_view(), name='generate-etiquettes'),

]
