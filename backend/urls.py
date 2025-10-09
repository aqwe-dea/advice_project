from django.contrib import admin
from django.urls import path
from django.urls import include
from aqwe_app.urls import path
from django.urls import re_path
from django.conf import settings
from aqwe_app import views
from django.views.generic import TemplateView
from django.conf.urls.static import static
from aqwe_app.views import CreatePaymentIntentView
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView
from djstripe.urls import path
from aqwe_app.views import ChatView
from aqwe_app.views import GenerateCourseView
from aqwe_app.views import LegalDocumentAnalysisView
from aqwe_app.views import FinancialAnalysisView
from aqwe_app.views import PhotoRestorationView
from aqwe_app.views import MedicalImageView
from aqwe_app.views import ThreeDToProjectView
from aqwe_app.views import HealthRecommendationView
from aqwe_app.views import BusinessPlanView
from aqwe_app.views import PresentationGenerationView
from aqwe_app.views import InvestmentAnalysisView
from aqwe_app.views import MarketingStrategyView
from aqwe_app.views import TravelPlannerView
from aqwe_app.views import CompetitorAnalysisView
from aqwe_app.views import CommunicationOptimizationView
from aqwe_app.views import CreateSessionView
from aqwe_app.views import CreateCheckoutSessionView
from aqwe_app.views import SessionStatusView
from aqwe_app.views import HandleStripeWebhookView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.openapi import Swagger
from drf_yasg.openapi import Schema
from drf_yasg.generators import OpenAPISchemaGenerator

schema_view = get_schema_view(
    openapi.Info(
        title="Советница АКВИ API",
        default_version='v1',
        description="Документация проекта Советница Акви"
    ),
    public=True
)

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('aqwe_app.urls')),
    path('chat/', ChatView.as_view(), name='chat'),
    path('generate-course/', GenerateCourseView.as_view(), name='generate-course'),
    path('legal-document-analysis/', LegalDocumentAnalysisView.as_view(), name='legal-document-analysis'),
    path('financial-analysis/', FinancialAnalysisView.as_view(), name='finacial-analysis'),
    path('photo-restoration/', PhotoRestorationView.as_view(), name='photo-restoration'),
    path('medical-image-analysis/', MedicalImageView.as_view(), name='medical-image-analysis'),
    path('3d-to-project/', ThreeDToProjectView.as_view(), name='3d-to-project'),
    path('health-recommendation/', HealthRecommendationView.as_view(), name='health-recommendation'),
    path('business-plan/', BusinessPlanView.as_view(), name='business-plan'),
    path('business-plan/industry-templates/', BusinessPlanView.as_view(), name='industry-templates'),
    path('business-plan/pitch-deck/', BusinessPlanView.as_view(), name='pitch-deck'),
    path('generate-presentation/', PresentationGenerationView.as_view(), name='generate-presentation'),
    path('investment-analysis/', InvestmentAnalysisView.as_view(), name='investment-analysis'),
    path('marketing-strategy/', MarketingStrategyView.as_view(), name='marketing-strategy'),
    path('travel-planner/', TravelPlannerView.as_view(), name='travel-planner'),
    path('competitor-analysis/', CompetitorAnalysisView.as_view(), name='competitor-analysis'),
    path('communication-optimization/', CommunicationOptimizationView.as_view(), name='communication-optimization'),
    path('stripe/', include('djstripe.urls', namespace='djstripe')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('create-session/', CreateSessionView.as_view(), name='create-session'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('session-status/', SessionStatusView.as_view(), name='session-status'),
    path('stripe-webhook/', HandleStripeWebhookView.as_view(), name='stripe-webhook'),
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    re_path(r'^(?:.*)/?$', TemplateView.as_view(template_name='index.html')),
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