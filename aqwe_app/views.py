import os
import io
import requests
import stripe
import logging
import json
import uuid
import PyPDF2
import base64
import numpy as np
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
from django.utils import timezone
from PIL import Image
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

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
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
            Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
            Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
            Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        user_message = request.data.get('message', '')
        if not user_message:
            return Response({'error': 'Сообщение не может быть пустым'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
        if not HF_API_KEY:
            logger.error("Hugging Face API ключ не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            CHAT_PROMPT = f"""
                {SYSTEM_PROMPT}
                Пользователь написал: "{user_message}" .
                Как Советница АКВИ, предоставь профессиональный и дружелюбный ответ.
                Твой ответ должен быть структурирован, информативен и соответствовать твоей роли эксперта.
                Не упоминай, что ты ИИ или Qwen - ты всегда Советница АКВИ.
            """ 
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=HF_API_KEY
            )
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
        logger.info(f"Получен запрос на генерацию курса: {request.data}")
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
            Вы - педагогический эксперт с 15-летним опытом разработки учебных программ.
            Ваши курсы соответствуют международным стандартам образования и учитывают особенности обучения в цифровой среде.
            Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
            Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
            Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        topic = request.data.get('topic', '')
        level = request.data.get('level', 'начальный')
        duration = request.data.get('duration', '4 недели')
        if not topic:
            return Response({'error': 'Тема курса не указана'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HF_API_KEY')
        if not HF_API_KEY:
            logger.error("Hugging Face API ключ не настроен")
            return Response({'error': 'API ключ Hugging Face не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            prompt = f"""
            {SYSTEM_PROMPT}
            Вы - эксперт в области педагогики и разработки учебных программ.
            Ваши курсы учитывают:
            - Уровень подготовки обучающегося
            - Цели обучения
            - Временные рамки
            - Практическую применимость материала
            - Интерактивные элементы для поддержания вовлеченности        
            Ваши рекомендации должны быть структурированы, информативны и соответствовать твоей роли эксперта.
            Не упоминайте, что вы ИИ или Qwen - вы всегда Советница АКВИ.
            Создайте персональный курс по запросу: "{topic}" для уровня "{level}" с продолжительностью "{duration}".
            Структура курса должна включать:
            1. Введение с обоснованием актуальности темы
            2. Пошаговую программу с указанием времени на каждый модуль
            3. Рекомендуемые материалы (книги, статьи, видео)
            4. Практические задания с критериями оценки
            5. Тесты для самопроверки
            6. Дополнительные ресурсы для углубленного изучения            
            Ответ должен быть подробным, структурированным и профессиональным.
            """
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=HF_API_KEY
            )
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2200
            )
            return Response({
                'course': response.choices[0].message.content,
                'topic': topic,
                'level': level,
                'duration': duration
            })
        except Exception as e:
            logger.error(f"Ошибка генерации курса: {str(e)}", exc_info=True)
            return Response({'error': f'Ошибка сервера: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LegalDocumentAnalysisView(APIView):
    def extract_text_from_pdf(file):
        try:
            file_stream = io.BytesIO(file.read())
            reader = PyPDF2.PdfReader(file_stream)
            text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    try:
                        corrected_text = page_text.encode('latin1').decode('cp1251')
                        text += corrected_text + "\n"
                    except:
                        text += page_text + "\n"
            return text
        except Exception as e:
            logger.error(f"Ошибка при извлечении текста из PDF: {str(e)}")
            return None
    def post(self, request, *args, **kwargs):
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
            Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
            Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
            Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        logger.info(f"Получен запрос: {request.data}")
        logger.info(f"FILES: {request.FILES}")
        logger.info(f"Content-Type: {request.content_type}")
        # Получаем файл из запроса
        document = request.FILES.get('document')
        if not document:
            return Response({'error': 'Документ не загружен'}, status=status.HTTP_400_BAD_REQUEST)
        # Проверяем тип файла
        if not document.name.lower().endswith('.pdf'):
            return Response({'error': 'Поддерживаются только PDF файлы'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HF_API_KEY_UR')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            logger.info(f"Начало обработки документа: {document.name}") 
            document.seek(0)  # Сбрасываем указатель файла в начало
            document_text = extract_text_from_pdf(document)
            if not document_text or len(document_text.strip()) < 100:
                return Response({
                    'error': 'Не удалось извлечь достаточное количество текста из документа',
                    'suggestion': 'Для PDF с кириллицей рекомендуется скопировать текст в редактор и вставить его в текстовое поле'
                }, status=status.HTTP_400_BAD_REQUEST)
            logger.info(f"Извлечено {len(document_text)} символов из документа")
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=HF_API_KEY
            )
            prompt = f"""
                {SYSTEM_PROMPT}
                Вы - юридический эксперт с 10-летним опытом работы в сфере гражданского права РФ.
                Ваши рекомендации основаны на актуальном законодательстве РФ и судебной практике.
                Проанализируйте следующий юридический документ:
                {document_text[:4000]}  # Ограничиваем длину
                Ваш анализ должен включать:
                - Выявление нарушений законодательства с указанием конкретных статей
                - Оценку рисков для каждой стороны
                - Рекомендации по исправлению выявленных проблем
                - Примеры из судебной практики по аналогичным случаям
                - Предложения по улучшению документа
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400
            )
            return Response({
                'legal_analysis': response.choices[0].message.content,
                'document_name': document.name,
                'extracted_text_length': len(document_text)
            })
        except Exception as e:
            logger.error(f"Ошибка генерации юридического анализа: {str(e)}", exc_info=True)
            return Response({'error': f'Ошибка сервера: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FinancialAnalysisView(APIView):
    def post(self, request, *args, **kwargs):
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
            Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
            Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
            Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
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
                {SYSTEM_PROMPT}
                Вы - сертифицированный финансовый аналитик с опытом работы в Big4.
                Ваши рекомендации соответствуют международным стандартам финансовой отчетности (МСФО).
                Проанализируйте финансовую отчетность: "{financial_data}".
                Ваш анализ должен включать:
                - Расчет ключевых финансовых коэффициентов
                - Оценку ликвидности, рентабельности и финансовой устойчивости
                - Выявление аномалий и потенциальных мошеннических схем
                - Прогнозирование финансовых показателей на следующий период
                - Конкретные рекомендации по оптимизации финансовой деятельности
            """
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=HF_API_KEY
            )
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
        logger.info(f"Получен запрос на реставрацию фотографии: {request.data}")
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
            Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
            Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
            Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        image = request.FILES.get('image')
        if not image:
            return Response({'error': 'Изображение не загружено'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HF_API_KEY_PREST')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            # 1. Сначала получаем описание проблемы с изображением
            image_data = image.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            image.seek(0)  # Сбрасываем указатель файла
            # Используем Qwen-VL для анализа изображения
            client = InferenceClient(
                model="Qwen/Qwen2.5-VL-72B-Instruct",
                token=HF_API_KEY
            )
            # Анализируем изображение
            analysis_prompt = """
            {SYSTEM_PROMPT}
            Вы - эксперт по обработке изображений. Проанализируйте фотографию и определите:
            1. Тип повреждений (царапины, потери цвета, размытость и т.д.)
            2. Области, требующие восстановления
            3. Рекомендуемые методы обработки
            Верните ответ в формате JSON:
            {
                "damage_type": "тип повреждений",
                "affected_areas": ["область 1", "область 2"],
                "recommended_methods": ["метод 1", "метод 2"]
            }
            """
            analysis_messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": analysis_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ]
            analysis_response = client.chat_completion(
                messages=analysis_messages,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            # 2. Теперь обрабатываем изображение с помощью подходящей модели
            try:
                # Конвертируем в PIL Image для обработки
                img = Image.open(io.BytesIO(image_data))
                img = img.convert('RGB')  # Убедимся, что изображение в RGB
                # Подготовим изображение для обработки
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG")
                img_byte = buffered.getvalue()
                img_base64 = base64.b64encode(img_byte).decode('utf-8')
                # Используем модель для фактической реставрации
                restoration_client = InferenceClient(
                    model="SG161222/Realistic_Vision_V5.1_noVAE",
                    token=HF_API_KEY
                )
                # Создаем промпт для реставрации
                restoration_prompt = "high quality restored photo, improved details, vibrant colors, no damage, professional restoration"
                # Выполняем инференс для генерации улучшенного изображения
                output = restoration_client.post(
                    json={
                        "inputs": restoration_prompt,
                        "image": f"data:image/jpeg;base64,{img_base64}",
                        "num_inference_steps": 30
                    }
                )
                # Получаем обработанное изображение
                restored_image_base64 = base64.b64encode(output).decode('utf-8')
                # 3. Возвращаем обработанное изображение и анализ
                return Response({
                    'restored_image': f"data:image/jpeg;base64,{restored_image_base64}",
                    'analysis': analysis_response.choices[0].message.content,
                    'status': 'success'
                })
            except Exception as process_error:
                logger.error(f"Ошибка обработки изображения: {str(process_error)}", exc_info=True)
                # Если не удалось обработать, возвращаем хотя бы анализ
                return Response({
                    'analysis': analysis_response.choices[0].message.content,
                    'error': 'Не удалось выполнить обработку изображения, но анализ предоставлен',
                    'status': 'partial'
                })
        except Exception as e:
            logger.error(f"Ошибка анализа изображения: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MedicalImageView(APIView):
    def post(self, request, *args, **kwargs):
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
            Вы - медицинский эксперт с 10-летним опытом работы в диагностике.
            Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
            Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
            Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        logger.info(f"Получен запрос на анализ медицинского изображения: {request.FILES}")
        image = request.FILES.get('image')
        if not image:
            return Response({'error': 'Изображение не загружено'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HF_API_KEY_MEDIC')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
             # Преобразуем изображение в base64
            image_data = base64.b64encode(image.read()).decode('utf-8')
            image.seek(0)  # Сбрасываем указатель файла
            # Используем правильный клиент
            client = InferenceClient(
                model="Qwen/Qwen2.5-VL-72B-Instruct",
                token=HF_API_KEY
            )
            # Создаем сообщение с изображением
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Проанализируйте это медицинское изображение"},
                        {"type": "image_url", "image_url": {"url": f"image/jpeg;base64,{image_data}"}}
                    ]
                }
            ]
            # Правильный вызов API
            response = client.chat_completion(
                messages=messages,
                max_tokens=500
            )
            return Response({
                'medical_analysis': response.choices[0].message.content,
                'image_name': image.name
            })
        except Exception as e:
            logger.error(f"Ошибка анализа медицинского изображения: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ThreeDToProjectView(APIView):
    def post(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на преобразование 3D-модели: {request.FILES}")
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
            Вы - эксперт по 3D-моделированию с 7-летним опытом работы.
            Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
            Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
            Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        model_file = request.FILES.get('model')
        model_description = request.data.get('model_description', '')
        if not model_file and not model_description:
            return Response({'error': 'Модель не загружена и описание не предоставлено'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HF_API_KEY_3D')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            logger.info(f"Преобразование 3D-модели: {model.name}, тип проекта: {project_type}")
            model_content = model.read()
            client = InferenceClient(
                model="Qwen/Qwen2-VL-72B-Instruct",
                token=HF_API_KEY
            )
            prompt = f"""
            {SYSTEM_PROMPT}
            Проанализируй эту 3D-модель {model_description} и преобразуй её в реальный проект ({project_type}) для {country}.
            Задачи:
            1. Опиши основные характеристики модели (размеры, сложность, особенности)
            2. Предоставь рекомендации по материалам и технологии изготовления
            3. Создай пошаговый план реализации проекта
            4. Укажи возможные сложности и их решения
            5. Дай оценку стоимости и сроков реализации
            Ответ должен быть профессиональным и содержать конкретные рекомендации.
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            return Response({
                'conversion_plan': response.choices[0].message.content,
                'model_description': model_description
            })
        except Exception as e:
            logger.error(f"Ошибка преобразования 3D-модели: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HealthRecommendationView(APIView):
    def post(self, request, *args, **kwargs):
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
            Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
            Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
            Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        logger.info(f"Получен запрос на рекомендации по здоровью: {request.data}")
        symptoms = request.data.get('symptoms', '')
        age = request.data.get('age', '')
        gender = request.data.get('gender', 'не указан')
        country = request.data.get('country', 'Россия')
        recommendation_type = request.data.get('type', 'общие')
        if not symptoms:
            return Response({'error': 'Симптомы не указаны'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HF_API_KEY_REK')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            logger.info(f"Генерация рекомендаций по здоровью для симптомов: {symptoms}")
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=HF_API_KEY
            )
            prompt = f"""
                {SYSTEM_PROMPT}
                Проанализируй следующие симптомы и дай рекомендации по улучшению здоровья:
                Симптомы: {symptoms}
                Возраст: {age}
                Пол: {gender}
                Страна: {country}
                Тип рекомендаций: {recommendation_type}
                Задачи:
                1. Опиши возможные причины симптомов
                2. Предоставь рекомендации по образу жизни для улучшения состояния
                3. Укажи, какие натуральные средства или методы могут помочь
                4. Дай рекомендации по питанию
                5. Укажи, когда следует обратиться к врачу
                Важно: Это не заменяет профессиональную медицинскую консультацию. 
                Ответ должен быть структурирован, безопасен и профессионален.
                Предоставь рекомендации в следующем формате:
                - Возможные причины
                - Рекомендации по образу жизни
                - Натуральные средства
                - Рекомендации по питанию
                - Когда обращаться к врачу
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600
            )
            return Response({
                'recommendation': response.choices[0].message.content,
                'symptoms': symptoms,
                'age': age,
                'gender': gender,
                'country': country,
                'recommendation_type': recommendation_type
            })
        except Exception as e:
            logger.error(f"Ошибка генерации рекомендаций по здоровью: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BusinessPlanView(APIView):
    def post(self, request, *args, **kwargs):
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
            Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
            Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
            Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        logger.info(f"Получен запрос на генерацию бизнес-плана: {request.data}")
        business_idea = request.data.get('idea', '')
        business_type = request.data.get('type', 'стартап')
        country = request.data.get('country', 'Россия')
        if not business_idea:
            return Response({'error': 'Идея бизнеса не указана'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HF_API_KEY_BPLN')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            logger.info(f"Генерация бизнес-плана для идеи: {business_idea}")
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=HF_API_KEY
            )
            prompt = f"""
                {SYSTEM_PROMPT}
                Создай подробный бизнес-план для {business_type} в стране {country} на основе следующей идеи: "{business_idea}".
                Бизнес-план должен включать:
                1. Краткое резюме проекта
                2. Описание продукта/услуги
                3. Анализ рынка и целевой аудитории
                4. Конкурентный анализ
                5. Маркетинговая стратегия
                6. Операционный план
                7. Организационная структура
                8. Финансовый план (прогноз доходов, расходов, прибыли на 3 года)
                9. Анализ рисков и пути их минимизации
                Дополнительно предоставь SWOT-анализ:
                - Сильные стороны (Strengths)
                - Слабые стороны (Weaknesses)
                - Возможности (Opportunities)
                - Угрозы (Threats)
                Ответ должен быть профессиональным, структурированным и содержать конкретные рекомендации.
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            return Response({
                'business_plan': response.choices[0].message.content,
                'business_idea': business_idea,
                'business_type': business_type,
                'country': country
            })
        except Exception as e:
            logger.error(f"Ошибка генерации бизнес-плана: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PresentationGenerationView(APIView):
    def post(self, request, *args, **kwargs):
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
            Вы - эксперт по созданию презентаций с 5-летним опытом работы.
            Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
            Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
            Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        logger.info(f"Получен запрос на генерацию презентации: {request.data}")
        topic = request.data.get('topic', '')
        audience = request.data.get('audience', 'общая аудитория')
        duration = request.data.get('duration', '30 минут')
        style = request.data.get('style', 'профессиональный')
        if not topic:
            return Response({'error': 'Тема презентации не указана'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HF_API_KEY_SLD')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            logger.info(f"Генерация презентации по теме: {topic}")
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=HF_API_KEY
            )
            prompt = f"""
            {SYSTEM_PROMPT}
            Создайте структуру презентации на тему: "{topic}"
            Целевая аудитория: {audience}
            Продолжительность: {duration}
            Стиль: {style}
            Структура должна включать:
            - Заголовки всех слайдов
            - Краткое содержание каждого слайда
            - Рекомендации по визуальному оформлению
            - Заметки докладчика для каждого слайда
            - Рекомендации по времени на каждый слайд
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            return Response({
                'presentation': response.choices[0].message.content,
                'topic': topic,
                'audience': audience,
                'duration': duration,
                'style': style
            })
        except Exception as e:
            logger.error(f"Ошибка генерации презентации: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InvestmentAnalysisView(APIView):
    def post(self, request, *args, **kwargs):
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
            Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
            Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
            Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        logger.info(f"Получен запрос на анализ инвестиций: {request.data}")
        initial_investment = request.data.get('initial_investment', '')
        expected_return = request.data.get('expected_return', '')
        investment_period = request.data.get('investment_period', '')
        risk_level = request.data.get('risk_level', 'средний')
        investment_type = request.data.get('investment_type', 'акции')
        country = request.data.get('country', 'Россия')
        if not initial_investment or not expected_return or not investment_period:
            return Response({
                'error': 'Необходимо указать начальные инвестиции, ожидаемую доходность и период инвестирования'
            }, status=status.HTTP_400_BAD_REQUEST)        
        HF_API_KEY = os.getenv('HF_API_KEY_INVS')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            logger.info(f"Анализ инвестиций: {initial_investment} на {investment_period} с ожидаемой доходностью {expected_return}")
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=HF_API_KEY
            )
            prompt = f"""
                {SYSTEM_PROMPT}
                Проанализируй инвестиционную возможность с следующими параметрами:
                - Начальные инвестиции: {initial_investment}
                - Ожидаемая годовая доходность: {expected_return}
                - Период инвестирования: {investment_period}
                - Уровень риска: {risk_level}
                - Тип инвестиций: {investment_type}
                - Страна: {country}
                Задачи:
                1. Рассчитай потенциальную доходность и конечную сумму
                2. Оцени уровень риска и вероятность достижения целевой доходности
                3. Сравни с альтернативными инвестиционными возможностями
                4. Выяви возможные скрытые риски
                5. Дай рекомендации по оптимизации инвестиционной стратегии
                Ответ должен включать:
                - Расчет потенциальной доходности (с учетом сложных процентов)
                - Оценку рисков (низкий/средний/высокий)
                - Рекомендации по диверсификации
                - Сравнение с рыночными показателями
                - Общую рекомендацию (стоит инвестировать или нет)
                Ответ должен быть профессиональным, содержать конкретные цифры и рекомендации.
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800
            )
            return Response({
                'analysis': response.choices[0].message.content,
                'initial_investment': initial_investment,
                'expected_return': expected_return,
                'investment_period': investment_period,
                'risk_level': risk_level,
                'investment_type': investment_type,
                'country': country
            })
        except Exception as e:
            logger.error(f"Ошибка анализа инвестиций: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MarketingStrategyView(APIView):
    def post(self, request, *args, **kwargs):
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
            Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
            Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
            Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        logger.info(f"Получен запрос на маркетинговую стратегию: {request.data}")
        idea = request.data.get('idea', '')
        target_audience = request.data.get('target_audience', 'широкая аудитория')
        budget = request.data.get('budget', 'средний')
        timeframe = request.data.get('timeframe', '3 месяца')
        country = request.data.get('country', 'Россия')
        platform = request.data.get('platform', 'многофункциональная')
        if not idea:
            return Response({'error': 'Идея не указана'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HF_API_KEY_MAR')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            logger.info(f"Генерация маркетинговой стратегии для идеи: {idea}")
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=HF_API_KEY
            )
            prompt = f"""
            {SYSTEM_PROMPT}
            Создай подробную стратегию продвижения для идеи: "{idea}".
            Параметры:
            - Целевая аудитория: {target_audience}
            - Бюджет: {budget}
            - Временные рамки: {timeframe}
            - Страна: {country}
            - Платформа: {platform}
            Стратегия должна включать:
            1. Анализ целевой аудитории
            - Демографические характеристики
            - Психографические характеристики
            - Поведенческие паттерны
            - Каналы коммуникации
            2. Анализ конкурентов
            - Основные конкуренты
            - Их сильные и слабые стороны
            - Уникальное торговое предложение (УТП)
            3. Многоуровневая стратегия продвижения
            - Онлайн-стратегия (социальные сети, контент-маркетинг, email-маркетинг, SEO)
            - Офлайн-стратегия (мероприятия, печатные материалы, партнерства)
            - Вирусный маркетинг (идеи для вовлечения)
            4. План внедрения
            - Пошаговый план на {timeframe}
            - Приоритетные действия
            - Ожидаемые результаты
            5. Инструменты и технологии
            - Рекомендуемые инструменты для аналитики
            - Платформы для автоматизации
            - Бюджетное распределение
            6. Метрики успеха
            - Ключевые показатели эффективности (KPI)
            - Как измерять успех
            - Корректировка стратегии
            7. Риски и пути их минимизации
            - Возможные проблемы
            - Стратегии преодоления
            Ответ должен быть профессиональным, структурированным и содержать конкретные рекомендации с примерами.
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            return Response({
                'marketing_strategy': response.choices[0].message.content,
                'idea': idea,
                'target_audience': target_audience,
                'budget': budget,
                'timeframe': timeframe,
                'country': country,
                'platform': platform
            })
        except Exception as e:
            logger.error(f"Ошибка генерации маркетинговой стратегии: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TravelPlannerView(APIView):
    def post(self, request, *args, **kwargs):
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
            Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
            Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
            Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        logger.info(f"Получен запрос на планирование путешествия: {request.data}")
        destination = request.data.get('destination', '')
        budget = request.data.get('budget', 'средний')
        travel_dates = request.data.get('travel_dates', 'июль-август')
        travel_style = request.data.get('travel_style', 'активный отдых')
        group_type = request.data.get('group_type', 'один/одна')
        special_interests = request.data.get('special_interests', 'общие')
        if not destination:
            return Response({'error': 'Назначение путешествия не указано'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HF_API_KEY_TURL')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            logger.info(f"Генерация маршрута для путешествия в {destination}")
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=HF_API_KEY
            )
            prompt = f"""
            {SYSTEM_PROMPT}
            Создай подробный план путешествия в {destination} с учетом следующих параметров:
            - Бюджет: {budget}
            - Даты путешествия: {travel_dates}
            - Стиль путешествия: {travel_style}
            - Тип группы: {group_type}
            - Специальные интересы: {special_interests}
            План должен включать:
            1. Обзор назначения
            - Краткое описание места
            - Лучшее время для посещения
            - Особенности климата в выбранный период
            2. Детальный маршрут на каждый день
            - Утренние, дневные и вечерние активности
            - Время на дорогу между локациями
            - Рекомендуемый транспорт
            3. Бюджетный план
            - Примерная стоимость проживания
            - Стоимость еды и развлечений
            - Советы по экономии
            4. Рекомендации по питанию
            - Местная кухня, которую стоит попробовать
            - Рестораны на разные бюджеты
            - Особенности этикета
            5. Культурные особенности
            - Что делать и чего не делать
            - Полезные фразы на местном языке
            - Традиции и праздники в период посещения
            6. Советы по безопасности
            - Области для избегания
            - Экстренные контакты
            - Советы по сохранности личных вещей
            7. Необычные рекомендации
            - Места, которые знают только местные
            - Уникальные мероприятия
            - Скрытые жемчужины
            8. Подготовка к поездке
            - Что взять с собой
            - Документы и визы
            - Медицинские рекомендации
            Ответ должен быть структурирован, информативен и содержать конкретные рекомендации.
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600
            )
            return Response({
                'travel_plan': response.choices[0].message.content,
                'destination': destination,
                'budget': budget,
                'travel_dates': travel_dates,
                'travel_style': travel_style,
                'group_type': group_type,
                'special_interests': special_interests
            })
        except Exception as e:
            logger.error(f"Ошибка генерации плана путешествия: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CompetitorAnalysisView(APIView):
    def post(self, request, *args, **kwargs):
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
            Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
            Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
            Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        logger.info(f"Получен запрос на анализ конкурентов: {request.data}")
        business_name = request.data.get('business_name', '')
        business_description = request.data.get('business_description', '')
        competitors = request.data.get('competitors', '')
        market_segment = request.data.get('market_segment', 'общий рынок')
        country = request.data.get('country', 'Россия')
        if not business_name or not business_description:
            return Response({'error': 'Название бизнеса и его описание обязательны'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HF_API_KEY_KONK')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            logger.info(f"Анализ конкурентов для бизнеса: {business_name}")
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=HF_API_KEY
            )
            prompt = f"""
            {SYSTEM_PROMPT}
            Проведи глубокий анализ конкурентов для бизнеса "{business_name}" в сегменте "{market_segment}".
            Описание бизнеса: {business_description}
            Конкуренты: {competitors}
            Страна: {country}
            Анализ должен включать:
            1. Обзор рынка
            - Размер рынка и темпы роста
            - Ключевые тренды в отрасли
            - Основные игроки
            2. Детальный анализ конкурентов
            - Сильные и слабые стороны каждого конкурента
            - Их уникальные торговые предложения
            - Ценовая политика
            - Каналы продаж и маркетинговые стратегии
            3. SWOT-анализ вашего бизнеса в контексте конкурентов
            - Сильные стороны (что лучше, чем у конкурентов)
            - Слабые стороны (что хуже, чем у конкурентов)
            - Возможности (что можно улучшить)
            - Угрозы (что угрожает вашему бизнесу)
            4. Позиционирование на рынке
            - Где ваш бизнес лучше всего конкурирует
            - Какие сегменты рынка недостаточно обслужены
            - Как выделиться среди конкурентов
            5. Рекомендации по улучшению конкурентоспособности
            - Тактические шаги на ближайшие 3 месяца
            - Стратегические шаги на 6-12 месяцев
            - Конкретные примеры успешных кейсов из других компаний
            6. Анализ онлайн-присутствия конкурентов
            - Эффективность их веб-сайтов
            - Активность в социальных сетях
            - Отзывы клиентов и управление репутацией
            7. Прогноз развития рынка
            - Какие изменения ожидают рынок в ближайшие 1-2 года
            - Как подготовиться к этим изменениям
            - Возможные новые конкуренты
            Ответ должен быть профессиональным, содержать конкретные цифры и рекомендации.
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            return Response({
                'analysis': response.choices[0].message.content,
                'business_name': business_name,
                'market_segment': market_segment,
                'country': country,
                'competitors': competitors
            })
        except Exception as e:
            logger.error(f"Ошибка анализа конкурентов: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CommunicationOptimizationView(APIView):
    def post(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на оптимизацию коммуникации: {request.data}")
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
            Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
            Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
            Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        company_size = request.data.get('company_size', '500+ сотрудников')
        industry = request.data.get('industry', 'общая отрасль')
        communication_problems = request.data.get('communication_problems', '')
        current_tools = request.data.get('current_tools', 'стандартные инструменты')
        goals = request.data.get('goals', 'улучшение коммуникации')
        country = request.data.get('country', 'Россия')
        if not communication_problems:
            return Response({'error': 'Описание проблем с коммуникацией обязательно'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HF_API_KEY_OPMS')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            logger.info(f"Оптимизация коммуникации для компании размером {company_size} в отрасли {industry}")
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=HF_API_KEY
            )
            prompt = f"""
                {SYSTEM_PROMPT}
                Проведи анализ и оптимизацию коммуникации для крупной организации с учетом следующих параметров:
                - Размер компании: {company_size}
                - Отрасль: {industry}
                - Проблемы с коммуникацией: {communication_problems}
                - Текущие используемые инструменты: {current_tools}
                - Цели оптимизации: {goals}
                - Страна: {country}
                Анализ должен включать:
                1. Диагностика текущих проблем
                - Выявление узких мест в коммуникационных процессах
                - Анализ причин возникновения проблем
                - Оценка влияния проблем на бизнес-процессы
                2. Стратегия оптимизации коммуникации
                - Рекомендуемые структурные изменения
                - Оптимизация коммуникационных каналов
                - Улучшение межотраслевого взаимодействия
                3. Технологические решения
                - Рекомендуемые инструменты и платформы
                - Интеграция с существующими системами
                - Оценка стоимости внедрения
                4. Обучение и адаптация персонала
                - Программа обучения сотрудников
                - Стратегия внедрения изменений
                - Как минимизировать сопротивление изменениям
                5. Измерение эффективности
                - Ключевые метрики для оценки улучшений
                - Периодичность оценки
                - Как корректировать стратегию при необходимости
                6. Кейсы успешной оптимизации
                - Примеры из аналогичных компаний
                - Уроки, которые можно извлечь
                - Что делать и чего не делать
                7. План внедрения
                - Пошаговый план на 3, 6 и 12 месяцев
                - Ответственные за каждый этап
                - Бюджетные требования
                8. Риски и пути их минимизации
                - Потенциальные проблемы при внедрении
                - Стратегии преодоления
                - Резервные планы
                Ответ должен быть профессиональным, содержать конкретные рекомендации и примеры из реальных компаний.
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2500
            )
            return Response({
                'optimization_plan': response.choices[0].message.content,
                'company_size': company_size,
                'industry': industry,
                'communication_problems': communication_problems,
                'current_tools': current_tools,
                'goals': goals,
                'country': country
            })
        except Exception as e:
            logger.error(f"Ошибка оптимизации коммуникации: {str(e)}")
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

class CreateSessionView(APIView):
    def post(self, request, *args, **kwargs):
        duration = request.data.get('duration', 1)  # по умолчанию 1 час
        # Проверяем допустимость продолжительности
        if duration < 1 or duration > 168:  # от 1 часа до 168 часов (неделя)
            return Response({'error': 'Недопустимая продолжительность сессии'}, status=status.HTTP_400_BAD_REQUEST)
        # Создаем токен сессии
        session_token = str(uuid.uuid4())
        # Создаем новую сессию
        expires_at = timezone.now() + timedelta(hours=duration)
        session = Session.objects.create(
            id=uuid.uuid4(),
            expires_at=expires_at,
            duration_hours=duration,
            session_token=session_token
        )
        # Возвращаем данные сессии
        return Response({
            'session_id': str(session.id),
            'session_token': session_token,
            'expires_at': session.expires_at,
            'duration_hours': duration,
            'remaining_time': session.remaining_time()
        })

class CreateCheckoutSessionView(APIView):
    def post(self, request, *args, **kwargs):
        duration = request.data.get('duration', 1)
        # Проверяем допустимость продолжительности
        if duration < 1 or duration > 168:
            return Response({'error': 'Недопустимая продолжительность сессии'}, status=status.HTTP_400_BAD_REQUEST)
        # Рассчитываем цену (например, 10 рублей за час)
        price = duration * 10
        try:
            stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
            success_url = request.build_absolute_uri('/payment-success?session_id={CHECKOUT_SESSION_ID}')
            cancel_url = request.build_absolute_uri('/payment-cancelled')
            # Создаем сессию Stripe
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'rub',
                        'product_data': {
                            'name': f'Сессия доступа ({duration} часов)',
                        },
                        'unit_amount': price * 100,  # в копейках
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'duration': str(duration)
                }
            )
            return Response({
                'id': session.id,
                'url': session.url
            })
        except Exception as e:
            logger.error(f"Ошибка создания сессии оплаты: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SessionStatusView(APIView):
    def get(self, request, *args, **kwargs):
        session_token = request.COOKIES.get('session_token')       
        if not session_token:
            return Response({'is_active': False, 'message': 'Сессия не найдена'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            session = Session.objects.get(session_token=session_token)
            is_valid = session.is_valid()
            return Response({
                'is_active': is_valid,
                'expires_at': session.expires_at,
                'duration_hours': session.duration_hours,
                'remaining_time': session.remaining_time(),
                'message': 'Сессия активна' if is_valid else 'Сессия истекла'
            })
        except Session.DoesNotExist:
            return Response({'is_active': False, 'message': 'Сессия не найдена'}, status=status.HTTP_404_NOT_FOUND)

class HandleStripeWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            logger.error(f"Неверный payload: {str(e)}")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Ошибка верификации подписи: {str(e)}")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # Обрабатываем событие оплаты
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            duration = int(session['metadata'].get('duration', 1))
            # Создаем сессию доступа
            expires_at = timezone.now() + timedelta(hours=duration)
            session_token = str(uuid.uuid4())
            Session.objects.create(
                id=uuid.uuid4(),
                expires_at=expires_at,
                duration_hours=duration,
                session_token=session_token
            )
            # Возвращаем данные для фронтенда
            return Response({
                'session_token': session_token,
                'expires_at': expires_at,
                'duration_hours': duration
            })
        return Response(status=status.HTTP_200_OK)
    
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