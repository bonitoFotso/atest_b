"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from .views import index, file_metadata_view, CurrentDateTimeView
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name='index'),
    path('api/current-datetime/', CurrentDateTimeView.as_view(), name='current_datetime'),

                  # path("qrcode/", include('qrcode_api.urls')),
    path('metadata/', file_metadata_view, name='file_metadata'),

    # path('rapports/<uuid:uuid>/', get_file_by_uuid, name='get_file_by_uuid'),

    #    path('file/', include('file.urls')),
    path('auth/', include('auths.urls')),
    # path('api/', include('file_api.urls')),
    path('api/', include('apps.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)























































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































