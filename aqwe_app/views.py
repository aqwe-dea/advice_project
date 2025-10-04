import os
import io
import requests
import stripe
import logging
import json
import uuid
import base64
import numpy as np
import re
from PyPDF2 import PdfReader
from typing import Dict, List
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
from django.core.files.storage import default_storage
from django.utils import timezone
from PIL import Image
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)
@method_decorator(csrf_exempt, name='dispatch')
@permission_classes([AllowAny])

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
            prompt = f"""
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
                max_tokens=1800
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
        Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
        Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
        Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
        Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
        Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        course_topic = request.data.get('course_topic', '')
        target_audience = request.data.get('target_audience', 'начинающие')
        course_duration = request.data.get('course_duration', '4 недели')
        knowledge_level = request.data.get('knowledge_level', 'базовый')
        course_format = request.data.get('course_format', 'онлайн с видеоуроками')
        learning_objectives = request.data.get('learning_objectives', '')
        practical_tasks = request.data.get('practical_tasks', 'есть')
        certification = request.data.get('certification', 'есть')
        if not course_topic:
            return Response({'error': 'Тема курса обязательна для заполнения'}, status=status.HTTP_400_BAD_REQUEST)
        if not learning_objectives:
            return Response({'error': 'Цели обучения обязательны для заполнения'}, status=status.HTTP_400_BAD_REQUEST)
        HF_API_KEY = os.getenv('HF_API_KEY')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face для генерации курсов не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            logger.info(f"Генерация курса по теме: {course_topic} для аудитории: {target_audience}")
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=HF_API_KEY
            )
            prompt = f"""
                {SYSTEM_PROMPT}
                Создайте подробную структуру образовательного курса по следующим параметрам:
                    - Тема курса: {course_topic}
                    - Целевая аудитория: {target_audience}
                    - Продолжительность курса: {course_duration}
                    - Уровень знаний: {knowledge_level}
                    - Формат курса: {course_format}
                    - Основные цели обучения: {learning_objectives}
                    - Практические задания: {practical_tasks}
                    - Сертификация: {certification}
                
                Структура курса должна включать:
                    1. Введение в курс
                        - Краткое описание курса и его значимости
                        - Для кого предназначен курс
                        - Что студенты получат по окончании курса
                        - Необходимые предварительные знания
                    
                    2. Подробная структура курса (по модулям)
                        - Название и краткое описание каждого модуля
                        - Цели каждого модуля
                        - Продолжительность каждого модуля
                        - Основные темы и подтемы
                        
                    3. Методология обучения
                        - Используемые методы обучения (лекции, кейсы, групповые работы и т.д.)
                        - Как обеспечивается вовлеченность студентов
                        - Как адаптируется курс под разные стили обучения
                        
                    4. Практические задания и проекты
                        - Описание практических заданий для каждого модуля
                        - Критерии оценки заданий
                        - Примеры реальных проектов
                        
                    5. Оценка знаний и обратная связь
                        - Формы контроля знаний (тесты, проекты, экзамены)
                        - Как и когда студенты получают обратную связь
                        - Система оценок и сертификации
                        
                    6. Рекомендуемые материалы
                        - Основная литература и ресурсы
                        - Дополнительные материалы для углубленного изучения
                        - Онлайн-ресурсы и сообщества
                        
                    7. Расписание и план занятий
                        - Подробный план на весь курс
                        - Что изучается на каждом занятии
                        - Домашние задания и дедлайны
                        
                    8. Примеры успешных кейсов
                        - Истории успеха выпускников
                        - Как знания из курса были применены в реальной жизни
                        - Отзывы студентов
                        
                    9. Поддержка студентов
                        - Как студенты могут получать помощь
                        - Доступ к преподавателям и менторам
                        - Форумы и сообщества для обсуждения
                        
                    10. Рекомендации по дальнейшему обучению
                        - Какие курсы или направления изучать после этого
                        - Как продолжить развитие в этой области
                        - Возможные карьерные пути
                        
                Ответ должен быть профессиональным, детализированным и содержать конкретные примеры.
                Структура ответа должна четко соответствовать указанным разделам.
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            return Response({
                'course_structure': response.choices[0].message.content,
                'course_topic': course_topic,
                'target_audience': target_audience,
                'course_duration': course_duration,
                'knowledge_level': knowledge_level,
                'course_format': course_format,
                'learning_objectives': learning_objectives,
                'practical_tasks': practical_tasks,
                'certification': certification
            }) 
        except Exception as e:
            logger.error(f"Ошибка генерации курса: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LegalDocumentAnalysisView(APIView):
    def post(self, request, *args, **kwargs):
        SYSTEM_PROMPT = """
        Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
        Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
        Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
        Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
        Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
        Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        if 'file' not in request.FILES:
            return Response(
                {'error': 'Файл не предоставлен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        uploaded_file = request.FILES['file']
        if not uploaded_file.name.lower().endswith('.pdf'):
            return Response(
                {'error': 'Поддерживаются только PDF-файлы'},
                status=status.HTTP_400_BAD_REQUEST
            )
        file_path = default_storage.save(f'tmp/{uploaded_file.name}', ContentFile(uploaded_file.read()))
        try:
            with open(default_storage.path(file_path), 'rb') as f:
                pdf_reader = PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
            HF_API_KEY = os.getenv('HF_API_KEY_UR')
            if not HF_API_KEY:
                return Response(
                    {'error': 'API ключ для юридического анализа не настроен'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            prompt = f"""
                {SYSTEM_PROMPT}
                Вы - сертифицированный юрист с опытом работы в юридической фирме.
                Ваши рекомендации соответствуют законодательству Российской Федерации.
                
                Проанализируйте юридический документ: "{text[:5000]}"
                
                Ваш анализ должен включать:
                1. Выявление ключевых рисков и уязвимостей в документе
                2. Проверку соответствия документа Гражданскому кодексу РФ
                3. Определение потенциальных нарушений законодательства
                4. Предложение конкретных правок для минимизации юридических рисков
                5. Сравнение с судебной практикой по аналогичным делам
                6. Формирование структурированного отчета с рекомендациями
                
                Ответ должен быть профессиональным, структурированным и содержать ссылки на конкретные статьи ГК РФ.
            """
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=HF_API_KEY
            )
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            return Response({
                'document_summary': {
                    'file_name': uploaded_file.name,
                    'page_count': len(pdf_reader.pages),
                    'text_length': len(text)
                },
                'analysis': response.choices[0].message.content
            })
        except Exception as e:
            logger.error(f"Ошибка при обработке юридического документа: {str(e)}")
            return Response(
                {'error': 'Произошла ошибка при обработке документа'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            if 'file_path' in locals() and default_storage.exists(file_path):
                default_storage.delete(file_path)
    
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
        if not financial_data or not isinstance(financial_data, list):
            return Response({'error': 'Финансовые данные не предоставлены'}, status=status.HTTP_400_BAD_REQUEST)
        country = request.data.get('country', 'Россия')
        HF_API_KEY = os.getenv('HF_API_KEY_FIN')
        if not HF_API_KEY:
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            total_revenue = sum(float(item['revenue']) for item in financial_data)
            total_expenses = sum(float(item['expenses']) for item in financial_data)
            profit = total_revenue - total_expenses
            profit_margin = profit / total_revenue if total_revenue else 0
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=HF_API_KEY
            )
            prompt = f"""
                {SYSTEM_PROMPT}
                Вы - сертифицированный финансовый аналитик с опытом работы в Big4.
                Ваши рекомендации соответствуют международным стандартам финансовой отчетности (МСФО).
                Проанализируйте финансовую отчетность: "{financial_data}"
                Ваш анализ должен включать:
                    - Расчет ключевых финансовых коэффициентов
                    - Оценку ликвидности, рентабельности и финансовой устойчивости
                    - Выявление аномалий и потенциальных мошеннических схем
                    - Прогнозирование финансовых показателей на следующий период
                    - Конкретные рекомендации по оптимизации финансовой деятельности
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
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
    def analyze_damage(image_data):
        try:
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            damage_severity = 0.2        
            if width < 500 or height < 500:
                damage_severity += 0.1    
            img_array = np.array(image)
            if np.mean(img_array) < 50:
                damage_severity += 0.15
            elif np.mean(img_array) > 200:
                damage_severity += 0.1
            damage_severity = min(max(damage_severity, 0), 1)
            return {
                "damage_type": "fading" if damage_severity < 0.3 else "scratches",
                "damage_severity": damage_severity,
                "recommended_method": "local" if damage_severity < 0.4 else "generation",
                "description": "Изображение имеет умеренные потери цвета и небольшие царапины"
            }
        except Exception as e:
            logger.error(f"Ошибка анализа повреждений: {str(e)}")
            return {
                "damage_type": "unknown",
                "damage_severity": 0.5,
                "recommended_method": "generation",
                "description": "Не удалось автоматически определить тип повреждений"
            }
    def process_locally(image_data, damage_analysis):
        try:
            return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Ошибка локальной обработки: {str(e)}")
            raise
    def generate_from_description(image_data, description):
        try:
            return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Ошибка генерации изображения: {str(e)}")
            raise
    def post(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на реставрацию фотографии: {request.data}")
        SYSTEM_PROMPT = """
        Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
        Вы - эксперт по обработке изображений с 8-летним опытом работы в цифровой реставрации.
        Ваши рекомендации основаны на передовых методах обработки изображений..
        Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
        Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
        Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
        Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
        Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        image = request.FILES.get('image')
        if not image:
            return Response({'error': 'Изображение не загружено'}, status=status.HTTP_400_BAD_REQUEST)   
        repair_level = request.data.get('repair_level', 'medium')
        HF_API_KEY = os.getenv('HF_API_KEY_PREST')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=HF_API_KEY
            )
            image_data = image.read()
            damage_analysis = analyze_damage(image_data)
            if repair_level == 'light' or (repair_level == 'medium' and damage_analysis['damage_severity'] < 0.3):
                restored_image_base64 = process_locally(image_data, damage_analysis)
            else:
                restored_image_base64 = generate_from_description(image_data, damage_analysis['description'])
            prompt = """
                {SYSTEM_PROMPT}
                Проанализируйте фотографию и предоставьте отчет о восстановлении.
                Тип повреждений: {damage_analysis['damage_type']}
                Степень повреждения: {damage_analysis['damage_severity']:.2f}
                Рекомендованный метод: {damage_analysis['recommended_method']}
                Ваш отчет должен включать:
                    1. Краткое описание обнаруженных повреждений
                    2. Описание примененного метода восстановления
                    3. Рекомендации по дальнейшему сохранению фотографии
                    4. Оценку качества восстановления (в процентах)
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            restoration_report = response.choices[0].message.content
            return Response({
                'restored_image': f"data:image/jpeg;base64,{restored_image_base64}",
                'analysis': damage_analysis,
                'restoration_report': restoration_report,
                'repair_level': repair_level
            })
        except Exception as e:
            logger.error(f"Ошибка генерации плана реставрации: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
class MedicalImageView(APIView):
    def post(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на медицинский анализ: {request.data}")
        SYSTEM_PROMPT = """
        Вы - Советница АКВИ, профессиональный медицинский консультант с экспертными знаниями в диагностике и лечении заболеваний.
        Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
        Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
        Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
        Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных медицинских источниках.
        Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        if 'image' not in request.FILES:
            return Response(
                {'error': 'Изображение не предоставлено'},
                status=status.HTTP_400_BAD_REQUEST
            )
        image_file = request.FILES['image']
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.dcm']
        file_ext = os.path.splitext(image_file.name)[1].lower()
        if file_ext not in allowed_extensions:
            return Response(
                {'error': f'Поддерживаются только форматы: {", ".join(allowed_extensions)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        patient_info = {
            'age': request.data.get('age', ''),
            'gender': request.data.get('gender', 'не указан'),
            'symptoms': request.data.get('symptoms', ''),
            'medical_history': request.data.get('medical_history', ''),
            'imaging_type': request.data.get('imaging_type', 'рентген')
        }
        file_path = default_storage.save(f'tmp/{image_file.name}', ContentFile(image_file.read()))
        try:
            HF_API_KEY = os.getenv('HF_API_KEY_MEDIC')
            if not HF_API_KEY:
                logger.error("API ключ Hugging Face для медицинского анализа не настроен")
                return Response(
                    {'error': 'API ключ не настроен'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            image_description = self.analyze_image(file_path, HF_API_KEY)
            medical_analysis = self.generate_medical_analysis(
                image_description, 
                patient_info,
                HF_API_KEY
            )
            return Response({
                'image_description': image_description,
                'medical_analysis': medical_analysis,
                'patient_info': patient_info,
                'image_type': file_ext[1:].upper()
            })    
        except Exception as e:
            logger.error(f"Ошибка медицинского анализа: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Произошла ошибка при анализе изображения'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            if 'file_path' in locals() and default_storage.exists(file_path):
                default_storage.delete(file_path)
    def analyze_image(self, image_path, hf_api_key):
        try:
            client = InferenceClient(
                model="Qwen/Qwen2-VL-72B-Instruct",
                token=hf_api_key
            )
            prompt = """
            Вы - профессиональный медицинский специалист, который анализирует медицинские изображения.
            Внимательно изучите предоставленное изображение и опишите:
            1. Тип изображения (рентген, УЗИ, МРТ, КТ и т.д.)
            2. Общее качество изображения
            3. Видимые анатомические структуры
            4. Патологические изменения, если они обнаружены
            5. Подозрительные области, требующие дополнительного внимания
            
            Ваш ответ должен быть профессиональным, точным и структурированным.
            """
            response = client.chat_completion(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"file://{image_path}"}}
                        ]
                    }
                ],
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Ошибка анализа изображения: {str(e)}")
            return "Не удалось проанализировать изображение"
    def generate_medical_analysis(self, image_description, patient_info, hf_api_key):
        try:
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=hf_api_key
            )
            prompt = f"""
                {SYSTEM_PROMPT}
                Проведите комплексный медицинский анализ на основе следующих данных:
                
                Описание изображения:
                {image_description}
                
                Информация о пациенте:
                - Возраст: {patient_info['age']}
                - Пол: {patient_info['gender']}
                - Симптомы: {patient_info['symptoms']}
                - Медицинская история: {patient_info['medical_history']}
                - Тип изображения: {patient_info['imaging_type']}
                
                Ваш анализ должен включать:
                
                1. Интерпретация результатов
                    - Подробное описание выявленных аномалий
                    - Сравнение с нормой
                    - Оценка степени тяжести выявленных изменений
                
                2. Диагностические рекомендации
                    - Какие дополнительные исследования могут понадобиться
                    - Какие специалисты должны быть привлечены
                    - Какие лабораторные анализы рекомендованы
                
                3. Возможные диагнозы
                    - Основные предполагаемые диагнозы (в порядке вероятности)
                    - Дифференциальная диагностика
                    - Критерии, подтверждающие или исключающие каждый диагноз
                
                4. Рекомендации по лечению
                    - Неотложные меры, если они необходимы
                    - Консервативные методы лечения
                    - Хирургические варианты, если применимо
                    - Рекомендации по медикаментозной терапии
                
                5. Рекомендации по наблюдению
                    - Как часто следует проводить контрольные исследования
                    - Какие показатели необходимо отслеживать
                    - При каких условиях требуется срочное обращение к врачу
                
                6. Прогноз
                    - Краткосрочный прогноз
                    - Долгосрочный прогноз
                    - Факторы, которые могут повлиять на прогноз
                
                7. Рекомендации по образу жизни
                    - Диетические рекомендации
                    - Физическая активность
                    - Психологические аспекты и рекомендации
                
                Важно: Это не заменяет профессиональную медицинскую консультацию.
                Ответ должен быть структурирован, безопасен и профессионален.
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Ошибка генерации медицинского анализа: {str(e)}")
            return "Не удалось сгенерировать медицинский анализ"

class ThreeDToProjectView(APIView):
    def analyze_3d_model(model_data, model_type):
        try:
            if model_type == "stl":
                return {
                    "model_type": "furniture",
                    "components": [
                        {
                            "name": "base",
                            "description": "Основание конструкции",
                            "dimensions": {"x": 50.0, "y": 50.0, "z": 5.0},
                            "material_recommendations": ["plywood", "mdf"]
                        },
                        {
                            "name": "legs",
                            "description": "Ножки конструкции",
                            "dimensions": {"x": 5.0, "y": 5.0, "z": 70.0},
                            "material_recommendations": ["hardwood", "metal"]
                        }
                    ],
                    "complexity": 0.6,
                    "estimated_print_time": "3 hours"
                }
            elif model_type == "obj":
                return {
                    "model_type": "architecture",
                    "components": [
                        {
                            "name": "walls",
                            "description": "Стены здания",
                            "dimensions": {"x": 100.0, "y": 100.0, "z": 20.0},
                            "material_recommendations": ["concrete", "brick"]
                        },
                        {
                            "name": "roof",
                            "description": "Крыша здания",
                            "dimensions": {"x": 100.0, "y": 100.0, "z": 10.0},
                            "material_recommendations": ["metal", "tiles"]
                        }
                    ],
                    "complexity": 0.8,
                    "estimated_print_time": "6 hours"
                }
            else:
                return {
                    "model_type": "unknown",
                    "components": [
                        {
                            "name": "main_part",
                            "description": "Основная часть конструкции",
                            "dimensions": {"x": 30.0, "y": 30.0, "z": 30.0},
                            "material_recommendations": ["plastic", "resin"]
                        }
                    ],
                    "complexity": 0.5,
                    "estimated_print_time": "2 hours"
                }
        except Exception as e:
            logger.error(f"Ошибка анализа 3D модели: {str(e)}")
            return {
                "model_type": "unknown",
                "components": [],
                "complexity": 0.5,
                "estimated_print_time": "unknown"
            }
    def generate_construction_plan(analysis):
        try:
            bill_of_materials = []
            total_cost = 0
            for component in analysis['components']:
                for material in component['material_recommendations'][:1]:
                    volume = component['dimensions']['x'] * component['dimensions']['y'] * component['dimensions']['z'] / 1000000  # в м³
                    cost_per_unit = 500 if material in ["wood", "plywood", "mdf"] else 1000  # руб/м³
                    estimated_cost = volume * cost_per_unit
                    bill_of_materials.append({
                        "component": component['name'],
                        "material": material,
                        "quantity": f"{volume:.2f} м³",
                        "estimated_cost": estimated_cost
                    })
                    total_cost += estimated_cost
            assembly_instructions = [
                {
                    "step_number": 1,
                    "description": "Подготовьте все необходимые материалы и инструменты",
                    "visual_guide": None
                },
                {
                    "step_number": 2,
                    "description": "Соберите основные компоненты конструкции согласно чертежам",
                    "visual_guide": None
                },
                {
                    "step_number": 3,
                    "description": "Выполните соединение компонентов с использованием рекомендованных крепежных элементов",
                    "visual_guide": None
                },
                {
                    "step_number": 4,
                    "description": "Проведите финальную проверку и доработку конструкции",
                    "visual_guide": None
                }
            ]        
            return {
                "bill_of_materials": bill_of_materials,
                "assembly_instructions": assembly_instructions,
                "total_estimated_cost": total_cost,
                "optimization_suggestions": [
                    "Рассмотрите возможность использования более легких материалов для уменьшения общей массы",
                    "Оптимизируйте форму компонентов для уменьшения расхода материала",
                    "Используйте стандартные размеры материалов для минимизации отходов"
                ]
            }
        except Exception as e:
            logger.error(f"Ошибка генерации технического проекта: {str(e)}")
            return {
                "bill_of_materials": [],
                "assembly_instructions": [],
                "total_estimated_cost": 0,
                "optimization_suggestions": [
                    "Не удалось автоматически сгенерировать технический проект"
                ]
            }
    def post(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на обработку 3D модели: {request.data}")
        SYSTEM_PROMPT = """
        Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
        Вы - эксперт по 3D-моделированию и проектированию с 7-летним опытом работы.
        Ваши рекомендации основаны на передовых методах проектирования и оптимизации конструкций.
        Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
        Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
        Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
        Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
        Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        model_file = request.FILES.get('model_file')
        if not model_file:
            return Response({'error': '3D модель не загружена'}, status=status.HTTP_400_BAD_REQUEST)
        model_type = request.data.get('model_type', 'stl')
        output_type = request.data.get('output_type', 'project')
        HF_API_KEY = os.getenv('HF_API_KEY_3D')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            model_data = model_file.read()
            analysis = analyze_3d_model(model_data, model_type)
            construction_plan = generate_construction_plan(analysis)
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=HF_API_KEY
            )
            prompt = f"""
                {SYSTEM_PROMPT}
                Уточните следующий технический проект:
                    Тип модели: {analysis['model_type']}
                    Сложность: {analysis['complexity']:.1f}
                    Оценочное время печати: {analysis['estimated_print_time']}
                    Смета материалов:
                        {json.dumps(construction_plan['bill_of_materials'], indent=2)}
                    Пошаговая инструкция:
                        {json.dumps(construction_plan['assembly_instructions'], indent=2)}
                    Предложения по оптимизации:
                        {chr(10).join(construction_plan['optimization_suggestions'])}
                    Ваш уточненный проект должен:
                        1. Сохранять техническую точность
                        2. Быть понятным для человека без технического образования
                        3. Содержать четкие рекомендации по реализации
                        4. Указывать на возможные сложности и их решения
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1800
            )
            refined_project = response.choices[0].message.content
            return Response({
                'original_model': f"data:model/{model_type};base64,{base64.b64encode(model_data).decode('utf-8')}",
                'analysis': analysis,
                'construction_plan': construction_plan,
                'refined_project': refined_project,
                'model_type': model_type,
                'output_type': output_type
            })
        except Exception as e:
            logger.error(f"Ошибка обработки 3D модели: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class HealthRecommendationView(APIView):
    def post(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на рекомендации по здоровью: {request.data}")
        SYSTEM_PROMPT = """
        Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
        Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
        Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
        Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
        Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
        Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        symptoms = request.data.get('symptoms', '')
        if not symptoms:
            return Response({'error': 'Симптомы не указаны'}, status=status.HTTP_400_BAD_REQUEST)
        age = request.data.get('age', '')
        gender = request.data.get('gender', 'не указан')
        country = request.data.get('country', 'Россия')
        recommendation_type = request.data.get('type', 'общие')
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
                Предоставь рекомендации в следующем формате:
                    - Возможные причины
                    - Рекомендации по образу жизни
                    - Натуральные средства
                    - Рекомендации по питанию
                    - Когда обращаться к врачу
                Ответ должен быть структурирован, безопасен и профессионален.   
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200
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
        logger.info(f"Получен запрос на генерацию бизнес-плана: {request.data}")
        SYSTEM_PROMPT = """
        Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
        Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
        Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
        Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
        Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
        Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        business_idea = request.data.get('idea', '')
        if not business_idea:
            return Response({'error': 'Идея бизнеса не указана'}, status=status.HTTP_400_BAD_REQUEST)
        business_type = request.data.get('type', 'стартап')
        country = request.data.get('country', 'Россия')
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
                Создайте полный бизнес-план для: "{business_idea}"
                БИЗНЕС-ПЛАН ДОЛЖЕН СТРОГО СОДЕРЖАТЬ СЛЕДУЮЩИЕ РАЗДЕЛЫ:
                # НАЗВАНИЕ БИЗНЕС-ПЛАНА
                    [Название проекта]
                ## 1. ИСПОЛНИТЕЛЬНОЕ РЕЗЮМЕ
                    - Краткое описание бизнес-идеи
                    - Целевые показатели
                    - Требуемые инвестиции
                    - Ожидаемая прибыль
                ## 2. ОПИСАНИЕ БИЗНЕСА
                    - Миссия и видение
                    - Цели и задачи
                    - Уникальное торговое предложение
                    - Этапы развития
                ## 3. АНАЛИЗ РЫНКА
                    - Размер рынка
                    - Целевая аудитория
                    - Тренды отрасли
                    - Потребности клиентов
                ## 4. SWOT-АНАЛИЗ
                    - Сильные стороны
                    - Слабые стороны
                    - Возможности
                    - Угрозы
                ## 5. КОНКУРЕНТНЫЙ АНАЛИЗ
                    - Основные конкуренты
                    - Их сильные и слабые стороны
                    - Наше конкурентное преимущество
                    - Позиционирование на рынке
                ## 6. МАРКЕТИНГОВАЯ СТРАТЕГИЯ
                    - Ценообразование
                    - Продвижение
                    - Распределение
                    - Продажи
                ## 7. ПЛАН ОПЕРАЦИЙ
                    - Производственный процесс
                    - Требуемые ресурсы
                    - Поставщики
                    - Качество
                ## 8. ОРГАНИЗАЦИОННАЯ СТРУКТУРА
                    - Штатное расписание
                    - Роли и обязанности
                    - Управленческая структура
                    - Внешние партнеры
                ## 9. ФИНАНСОВЫЙ ПЛАН
                    - Стартовые инвестиции
                    - Прогноз доходов
                    - Прогноз расходов
                    - Точка безубыточности
                    - Прогноз прибыли на 3 года
                ## 10. РИСКИ И ИХ МИНИМИЗАЦИЯ
                    - Основные риски
                    - Вероятность возникновения
                    - Последствия
                    - Меры по минимизации
                ВАЖНО: Ответ должен быть строго структурирован как указано выше, без дополнительных комментариев.
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1800
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
        logger.info(f"Получен запрос на генерацию презентации: {request.data}")
        SYSTEM_PROMPT = """
        Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
        Вы - эксперт по созданию презентаций с 5-летним опытом работы.
        Ваши презентации соответствуют международным стандартам и учитывают особенности восприятия аудитории.
        Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
        Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
        Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
        Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
        Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        topic = request.data.get('topic', '')
        if not topic:
            return Response({'error': 'Тема презентации не указана'}, status=status.HTTP_400_BAD_REQUEST)
        audience = request.data.get('audience', 'общая аудитория')
        duration = request.data.get('duration', '30 минут')
        style = request.data.get('style', 'профессиональный')
        HF_API_KEY = os.getenv('HF_API_KEY_SLD')
        if not HF_API_KEY:
            logger.error("API ключ Hugging Face не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            client = InferenceClient(
                model="Qwen/Qwen2.5-72B-Instruct",
                token=HF_API_KEY
            )
            prompt = f"""
                {SYSTEM_PROMPT}
                Создайте профессиональную презентацию на тему: "{topic}"
                Целевая аудитория: {audience}
                Продолжительность: {duration}
                Стиль: {style}
                СТРОГО СЛЕДУЙТЕ ЭТОЙ СТРУКТУРЕ:
                    # ЗАГОЛОВОК ПРЕЗЕНТАЦИИ
                        [Краткий, привлекающий внимание заголовок]
                    ## СЛАЙД 1: ВВЕДЕНИЕ
                        - Заголовок слайда: [текст]
                        - Содержание: [3-4 пункта]
                        - Визуальные рекомендации: [описание]
                        - Заметки докладчика: [текст]
                    ## СЛАЙД 2: [ТЕМА СЛАЙДА]
                        - Заголовок слайда: [текст]
                        - Содержание: [3-4 пункта]
                        - Визуальные рекомендации: [описание]
                        - Заметки докладчика: [текст]
                    [И так для всех слайдов - всего 8-12 слайдов]
                    ## ЗАКЛЮЧЕНИЕ
                        - Основные выводы: [3-4 пункта]
                        - Призыв к действию: [текст]
                    ## ДОПОЛНИТЕЛЬНЫЕ МАТЕРИАЛЫ
                        - Рекомендуемая литература: [3-5 источников]
                        - Полезные ресурсы: [ссылки]
                        - Контактная информация: [текст]
                ВАЖНО: Ответ должен быть строго структурирован как указано выше, без дополнительных комментариев.
                Не используйте маркированные списки в содержании - используйте формат "1. [пункт]"
            """
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200
            )
            presentation_data = self.parse_presentation(response.choices[0].message.content)
            return Response({
                'presentation': response.choices[0].message.content,
                'structured_presentation': presentation_data,
                'topic': topic,
                'audience': audience,
                'duration': duration,
                'style': style
            })
        except Exception as e:
            logger.error(f"Ошибка генерации презентации: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def parse_presentation(self, presentation_text):
        try:
            slides = []
            current_slide = None
            for line in presentation_text.split('\n'):
                line = line.strip()
                if line.startswith("# ЗАГОЛОВОК ПРЕЗЕНТАЦИИ"):
                    continue
                elif line and not line.startswith("#") and current_slide is None:
                    slides.append({
                        'title': 'Заголовок',
                        'content': line,
                        'visual': '',
                        'notes': ''
                    })
                    continue
                if line.startswith("## СЛАЙД"):
                    if current_slide:
                        slides.append(current_slide)
                    parts = line.split(":", 1)
                    slide_title = parts[1].strip() if len(parts) > 1 else "Новый слайд"
                    current_slide = {
                        'title': slide_title,
                        'content': '',
                        'visual': '',
                        'notes': ''
                    }
                elif current_slide:
                    if line.startswith("- Заголовок слайда:"):
                        current_slide['title'] = line.replace("- Заголовок слайда:", "").strip()
                    elif line.startswith("- Содержание:"):
                        current_slide['content'] = line.replace("- Содержание:", "").strip()
                    elif line.startswith("- Визуальные рекомендации:"):
                        current_slide['visual'] = line.replace("- Визуальные рекомендации:", "").strip()
                    elif line.startswith("- Заметки докладчика:"):
                        current_slide['notes'] = line.replace("- Заметки докладчика:", "").strip()
            if current_slide:
                slides.append(current_slide)
            return {
                'slides': slides,
                'original_text': presentation_text
            }
        except Exception as e:
            logger.error(f"Ошибка парсинга презентации: {str(e)}")
            return {
                'slides': [],
                'original_text': presentation_text
            }

class InvestmentAnalysisView(APIView):
    def post(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на анализ инвестиций: {request.data}")
        SYSTEM_PROMPT = """
        Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
        Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
        Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
        Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
        Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
        Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        initial_investment = request.data.get('initial_investment', '')
        expected_return = request.data.get('expected_return', '')
        investment_period = request.data.get('investment_period', '')
        if not initial_investment or not expected_return or not investment_period:
            return Response({'error': 'Необходимо указать начальные инвестиции, ожидаемую доходность и период инвестирования'}, status=status.HTTP_400_BAD_REQUEST)
        risk_level = request.data.get('risk_level', 'средний')
        investment_type = request.data.get('investment_type', 'акции')
        country = request.data.get('country', 'Россия')
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
                max_tokens=1800
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
        logger.info(f"Получен запрос на маркетинговую стратегию: {request.data}")
        SYSTEM_PROMPT = """
        Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
        Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
        Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
        Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
        Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
        Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        idea = request.data.get('idea', '')
        if not idea:
            return Response({'error': 'Идея не указана'}, status=status.HTTP_400_BAD_REQUEST)
        target_audience = request.data.get('target_audience', 'широкая аудитория')
        budget = request.data.get('budget', 'средний')
        timeframe = request.data.get('timeframe', '3 месяца')
        country = request.data.get('country', 'Россия')
        platform = request.data.get('platform', 'многофункциональная')
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
                Создай подробную стратегию продвижения для идеи: "{idea}"
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
                max_tokens=1800
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
        logger.info(f"Получен запрос на планирование путешествия: {request.data}")
        SYSTEM_PROMPT = """
        Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
        Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
        Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
        Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
        Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
        Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        destination = request.data.get('destination', '')
        if not destination:
            return Response({'error': 'Назначение путешествия не указано'}, status=status.HTTP_400_BAD_REQUEST)
        budget = request.data.get('budget', 'средний')
        travel_dates = request.data.get('travel_dates', 'июль-август')
        travel_style = request.data.get('travel_style', 'активный отдых')
        group_type = request.data.get('group_type', 'один/одна')
        special_interests = request.data.get('special_interests', 'общие')
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
                max_tokens=1400
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
        logger.info(f"Получен запрос на анализ конкурентов: {request.data}")
        SYSTEM_PROMPT = """
        Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
        Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
        Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
        Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
        Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
        Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
        """
        business_name = request.data.get('business_name', '')
        business_description = request.data.get('business_description', '')
        if not business_name or not business_description:
            return Response({'error': 'Название бизнеса и его описание обязательны'}, status=status.HTTP_400_BAD_REQUEST)
        competitors = request.data.get('competitors', '')
        market_segment = request.data.get('market_segment', 'общий рынок')
        country = request.data.get('country', 'Россия')
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
                Проведи глубокий анализ конкурентов для бизнеса "{business_name}" в сегменте "{market_segment}"
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
                max_tokens=1000
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
        if not communication_problems:
            return Response({'error': 'Описание проблем с коммуникацией обязательно'}, status=status.HTTP_400_BAD_REQUEST)
        current_tools = request.data.get('current_tools', 'стандартные инструменты')
        goals = request.data.get('goals', 'улучшение коммуникации')
        country = request.data.get('country', 'Россия')
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
                max_tokens=900
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