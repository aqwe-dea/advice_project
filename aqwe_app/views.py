from rest_framework import viewsets
from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from aqwe_app.models import Advice
from aqwe_app.serializers import AdviceSerializer
from aqwe_app.models import UserHistory
from aqwe_app.serializers import UserHistorySerializer    
from djstripe.models.core import PaymentIntent
from djstripe.models import core        
from django.http.response import HttpResponse
from django.http import response


class AdviceViewSet(viewsets.ModelViewSet):
    queryset = Advice.objects.all()
    serializer_class = AdviceSerializer    

    def create(self, request, *args, **kwargs):
        category = request.data.get('category')
        question = request.data.get('question')
        if not category or not question:
            return Response(
                {'error': 'Необходимо указать категорию и вопрос'},
                status=status.HTTP_400_BAD_REQUEST
            )

        answers = {
            'финансы': 'Рекомендую создать бюджет и отслеживать расходы.',
            'здоровье': 'Попробуйте больше двигаться и соблюдать режим сна.',
            'образование': 'Определите свои цели и выберете подходящие курсы.',
            'default': 'Для этого случая у меня есть универсальный совет: Будьте терпеливы!'
        }

        answer = answers.get(category.lower(), answers['default'])

        try:
            advice = Advice.objects.create(
                category=category,
                question=question,
                answer=answer
            )
            serializer = self.get_serializer(advice)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e: 
            return Response(
                {'error': f'Произошла ошибка: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)  
      
        advice = Advice.objects.create(category=category, question=question, answer=answer)
        serializer = self.get_serializer(advice)

class UserHistoryViewSet(viewsets.ModelViewSet):
    queryset = UserHistory.objects.all()
    serializer_class = UserHistorySerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            return UserHistory.objects.filter(user_id=user_id)
        return UserHistory.objects.all()
        
class CreatePaymentIntentView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            payment_intent = PaymentIntent.create(
                amount=1000,
                currency='usd',
            )
            return Response({'clientSecret': payment_intent.client_secret})
        except Exception as e:
            return Response({'error': str(e)}, status=403)


# Create your views here.
