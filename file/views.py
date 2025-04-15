from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Client

# Liste des rapports (Read)
class ClientListView(ListView):
    model = Client
    template_name = 'rapports/client_list.html'
    context_object_name = 'rapports'

# Détail d'un client (Read)
class ClientDetailView(DetailView):
    model = Client
    template_name = 'rapports/client_detail.html'
    context_object_name = 'client'

# Créer un nouveau client (Create)
class ClientCreateView(CreateView):
    model = Client
    template_name = 'rapports/client_form.html'
    fields = ['name', 'email', 'phone', 'address']
    success_url = reverse_lazy('client-list')

# Mettre à jour un client (Update)
class ClientUpdateView(UpdateView):
    model = Client
    template_name = 'rapports/client_form.html'
    fields = ['name', 'email', 'phone', 'address']
    success_url = reverse_lazy('client-list')

# Supprimer un client (Delete)
class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'rapports/client_confirm_delete.html'
    success_url = reverse_lazy('client-list')


from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Site

# Liste des sites (Read)
class SiteListView(ListView):
    model = Site
    template_name = 'sites/site_list.html'
    context_object_name = 'sites'

# Détail d'un site (Read)
class SiteDetailView(DetailView):
    model = Site
    template_name = 'sites/site_detail.html'
    context_object_name = 'site'

# Créer un nouveau site (Create)
class SiteCreateView(CreateView):
    model = Site
    template_name = 'sites/site_form.html'
    fields = ['client', 'name', 'location']
    success_url = reverse_lazy('site-list')

# Mettre à jour un site (Update)
class SiteUpdateView(UpdateView):
    model = Site
    template_name = 'sites/site_form.html'
    fields = ['client', 'name', 'location']
    success_url = reverse_lazy('site-list')

# Supprimer un site (Delete)
class SiteDeleteView(DeleteView):
    model = Site
    template_name = 'sites/site_confirm_delete.html'
    success_url = reverse_lazy('site-list')


from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Document

# Liste des documents (Read)
class DocumentListView(ListView):
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'

# Détail d'un document (Read)
class DocumentDetailView(DetailView):
    model = Document
    template_name = 'documents/document_detail.html'
    context_object_name = 'document'

# Créer un nouveau document (Create)
class DocumentCreateView(CreateView):
    model = Document
    template_name = 'documents/document_form.html'
    fields = ['site', 'file', 'title', 'description']
    success_url = reverse_lazy('document-list')

# Mettre à jour un document (Update)
class DocumentUpdateView(UpdateView):
    model = Document
    template_name = 'documents/document_form.html'
    fields = ['site', 'file', 'title', 'description']
    success_url = reverse_lazy('document-list')

# Supprimer un document (Delete)
class DocumentDeleteView(DeleteView):
    model = Document
    template_name = 'documents/document_confirm_delete.html'
    success_url = reverse_lazy('document-list')
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Certificate

# Liste des certificats (Read)
class CertificateListView(ListView):
    model = Certificate
    template_name = 'certificates/certificate_list.html'
    context_object_name = 'certificates'

# Détail d'un certificat (Read)
class CertificateDetailView(DetailView):
    model = Certificate
    template_name = 'certificates/certificate_detail.html'
    context_object_name = 'certificate'

# Créer un nouveau certificat (Create)
class CertificateCreateView(CreateView):
    model = Certificate
    template_name = 'certificates/certificate_form.html'
    fields = ['client', 'file', 'title', 'issued_date', 'expiry_date']
    success_url = reverse_lazy('certificate-list')

# Mettre à jour un certificat (Update)
class CertificateUpdateView(UpdateView):
    model = Certificate
    template_name = 'certificates/certificate_form.html'
    fields = ['client', 'file', 'title', 'issued_date', 'expiry_date']
    success_url = reverse_lazy('certificate-list')

# Supprimer un certificat (Delete)
class CertificateDeleteView(DeleteView):
    model = Certificate
    template_name = 'certificates/certificate_confirm_delete.html'
    success_url = reverse_lazy('certificate-list')
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Report

# Liste des rapports (Read)
class ReportListView(ListView):
    model = Report
    template_name = 'reports/report_list.html'
    context_object_name = 'reports'

# Détail d'un rapport (Read)
class ReportDetailView(DetailView):
    model = Report
    template_name = 'reports/report_detail.html'
    context_object_name = 'report'

# Créer un nouveau rapport (Create)
class ReportCreateView(CreateView):
    model = Report
    template_name = 'reports/report_form.html'
    fields = ['site', 'file', 'title', 'description']
    success_url = reverse_lazy('report-list')

# Mettre à jour un rapport (Update)
class ReportUpdateView(UpdateView):
    model = Report
    template_name = 'reports/report_form.html'
    fields = ['site', 'file', 'title', 'description']
    success_url = reverse_lazy('report-list')

# Supprimer un rapport (Delete)
class ReportDeleteView(DeleteView):
    model = Report
    template_name = 'reports/report_confirm_delete.html'
    success_url = reverse_lazy('report-list')

