from rest_framework.routers import DefaultRouter
from backend.urls import path
from backend.urls import include
from .views import AdviceViewSet
from .views import UserHistoryViewSet
from .views import CreatePaymentIntentView
from .views import CreateDetailedAdviceView

router = DefaultRouter()
router.register(r'advice', AdviceViewSet)
router.register(r'user-history', UserHistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('advice/<int:pk>/',
      AdviceViewSet.as_view({'get': 'retrieve'}), name='advice-detail'),
    path('create-payment-intent/',
      CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    path('create-detailed-advice/',
      CreateDetailedAdviceView.as_view(), name='create_detailed_advice'),
]