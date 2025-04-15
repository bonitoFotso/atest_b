from django.urls import path, include

from file_api.lots.views import LotEtiquetteCreateView, DownloadLotEtiquettesView

urlpatterns = [
    path('', include('file_api.fichiers.urls')),
    path('', include('file_api.rapports.urls')),

    path('', include('file_api.lots.urls')),

    path('', include('file_api.certificats.urls')),

    path('', include('file_api.arc_flash.urls')),


]


