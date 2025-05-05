from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from django.conf import settings
import stripe
from .models import Advice, UserHistory
from .serializers import AdviceSerializer, UserHistorySerializer
from .utils import send_advice_email
import requests
import os
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

@api_view(['POST'])
@csrf_exempt

#stripe.api_key = settings.STRIPE_SECRET_KEY

#from rest_framework.viewsets import ViewSet
#from djstripe.models.core import PaymentIntent
#from djstripe.models import core
#from djstripe.models import PaymentIntent        
#from django.http.response import HttpResponse
#from django.http import response

class AdviceViewSet(viewsets.ModelViewSet):
    queryset = Advice.objects.all()
    serializer_class = AdviceSerializer
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        category = request.data.get('category')
        question = request.data.get('question')
        user_email = request.data.get('email')
        advice = response.data.get('answer')
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        advice = Advice.objects.create(category=category, question=question, answer=answer)
        try:
            advice = Advice.objects.create(
                category=category,
                question=question,
                answer=answer
            )
            serializer = self.get_serializer(advice)
        except Exception as e:
             return Response(
                {'error': f'Произошла ошибка: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
             )
        """
        if user_email and advice:
            send_advice_email(user_email, advice)
        return response
        if not category or not question:
             return Response(
                {'error': 'Необходимо указать категорию и вопрос'},
                status=status.HTTP_400_BAD_REQUEST
             )
        answer = answers.get(category.lower(), answers['default'])     
        answers = {
            'финансы': 'Рекомендую создать бюджет и отслеживать расходы.',
            'здоровье': 'Попробуйте больше двигаться и соблюдать режим сна.',
            'образование': 'Определите свои цели и выберете подходящие курсы.',
            'default': 'Для этого случая у меня есть универсальный совет: Будьте терпеливы!'
            }
        """    
class UserHistoryViewSet(viewsets.ModelViewSet):
    queryset = UserHistory.objects.all()
    serializer_class = UserHistorySerializer
    def get_queryset(self):
        email = self.request.query_params.get('email', None)
        if email:
             return UserHistory.objects.filter(email=email)
        return super().get_queryset()
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
             return UserHistory.objects.filter(user_id=user_id)
             return UserHistory.objects.all()
class CreateDetailedAdviceView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AdviceSerializer(data=request.data)
        if not serializer.is_valid():
             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        advice = serializer.save()
        email = request.data.get('email')
        if email:
             self.send_advice_to_email(email, advice)
        return Response({'id': advice.id}, status=status.HTTP_201_CREATED)
    @staticmethod
    def send_advice_to_email(email: str, advice: Advice):
        subject = 'Ваш детальный совет от АКВИ'
        message = (
            f'Категория: {advice.category}\n\n'
            f'Вопрос: {advice.question}\n\n'
            f'Ответ: {advice.answer}\n\n'
            f'Заметки: {advice.notes}'
        )
        send_advice_email(email, message)    
class CreatePaymentIntentView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            amount = int(request.data.get('amount', 0))
            currency = request.data.get('currency', 'usd')
            if amount <=0:
                return Response(
                    {'error': 'Сумма должна быть больше нуля.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                automatic_payment_methods={'enabled': True}
            )
            return Response(
                {'clientSecret': payment_intent.client_secret},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
class ChatView(APIView):
    def post(self, request, *args, **kwargs):
        user_message = request.data.get('message', '')
        if not user_message:
            return Response({'error': 'Сообщение не может быть пустым'}, status=status.HTTP_400_BAD_REQUST)
        HF_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
        model_url = 'https://api-inference.huggingface.co/models/Qwen/Qwen2.5-72B-Instruct'
        headers = {'Autorization': f'Bearer {HF_API_KEY}'}
        payload = {
            'inputs': user_message,
            'parameters': {'max_new_tokens': 200, 'temperature': 0.7}
        }
        try:
            response = requests.post(model_url, headers=headers, json=payload)
            response.raise_for_status()
            ai_response = response.json()[0]['generated_text']
            return Response({'response': ai_response})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# Create your views here.