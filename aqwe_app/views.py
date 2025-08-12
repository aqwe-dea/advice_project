import os
import io
import requests
import stripe
import logging
from .models import Advice, UserHistory
from .serializers import AdviceSerializer, UserHistorySerializer
from .utils import send_advice_email
from huggingface_hub import InferenceClient
from huggingface_hub import InferenceApi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework import viewsets
from rest_framework import response
from django.conf import settings
from django.http import JsonResponse
from django.core.files.base import ContentFile
from PIL import Image
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
#from django.http.response import HttpResponse


logger = logging.getLogger(__name__)
@method_decorator(csrf_exempt, name='dispatch')
@permission_classes([AllowAny])
#@api_view(['POST'])

#from djstripe.models.core import PaymentIntent
#from djstripe.models import core
#from djstripe.models import PaymentIntent        

#from django.http import response

class ChatView(APIView):
    def post(self, request, *args, **kwargs):
        user_message = request.data.get('message', '')
        if not user_message:
            return Response({'error': 'Сообщение не может быть пустым'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
        if not HF_API_KEY:
            logger.error("Hugging Face API ключ не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            client = InferenceClient(model="Qwen/Qwen2.5-72B-Instruct", token=HF_API_KEY)
            response = client.chat_completion(
                messages=[{"role": "user", "content": user_message}],
                max_tokens=300
            )
            ai_response = response.choices[0].message.content
            return Response({'response': ai_response})
        except Exception as e:
            logger.error(f"Ошибка чата: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateCourseView(APIView):
    def post(self, request, *args, **kwargs):
        topic = request.data.get('topic', '')
        level = request.data.get('level', 'начинающий')
        duration = request.data.get('duration', '1 месяц')
        if not topic:
            return Response({'error': 'Тема курса не указана'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HF_API_KEY')
        if not HF_API_KEY:
            logger.error("Hugging Face API ключ не настроен")
            return Response({'error': 'API ключ Hugging Face не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            client = InferenceClient(model="Qwen/Qwen2.5-72B-Instruct", token=HF_API_KEY)
            prompt = f"""
            Создай подробный учебный курс по теме "{topic}" для уровня "{level}".
            Курс должен длиться "{duration}" и включать:
            1. Введение и цели курса
            2. Пошаговую программу с темами каждого урока
            3. Рекомендуемые материалы и ресурсы
            4. Практические задания
            5. Тесты для самопроверки
            6. Заключение и рекомендации по дальнейшему обучению
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            course_plan = response.choices[0].message.content
            return Response({'course_plan': course_plan})
        except Exception as e:
            logger.error(f"Ошибка генерации курса: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LegalDocumentAnalysisView(APIView):
    def post(self, request, *args, **kwargs):
        logger.info(f"Получен запрос: {request.data}")
        logger.info(f"FILES: {request.FILES}")
        logger.info(f"Content-Type: {request.content_type}")
        document = ""
        if request.content_type == 'application/json':
            document = request.data.get('document', '')
            country = request.data.get('country', 'Россия')
            logger.info("Обработка JSON-запроса")
        elif 'document' in request.FILES:
            logger.info("Обработка файла из FILES")
            document_file = request.FILES['document']
            if hasattr(document_file, 'read'):
                try:
                    document_content = document_file.read()
                    if isinstance(document_content, bytes, bytearray):
                        document = document_content.decode('utf-8')
                    else:
                        document = document_content
                except Exception as e:
                    logger.error(f"Ошибка при чтении файла: {str(e)}")
                    return Response({'error': f'Ошибка при чтении файла: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                document = str(document_file)
        elif 'document' in request.data:
            document = request.data['document']
            country = request.POST.get('country', 'Россия')
        else:
            for key, value in request.data.items():
                if 'document' in key.lower():
                    document = value
                    break
            country = request.data.get('country', 'Россия')
            logger.info("Обработка других типов запросов")
        if not document:
            return Response({'error': 'Юридический документ не загружен'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(document, str):
            try:
                document = str(document)
            except:
                return Response({'error': 'Документ должен быть строкой'}, status=status.HTTP_400_BAD_REQUEST)
        country = request.data.get('country', 'Россия')
        HF_API_KEY = os.getenv('HF_API_KEY_UR')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            logger.info(f"Анализ юридического документа для {country}")
            client = InferenceClient(model="Qwen/Qwen2.5-72B-Instruct", token=HF_API_KEY)
            prompt = f"""
            Проанализируй юридический документ на соответствие законодательству {country}.
            Документ: {document[:2000]}  
            Предоставь анализ в следующем формате:
            1. Общая оценка соответствия законодательству
            2. Выявленные нарушения (с указанием конкретных статей кодексов)
            3. Рекомендации по исправлению
            4. Потенциальные риски
            Ответ должен быть структурирован и профессионален.
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            return Response({'analysis': response.choices[0].message.content})
        except Exception as e:
            logger.error(f"Ошибка юридического анализа: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FinancialAnalysisView(APIView):
    def post(self, request, *args, **kwargs):
        if 'report' in request.FILES:
            file = request.FILES['report']
            financial_data = [{"revenue": 100000, "expenses": 70000}, {"revenue": 120000, "expenses": 85000}]
        else:
            financial_data = request.data.get('data', [])
        country = request.data.get('country', 'Россия')
        if not financial_data or not isinstance(financial_data, list):
            return Response({'error': 'Финансовые данные не предоставлены'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HF_API_KEY_FIN')
        if not HF_API_KEY:
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            total_revenue = sum(float(item['revenue']) for item in financial_data)
            total_expenses = sum(float(item['expenses']) for item in financial_data)
            profit = total_revenue - total_expenses
            profit_margin = profit / total_revenue if total_revenue else 0
            prompt = f"""
            Проанализируй финансовую отчетность компании из {country}.
            Основные показатели:
            - Общий доход: {total_revenue}
            - Общие расходы: {total_expenses}
            - Прибыль: {profit}
            - Рентабельность: {profit_margin:.2%}
            
            Проведи анализ и предоставь:
            1. Оценку финансового состояния компании
            2. Выявленные риски и нарушения
            3. Рекомендации по оптимизации
            4. Прогноз на следующий период
            
            Ответ должен быть профессиональным и содержать конкретные цифры.
            """
            client = InferenceClient(model="Qwen/Qwen2.5-72B-Instruct", token=HF_API_KEY)
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            return Response({
                'summary': {
                    'total_revenue': total_revenue,
                    'total_expenses': total_expenses,
                    'profit': profit,
                    'profit_margin': profit_margin
                },
                'analysis': response.choices[0].message.content
            })
        except Exception as e:
            logger.error(f"Ошибка финансового анализа: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PhotoRestorationView(APIView):
    def post(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на реставрацию фотографии: {request.FILES}")
        if 'photo' not in request.FILES:
            return Response({'error': 'Фотография не загружена'}, status=status.HTTP_400_BAD_REQUEST)
        photo = request.FILES['photo']
        enhancement_level = request.data.get('enhancement_level', 'стандартное')
        if not photo.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            return Response({'error': 'Поддерживаются только форматы JPG, JPEG и PNG'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HF_API_KEY_PREST')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            logger.info(f"Реставрация фотографии: {photo.name}, уровень улучшения: {enhancement_level}")
            client = InferenceClient(model="Qwen/Qwen2-VL-72B-Instruct", token=HF_API_KEY)
            image = Image.open(photo)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            prompt = f"""
            Проанализируй и улучши это старое фото. Уровень улучшения: {enhancement_level}.
            Задачи:
            1. Убери царапины и повреждения
            2. Улучши резкость и четкость
            3. Восстанови цвета (если фото черно-белое, можно добавить естественную сепию)
            4. Улучши общую композицию
            
            Верни описание того, что ты сделал с фото, и предложи, как его можно использовать после реставрации.
            """
            response = client.image_to_text(img_byte_arr, prompt=prompt)
            return Response({
                'restoration_description': response,
                'enhancement_level': enhancement_level
            })
        except Exception as e:
            logger.error(f"Ошибка реставрации фото: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MedicalImageView(APIView):
    def post(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на анализ медицинского изображения: {request.FILES}")
        if 'image' not in request.FILES:
            return Response({'error': 'Медицинское изображение не загружено'}, status=status.HTTP_400_BAD_REQUEST)
        image = request.FILES['image']
        image_type = request.data.get('image_type', 'рентген')
        country = request.data.get('country', 'Россия')
        if not image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.dcm')):
            return Response({'error': 'Поддерживаются только форматы JPG, JPEG, PNG и DICOM'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HF_API_KEY_MEDIC')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            logger.info(f"Анализ медицинского изображения: {image.name}, тип: {image_type}")
            client = InferenceClient(model="Qwen/Qwen2-VL-72B-Instruct", token=HF_API_KEY)
            img = Image.open(image)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            prompt = f"""
            Проанализируй это медицинское изображение ({image_type}) и опиши, что ты видишь.
            Страна: {country}
            Задачи:
            1. Опиши анатомические структуры на изображении
            2. Выяви возможные аномалии или патологии
            3. Предоставь предварительную оценку состояния
            4. Дай рекомендации по дальнейшим действиям
            Важно: Это не заменяет профессиональную медицинскую консультацию. 
            Ответ должен быть структурирован и профессионален.
            """
            response = client.image_to_text(img_byte_arr, prompt=prompt)
            return Response({
                'analysis': response,
                'image_type': image_type,
                'country': country
            })
        except Exception as e:
            logger.error(f"Ошибка анализа медицинского изображения: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ThreeDToProjectView(APIView):
    def post(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на преобразование 3D-модели: {request.FILES}")
        if 'model' not in request.FILES:
            return Response({'error': '3D-модель не загружена'}, status=status.HTTP_400_BAD_REQUEST)
        model = request.FILES['model']
        project_type = request.data.get('project_type', 'строительный')
        country = request.data.get('country', 'Россия')
        valid_extensions = ['.stl', '.obj', '.fbx', '.3ds', '.dae', '.blend']
        file_ext = os.path.splitext(model.name)[1].lower()
        if file_ext not in valid_extensions:
            return Response({
                'error': f'Поддерживаются только форматы: {", ".join(valid_extensions)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HF_API_KEY_3D')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            logger.info(f"Преобразование 3D-модели: {model.name}, тип проекта: {project_type}")
            client = InferenceClient(model="Qwen/Qwen2-VL-72B-Instruct", token=HF_API_KEY)
            model_content = model.read()
            prompt = f"""
            Проанализируй эту 3D-модель и преобразуй её в реальный проект ({project_type}) для {country}.
            
            Задачи:
            1. Опиши основные характеристики модели (размеры, сложность, особенности)
            2. Предоставь рекомендации по материалам и технологии изготовления
            3. Создай пошаговый план реализации проекта
            4. Укажи возможные сложности и их решения
            5. Дай оценку стоимости и сроков реализации
            
            Ответ должен быть профессиональным и содержать конкретные рекомендации.
            """
            response = client.text_generation(
                prompt,
                max_new_tokens=600
            )
            return Response({
                'analysis': response,
                'project_type': project_type,
                'country': country
            })
        except Exception as e:
            logger.error(f"Ошибка преобразования 3D-модели: {str(e)}")
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