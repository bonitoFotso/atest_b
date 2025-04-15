from django.urls import path

from file_api.fichiers.views import QRCodeListCreateAPIView, \
    QRCodeRetrieveUpdateDestroyAPIView, \
    EtiquetteListCreateAPIView, \
    EtiquetteRetrieveUpdateDestroyAPIView, BulkCreateEtiquetteAPIView, LotEtiquetteListView, DossierListCreateView, \
    DossierRetrieveUpdateDestroyView, FichierListCreateView, FichierRetrieveUpdateDestroyView, download_qr_image, \
    GenerateQRCodeView, DownloadQRCodeView

urlpatterns = [



    # QRCode URLs
    path('qrcodes/', QRCodeListCreateAPIView.as_view(), name='qrcode-list-create'),
    path('qrcodes/<int:pk>/', QRCodeRetrieveUpdateDestroyAPIView.as_view(), name='qrcode-detail'),
    path('qrcodes/generate/', GenerateQRCodeView.as_view(), name='generate_qrcode'),
    path('qrcodes/<int:pk>/download/', DownloadQRCodeView.as_view(), name='download_qrcode'),

    # Folder URLs
    path('dossiers/', DossierListCreateView.as_view(), name='dossier-list-create'),
    path('dossiers/<int:pk>/', DossierRetrieveUpdateDestroyView.as_view(), name='dossier-retrieve-update-destroy'),
    path('fichiers/', FichierListCreateView.as_view(), name='fichier-list-create'),
    path('fichiers/<int:pk>/', FichierRetrieveUpdateDestroyView.as_view(), name='fichier-retrieve-update-destroy'),

    # Etiquette URLs


    path('lots/<int:lot_id>/etiquettes/', LotEtiquetteListView.as_view(), name='lot-etiquette-list'),

    path('etiquettes/bulk-create/', BulkCreateEtiquetteAPIView.as_view(), name='etiquette-bulk-create'),

    path('qrcodes/<int:qr_code_id>/download/', download_qr_image, name='download_qr_image'),

]
