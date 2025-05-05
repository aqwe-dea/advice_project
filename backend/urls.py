from django.contrib import admin
from django.urls import path
from aqwe_app.urls import include
from djstripe.urls import path
from django.urls import include
from aqwe_app.urls import path
from django.urls import re_path
from django.conf import settings
from aqwe_app import views
from django.views.generic import TemplateView
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView
from aqwe_app.views import ChatView

urlpatterns = [
    path('admin/',
          admin.site.urls),
    path('api/',
          include('aqwe_app.urls')),
    path('stripe/',
          include('djstripe.urls', namespace='djstripe')),        
]

urlpatterns = [
    path('',
          TemplateView.as_view(template_name='index.html'), name='home'),
    re_path(r'^(?:.*)/?$',
            TemplateView.as_view(template_name='index.html')),
    path('api/schema/',
         SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/',
         SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('chat/',
         ChatView.as_view(), name='chat'),
]
"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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