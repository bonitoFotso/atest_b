from django.urls import path

from .views import SessionListCreateView, SessionRetrieveUpdateDestroyView, ParticipantListCreateView, \
    ParticipantRetrieveUpdateDestroyView, CertificatListCreateView, CertificatRetrieveUpdateDestroyView, CertificatList

urlpatterns = [
    path('sessions/', SessionListCreateView.as_view(), name='session-list-create'),
    path('sessions/<int:pk>/', SessionRetrieveUpdateDestroyView.as_view(), name='session-retrieve-update-destroy'),
    path('participants/', ParticipantListCreateView.as_view(), name='participant-list-create'),
    path('participants/<int:pk>/', ParticipantRetrieveUpdateDestroyView.as_view(),
         name='participant-retrieve-update-destroy'),
    path('certificats/', CertificatListCreateView.as_view(), name='certificat-list-create'),
    path('certificats/<int:pk>/', CertificatRetrieveUpdateDestroyView.as_view(),
         name='certificat-retrieve-update-destroy'),

    path('certificats/list/', CertificatList.as_view(), name='certificat-list'),

]