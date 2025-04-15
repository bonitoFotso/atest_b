from django.urls import path
from .views import (
    ClientListCreateAPIView, ClientRetrieveUpdateDestroyAPIView,
    ClientSiteListCreateAPIView, SiteRetrieveUpdateDestroyAPIView,
    InspectionTypeListCreateAPIView, InspectionTypeRetrieveUpdateDestroyAPIView,
    SiteListCreateAPIView, RapportListCreateView, RapportDetailView, RapportCreateView
)

urlpatterns = [

    # Client URLs
    path('clients/', ClientListCreateAPIView.as_view(), name='client-list-create'),
    path('clients/<int:pk>/', ClientRetrieveUpdateDestroyAPIView.as_view(), name='client-detail'),

    # Site URLs under Client
    path('clients/<int:client_id>/sites/', ClientSiteListCreateAPIView.as_view(), name='client-site-list-create'),
    path('sites/', SiteListCreateAPIView.as_view(), name='site-list-create'),
    path('sites/<int:pk>/', SiteRetrieveUpdateDestroyAPIView.as_view(), name='site-detail'),

    # InspectionType URLs
    path('inspectiontypes/', InspectionTypeListCreateAPIView.as_view(), name='inspectiontype-list-create'),
    path('inspectiontypes/<int:pk>/', InspectionTypeRetrieveUpdateDestroyAPIView.as_view(), name='inspectiontype-detail'),


    # InspectionType URLs
    path('inspectiontypes/', InspectionTypeListCreateAPIView.as_view(), name='inspectiontype-list-create'),
    path('inspectiontypes/<int:pk>/', InspectionTypeRetrieveUpdateDestroyAPIView.as_view(),
         name='inspectiontype-detail'),



    # Rapport URLs
    path('rapports/', RapportListCreateView.as_view(), name='rapport-list-create'),
    path('rapports/<int:pk>/', RapportDetailView.as_view(), name='rapport-detail'),
    path('case/rapports/', RapportCreateView.as_view(), name='rapport-create'),

]
