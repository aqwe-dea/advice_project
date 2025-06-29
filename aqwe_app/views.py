import os
import requests
import stripe
from .models import Advice, UserHistory
from .serializers import AdviceSerializer, UserHistorySerializer
from .utils import send_advice_email
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from huggingface_hub import InferenceClient
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.views.generic.base import View

@method_decorator(csrf_exempt, name='dispatch')
@permission_classes([AllowAny])
#@api_view(['POST'])

#from djstripe.models.core import PaymentIntent
#from djstripe.models import core
#from djstripe.models import PaymentIntent        
#from django.http.response import HttpResponse
#from django.http import response

class ChatView(APIView):
    def post(self, request, *args, **kwargs):
        user_message = request.data.get('message', '')
        if not user_message:
            return Response({'error': 'Сообщение не может быть пустым'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
        if not HF_API_KEY:
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            client = InferenceClient(token=HF_API_KEY)
            response = client.chat_completion(
                model="Qwen/Qwen2.5-72B-Instruct",
                messages=[{"role": "user", "content": user_message}],
                max_tokens=200,
                temperature=0.7
            )
            ai_response = response.choices[0].message.content
            return Response({'response': ai_response})
        except requests.exceptions.HTTPError as e:
            return Response({
                'error': 'Не удалось пролучить ответ от модели',
                'status_code': response.status_code,
                'details': response.text
            }, status=500)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        if not category or not question:
            return Response(
                {'error': 'Необходимо указать категорию и вопрос'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user_email = request.data.get('email')
        advice = response.data.get('answer')
        if user_email and advice:
            send_advice_email(user_email, advice)
            return response
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        advice = Advice.objects.create(category=category, question=question, answer=answer)
        try:
            advice = Advice.objects.create(
                category=category,
                question=question,
                answer=answer
            )
            serializer = self.get_serializer(advice)
            answer = answers.get(category.lower(), answers['default'])     
            answers = {
            'финансы': 'Рекомендую создать бюджет и отслеживать расходы.',
            'здоровье': 'Попробуйте больше двигаться и соблюдать режим сна.',
            'образование': 'Определите свои цели и выберете подходящие курсы.',
            'default': 'Для этого случая у меня есть универсальный совет: Будьте терпеливы!'
            }
        except Exception as e:
            return Response(
                {'error': f'Произошла ошибка: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class HuggingFaceView(View):
    HF_API_URL = "https://api-inference.huggingface.co/models/ai-forever/ruT5-base "
    def get_api_headers(self):
        return {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
class GenerateCourseView(HuggingFaceView):
    def get(self, request):
        age = request.GET.get("age", "25")
        interests = request.GET.get("interests", "программирование, дизайн")
        level = request.GET.get("level", "новичок")
        prompt = f"""
        Создай индивидуальный курс для {age}-летнего пользователя с интересами: {interests}, уровень: {level}.
        Курс должен включать:
        - Цели обучения
        - Этапы освоенияя материала
        - Рекомендованные ресурсы
        - Практические задания
        - Оценка прогресса
        """
        try:
            response = requests.post(
                self.HF_API_URL,
                headers=self.get_api_headers(),
                json={"inputs": prompt.strip(), "max_length": 500, "num_return_sequences": 1, "do_sample": True, "temperature": 0.7}
            )
            response.raise_for_status()
            return JsonResponse(response.json())
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": str(e)}, status=500)
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

class CreateCheckoutSessionView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    @api_view(['POST'])
    def post(self, request, *args, **kwargs):
        amount = request.data.get('amount', none)
        currency = request.data.get('currency', 'usd')
        if not amount or amount < 1:
            return Response({'error': 'Сумма должна быть больше 0'}, status=status.HTTP_400_BAD_REQUEST)
        STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
        if not STRIPE_SECRET_KEY:
            return Response({'error': 'Stripe ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            stripe.api_key = STRIPE_SECRET_KEY
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {'name': 'Пожертвование проекту Советница АКВИ'},
                            'unit_amount': amount,
                        },
                        'quantity': 1,
                    }
                ],
                success_url='https://advice-project.onrender.com/donation-success/ ',
                cancel_url='https://advice-project.onrender.com/donation-cancel/ ',
            )
            return Response({'sessionId': checkout_session.id})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
            
class CreatePaymentIntentView(APIView):
    def post(self, request, *args, **kwargs):
        amount = request.data.get('amount', none)
        currency = request.data.get('currency', 'usd')
        if not amount or amount < 1:
            return Response({'error': 'Сумма должна быть больше 0'}, status=status.HTTP_400_BAD_REQUEST)
        STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
        if not STRIPE_SECRET_KEY:
            return Response({'error': 'Stripe ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            stripe.api_key = STRIPE_SECRET_KEY
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='currency',
                payment_method_types=['card'],
                metadata={'integration_check': 'accept_a_payment'}
            )
            return Response({'clientSecret': payment_intent.client_secret})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
# Create your views here.