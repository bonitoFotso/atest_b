from django.urls import path
from .views import ClientListView, ClientDetailView, ClientCreateView, ClientUpdateView, ClientDeleteView
from django.urls import path
from .views import SiteListView, SiteDetailView, SiteCreateView, SiteUpdateView, SiteDeleteView
from django.urls import path
from .views import DocumentListView, DocumentDetailView, DocumentCreateView, DocumentUpdateView, DocumentDeleteView
from django.urls import path
from .views import CertificateListView, CertificateDetailView, CertificateCreateView, CertificateUpdateView, CertificateDeleteView
from django.urls import path
from .views import ReportListView, ReportDetailView, ReportCreateView, ReportUpdateView, ReportDeleteView


urlpatterns = [
    path('rapports/', ClientListView.as_view(), name='client-list'),
    path('rapports/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
    path('rapports/new/', ClientCreateView.as_view(), name='client-create'),
    path('rapports/<int:pk>/edit/', ClientUpdateView.as_view(), name='client-update'),
    path('rapports/<int:pk>/delete/', ClientDeleteView.as_view(), name='client-delete'),
    #site urls
    path('sites/', SiteListView.as_view(), name='site-list'),
    path('sites/<int:pk>/', SiteDetailView.as_view(), name='site-detail'),
    path('sites/new/', SiteCreateView.as_view(), name='site-create'),
    path('sites/<int:pk>/edit/', SiteUpdateView.as_view(), name='site-update'),
    path('sites/<int:pk>/delete/', SiteDeleteView.as_view(), name='site-delete'),
    path('documents/', DocumentListView.as_view(), name='document-list'),
    path('documents/<int:pk>/', DocumentDetailView.as_view(), name='document-detail'),
    path('documents/new/', DocumentCreateView.as_view(), name='document-create'),
    path('documents/<int:pk>/edit/', DocumentUpdateView.as_view(), name='document-update'),
    path('documents/<int:pk>/delete/', DocumentDeleteView.as_view(), name='document-delete'),
    path('certificates/', CertificateListView.as_view(), name='certificate-list'),
    path('certificates/<int:pk>/', CertificateDetailView.as_view(), name='certificate-detail'),
    path('certificates/new/', CertificateCreateView.as_view(), name='certificate-create'),
    path('certificates/<int:pk>/edit/', CertificateUpdateView.as_view(), name='certificate-update'),
    path('certificates/<int:pk>/delete/', CertificateDeleteView.as_view(), name='certificate-delete'),
    path('reports/', ReportListView.as_view(), name='report-list'),
    path('reports/<int:pk>/', ReportDetailView.as_view(), name='report-detail'),
    path('reports/new/', ReportCreateView.as_view(), name='report-create'),
    path('reports/<int:pk>/edit/', ReportUpdateView.as_view(), name='report-update'),
    path('reports/<int:pk>/delete/', ReportDeleteView.as_view(), name='report-delete'),

]











