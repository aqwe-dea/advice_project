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
from djstripe.models import PaymentIntent        
from django.http.response import HttpResponse
from django.http import response
from aqwe_app.utils import send_advice_email

class CreateDetailedAdviceView(APIView):
     def post(self, request, *args, **kwargs):
         serializer = AdviceSerializer(data=request.data)
         if not serializer.is_valid():
             return Response(serializer.errors, status=400)
         advice = serializer.save()
         email = request.data.get('email')
         if email:
             self.send_advice_to_email(email, advice)
         return Response({'id': advice.id}, status=201)
     @staticmethod
     def send_advice_to_email(email: str, advice: Advice):
         subject = 'Ваш детальный совет от АКВИ'
         message = f'Категория: {advice.category}\n\nВопрос: {advice.question}\n\nОтвет: {advice.answer}'
         send_advice_email(email, message)
         
class AdviceViewSet(viewsets.ModelViewSet):
     queryset = Advice.objects.all()
     serializer_class = AdviceSerializer    

    def create(self, request, *args, **kwargs):
         response = super().create(request, *args, **kwargs)
         category = request.data.get('category')
         question = request.data.get('question')
         user_email = request.data.get('email')
         advice = response.data.get('answer')
        if user_email and advice:
             send_advice_email(user_email, advice)
             return response
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
                amount=request.data.get('amount'),
                currency=request.data.get('currency', 'usd'),
            )
            return Response({'clientSecret': payment_intent.client_secret})
        except Exception as e:
            return Response({'error': str(e)}, status=403)


# Create your views here.
