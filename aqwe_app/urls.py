from rest_framework.routers import DefaultRouter
from aqwe_app.views import AdviceViewSet
from aqwe_app.views import UserHistoryViewSet
from aqwe_app.views import CreatePaymentIntentView
from backend.urls import path
from backend.urls import include
from django.urls import path
from django.urls import include

router = DefaultRouter()
router.register(r'advice', AdviceViewSet)
router.register(r'user-history', UserHistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('advice/<int:pk>/', AdviceViewSet.as_view({'get': 'retrieve'}), name='advice-detail'),
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create_payment_intent'),
]