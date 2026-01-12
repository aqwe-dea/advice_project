from rest_framework.routers import DefaultRouter
from rest_framework import routers, viewsets
from backend.urls import path
from backend.urls import include
from django.conf import settings
from django.conf.urls.static import static
from .views import AdviceViewSet
from .views import UserHistoryViewSet
from .views import CreatePaymentIntentView
from .views import CreateDetailedAdviceView
from .views import ChatView
from .views import GenerateCourseView, BuildCourseBookView
from .views import LegalDocumentAnalysisView
from .views import FinancialAnalysisView
from .views import PhotoRestorationView
from .views import MedicalImageView
from .views import ThreeDToProjectView
from .views import HealthRecommendationView
from .views import BusinessPlanView
from .views import PresentationGenerationView
from .views import InvestmentAnalysisView
from .views import MarketingStrategyView
from .views import TravelPlannerView
from .views import CompetitorAnalysisView
from .views import CommunicationOptimizationView
from .views import CreateSessionView
from .views import CreateCheckoutSessionView
from .views import SessionStatusView
from .views import HandleStripeWebhookView

router = DefaultRouter()
router.register(r'advice', AdviceViewSet)
router.register(r'user-history', UserHistoryViewSet)

app_name = 'aqwe_app'

urlpatterns = [
    path('', include(router.urls)),
    path('advice/<int:pk>/', AdviceViewSet.as_view({'get': 'retrieve'}), name='advice-detail'),
    path('create-detailed-advice/', CreateDetailedAdviceView.as_view(), name='create-detailed-advice'),
    path('chat/', ChatView.as_view(), name='chat'),
    path('generate-course/', GenerateCourseView.as_view(), name='generate-course'),
    path('generate-course/build_course_book/', BuildCourseBookView.as_view(), name='build-course-book'),
    path('legal-document-analysis/', LegalDocumentAnalysisView.as_view(), name='legal-document-analysis'),
    path('financial-analysis/', FinancialAnalysisView.as_view(), name='finacial-analysis'),
    path('photo-restoration/', PhotoRestorationView.as_view(), name='photo-restoration'),
    path('medical-image-analysis/', MedicalImageView.as_view(), name='medical-image-analysis'),
    path('3d-to-project/', ThreeDToProjectView.as_view(), name='3d-to-project'),
    path('health-recommendation/', HealthRecommendationView.as_view(), name='health-recommendation'),
    path('business-plan/', BusinessPlanView.as_view(), name='business-plan'),
    path('generate-presentation/', PresentationGenerationView.as_view(), name='generate-presentation'),
    path('investment-analysis/', InvestmentAnalysisView.as_view(), name='investment-analysis'),
    path('marketing-strategy/', MarketingStrategyView.as_view(), name='marketing-strategy'),
    path('travel-planner/', TravelPlannerView.as_view(), name='travel-planner'),
    path('competitor-analysis/', CompetitorAnalysisView.as_view(), name='competitor-analysis'),
    path('communication-optimization/', CommunicationOptimizationView.as_view(), name='communication-optimization'),
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('create-session/', CreateSessionView.as_view(), name='create-session'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('session-status/', SessionStatusView.as_view(), name='session-status'),
    path('stripe-webhook/', HandleStripeWebhookView.as_view(), name='stripe-webhook'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)