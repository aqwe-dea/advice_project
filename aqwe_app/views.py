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
import time
import hashlib
from django.conf import settings
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from datetime import timedelta, datetime
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from typing import Dict, List
from .models import Advice, UserHistory
from .serializers import AdviceSerializer, UserHistorySerializer
from .utils import send_advice_email
from rest_framework import views
from rest_framework.views import APIView
from rest_framework import response
from rest_framework.response import Response
from rest_framework import decorators
from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework import viewsets
from PyPDF2 import _reader
from PyPDF2._reader import PdfReader
from PyPDF2 import PdfReader
from PIL import Image
from PIL.Image import Image
from io import BytesIO
from huggingface_hub import InferenceClient
from huggingface_hub import InferenceApi
from huggingface_hub import HfApi
from huggingface_hub import hf_api
from huggingface_hub.hf_api import HfApi
from huggingface_hub import inference_api
from huggingface_hub.inference_api import InferenceApi
from openai import _client
from openai._client import OpenAI
from openai import OpenAI

logger = logging.getLogger(__name__)
@method_decorator(csrf_exempt, name='dispatch')
@permission_classes([AllowAny])

def poll_kie_task(taskid: str, key: str, check_url: str, max_duration: int = 900):
    """
    Опрос задачи KIE.ai с экспоненциальной задержкой
    max_duration: секунд (по доке: 600-900 сек = 10-15 мин)
    """
    
    start_time = time.time()
    elapsed = 0
    attempt = 0
    
    while elapsed < max_duration:
        attempt += 1
        
        if elapsed < 30:
            sleep_time = 3
        elif elapsed < 120:
            sleep_time = 8
        else:
            sleep_time = 20
        
        try:
            check_response = requests.get(
                url=check_url,
                params={"taskId": taskid},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {key}"
                },
                timeout=30
            )
            checkwork = check_response.json()
            state = checkwork.get('data', {}).get('state')
            
            logger.info(f"Попытка {attempt} ({elapsed}с): статус={state}")
            
            if state == 'success':
                result_json_str = checkwork.get('data', {}).get('resultJson', '{}')
                result_data = json.loads(result_json_str)
                result_urls = result_data.get('resultUrls', [])
                
                if result_urls:
                    return result_urls[0].strip()
                else:
                    logger.error("resultUrls пустой в success-ответе")
                    return None
                    
            elif state == 'fail':
                fail_code = checkwork.get('data', {}).get('failCode')
                fail_msg = checkwork.get('data', {}).get('failMsg')
                logger.error(f"Задача не выполнена: code={fail_code}, msg={fail_msg}")
                return None
                
        except requests.Timeout:
            logger.warning(f"Таймаут запроса на попытке {attempt}")
        except Exception as e:
            logger.error(f"Ошибка опроса: {str(e)}")
        
        time.sleep(sleep_time)
        elapsed = time.time() - start_time
    
    logger.error(f"Превышено максимальное время опроса ({max_duration}с)")
    return None

def call_stream_chat_api(key, system_prompt, prompt):
    """Вызывает потоковый чат"""
    try:
        key = os.getenv('KIE_AQWE_SLIDES')
        if not key:
            logger.error("API ключ key не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        client = OpenAI(
            base_url="https://api.kie.ai/gemini-3-flash/v1/",
            api_key=key
        )
        response = client.chat.completions.create(
            stream=False,
            reasoning_effort="high",
            model="gemini-3-flash",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        text_content = response.choices[0].message.content
        if not isinstance(text_content, str):
            text_content = str(text_content)
        reasoning_content = response.choices[0].message.reasoning_content
        return {
            'outcome': text_content,
            'reasoning': reasoning_content
        }
    except Exception as e:
        logger.error(f"Ошибка вызова Gemini API: {str(e)}", exc_info=True)
        return None
        
class ChatView(APIView):
    """Этот класс запускает услугу чат"""
    def post(self, request, *args, **kwargs):
        user_message = request.data.get('message', '')
        if not user_message:
            return Response({'error': 'Сообщение не может быть пустым'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            system_prompt = """
                Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
                Вы говорите на русском языке в дружелюбном, но профессиональном тоне и используете форматированный ответ с четкой структурой.
                Вы не говорите, что вы ИИ или модель или Qwen - вы всегда представляетесь как Советница АКВИ.
                Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации. 
                Будьте кратки и информативны, избегайте повторений.
                Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
                Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
            """
            prompt = f"""
                Пользователь написал: {user_message}
                Как Советница АКВИ, предоставь профессиональный и дружелюбный ответ.
                Твой ответ должен быть структурирован, информативен и соответствовать твоей роли эксперта.
                Не упоминай, что ты ИИ или Qwen - ты всегда Советница АКВИ.
            """ 
            APIKEY = os.getenv('SAMBA_AQWE_SLIDES')
            if not APIKEY:
                logger.error("API ключ SAMBA не настроен")
                return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            client = OpenAI(
                base_url="https://api.sambanova.ai/v1",
                api_key=APIKEY
            )
            completion = client.chat.completions.create(
                model="Llama-4-Maverick-17B-128E-Instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=7000
            )
            text_content = completion.choices[0].message.content
            if not isinstance(text_content, str):
                text_content = str(text_content)
            return Response({
                'response': text_content
            })
        except Exception as e:
            logger.error(f"Ошибка чата: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateCourseView(APIView):
    """Этот класс запускает услугу курсы"""
    def post(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на генерацию курса: {request.data}")
        course_topic = request.data.get('topic', '') or request.data.get('course_topic', '')
        target_audience = request.data.get('target_audience', 'начинающие')
        course_duration = request.data.get('course_duration', '10 недель')
        knowledge_level = request.data.get('knowledge_level', 'углубленный')
        course_format = request.data.get('course_format', 'учебник')
        learning_objectives = request.data.get('learning_objectives', 'Основные цели обучения')
        practical_tasks = request.data.get('practical_tasks', 'есть')
        certification = request.data.get('certification', 'есть')
        if not course_topic:
            return Response({'error': 'Тема курса обязательна для заполнения'}, status=status.HTTP_400_BAD_REQUEST)
        if not learning_objectives:
            return Response({'error': 'Цели обучения обязательны для заполнения'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            logger.info(f"Генерация курса по теме: {course_topic} для аудитории: {target_audience}")
            system_prompt = """
                Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
                Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
                Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
                Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
                Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
                Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
            """
            prompt = f"""
                Создайте подробную структуру образовательного курса по следующим параметрам:
                    - Тема курса: {course_topic}
                    - Целевая аудитория: {target_audience}
                    - Продолжительность курса: {course_duration}
                    - Уровень знаний: {knowledge_level}
                    - Формат курса: {course_format}
                    - Основные цели обучения: {learning_objectives}
                    - Практические задания: {practical_tasks}
                    - Сертификация: {certification}
                
                Пожалуйста, структурируйте ответ СТРОГО в следующем формате:

                ### 1. ВВЕДЕНИЕ В КУРС:
                    - Краткое описание курса и его значимости
                    [Контент]            
                    - Для кого предназначен курс
                    [Контент]
                    - Что студенты получат по окончании курса
                    [Контент]
                    - Необходимые предварительные знания
                    [Контент]

                ### 2. ПОДРОБНАЯ СТРУКТУРА КУРСА (ПО МОДУЛЯМ):
                    - Название и краткое описание каждого модуля
                    [Контент]
                    - Цели каждого модуля
                    [Контент]
                    - Продолжительность каждого модуля
                    [Контент]
                    - Основные темы и подтемы
                    [Контент]

                ### 3. МЕТОДОЛОГИЯ ОБУЧЕНИЯ:
                    - Используемые методы обучения (лекции, кейсы, групповые работы и т.д.)
                    [Контент]
                    - Как обеспечивается вовлеченность студентов
                    [Контент]
                    - Как адаптируется курс под разные стили обучения
                    [Контент]
                    
                ### 4. ПРАКТИЧЕСКИЕ ЗАДАНИЯ И ПРОЕКТЫ:
                    - Описание практических заданий для каждого модуля
                    [Контент]
                    - Критерии оценки заданий
                    [Контент]
                    - Примеры реальных проектов
                    [Контент]
                    
                ### 5. ОЦЕНКА ЗНАНИЙ И ОБРАТНАЯ СВЯЗЬ:
                    - Формы контроля знаний (тесты, проекты, экзамены)
                    [Контент]
                    - Как и когда студенты получают обратную связь
                    [Контент]
                    - Система оценок и сертификации
                    [Контент]
                    
                ### 6. РЕКОМЕНДУЕМЫЕ МАТЕРИАЛЫ:
                    - [Список материалов]
                    [Контент]
                    - Основная литература и ресурсы
                    [Контент]
                    - Дополнительные материалы для углубленного изучения
                    [Контент]
                    - Онлайн-ресурсы и сообщества
                    [Контент]
                
                ### 7. РАСПИСАНИЕ И ПЛАН ЗАНЯТИЙ:
                    - [Детальный график занятий]
                    [Контент]
                    - Подробный план на весь курс
                    [Контент]
                    - Что изучается на каждом занятии
                    [Контент]
                    - Домашние задания и дедлайны
                    [Контент]
                    
                ### 8. ПРИМЕРЫ УСПЕШНЫХ КЕЙСОВ:
                    - Истории успеха выпускников
                    [Контент]
                    - Как знания из курса были применены в реальной жизни
                    [Контент]
                    - Отзывы студентов
                    [Контент]
                        
                ### 9. ПОДДЕРЖКА СТУДЕНТОВ:
                    - Как студенты могут получать помощь
                    [Контент]
                    - Доступ к преподавателям и менторам
                    [Контент]
                    - Форумы и сообщества для обсуждения
                    [Контент]
                        
                ### 10. РЕКОМЕНДАЦИИ ПО ДАЛЬНЕЙШЕМУ ОБУЧЕНИЮ:
                    - Какие курсы или направления изучать после этого
                    [Контент]
                    - Как продолжить развитие в этой области
                    [Контент]
                    - Возможные карьерные пути
                    [Контент]
                
                ...
                    Пожалуйста, замените все [Контент] на реальные подробные ответы. 
                    Вместо шаблонов напишите полные тексты с примерами и пояснениями.
                    Не оставляйте плейсхолдеры, заполните все разделы полностью.
                ...

                Пожалуйста, не добавляйте никаких дополнительных комментариев или пояснений.  
                Ответ должен быть профессиональным, детализированным и содержать конкретные примеры.
                Структура ответа должна четко соответствовать указанным разделам.
            """
            key = os.getenv('AICCTEST')
            client = OpenAI(
                base_url="https://api.ai.cc/v1",
                api_key=key
            )
            completion = client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=10000
            )
            return Response({
                'course_structure': completion.choices[0].message.content,
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
    def build_course_book(self, course_structure, course_topic):
        """Генерирует учебник на основе структуры курса"""
        try:
            logger.info(f"Генерация учебника по теме: {course_topic}")
            system_prompt = """
                Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
                Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
                Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
                Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
                Вы можете обучать студентов, так как имеете степень магистра и бакалавра в образовании.
                Вы используете полную медицинскую терминологию без цензуры.
                Вы создаёте полноценные учебники с полным содержанием всех глав.
                Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
                Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
            """
            min_length = 10000
            max_length = 100000
            prompt = f"""
                Вы - Советница АКВИ, профессиональный автор учебников.
                Создайте учебник по теме: {course_topic}
                Используя следующую структуру курса, разработайте полный учебник: {course_structure}
                Учебник должен содержать:
                    - 1. Содержание (с указанием страниц)
                    - 2. Главы и подзаголовки (с указанием глав и подзаголовков)
                    - 3. Введение (1-4 стр.)
                    - 4. Все разделы учебника (4-40 стр.)
                    - 5. Весь остальной текст учебника (40-85 стр.)
                    - 6. Практические задания и кейсы (85-90 стр.)
                    - 7. Контрольные вопросы (90-95 стр.)
                    - 8. Рекомендации по дальнейшему изучению (95-100 стр.)
                Требования к формату:
                    - Все медицинские термины должны быть написаны полностью.
                    - Содержание должно быть профессиональным, без сокращений (с подробным объяснением)
                    - Используйте академический стиль, как в учебниках (подробное содержание с иллюстрациями)
                    - Не используйте замены для терминов (все слова должны быть полными)
                    - Весь текст разделите на разделы, подразделы, пункты, подпункты (для удобного восприятия)
                    - Все разделы должны быть наполнены текстом (контент должен иметь содержание, введение, разделы, задания, вопросы, рекомендации)
                    - Вставляйте таблицы в текст где это необходимо (можно использовать текстовую графику ascii)
                    - Объем: {min_length}-{max_length} символов (не менее 4000 слов)
                    - Соблюдайте пунктуацию и орфографию.
                    - Используйте знаки препинания и правила правописания.
                    - Используйте форматирование текста и перенос по словам.
                Структура ответа и включите все разделы:
                    - Название курса.
                    - 1. Содержание с страницами (с указанием главы и страницы)
                    - 2. Описание глав главы и подзаголовки (как в структуре курса с подробным наполнением и описанием каждой главы)
                    - 4. Полный текст всех глав и весь текст курса-учебника (полный текст учебника от первой до последней страницы)
                    - 5. Примеры и кейсы и таблицы и схемы (практические задания и кейсы по пунктам)
                    - 6. Контрольные вопросы и практические задания (страница с вопросами и ответами)
                    - 7. Рекомендации по дальнейшему изучению (ссылки на рекомендованные ресурсы материалы книги)
                Требования к объему:
                    - Минимальный объем: {min_length} символов
                    - Максимальный объем: {max_length} символов
                    - Не превышайте указанный объем.
                    - Содержание должно быть полным и логичным.
                ВАЖНО:
                    - Заполните ВСЕ главы полностью (не "Продолжение следует")
                    - Используйте полную медицинскую терминологию
                НЕ ОБРЫВАЙТЕ текст - завершите все главы!
                Важно: Ответ должен быть профессиональным, детализированным и содержать конкретные примеры!     
            """
            key = os.getenv('AICCTEST')
            if not key:
                logger.error("API ключ AICCTEST не настроен")
                return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            client = OpenAI(
                base_url="https://api.ai.cc/v1",
                api_key=key
            )
            completion = client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=10000
            )
            text_content = completion.choices[0].message.content
            if not isinstance(text_content, str):
                text_content = str(text_content)
            return Response({
                'course_book': text_content,
                'course_topic': course_topic
            })
        except Exception as e:
            logger.error(f"Ошибка генерации учебника: {str(e)}", exc_info=True)
            return Response({'error': f'Не удалось сгенерировать учебник: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BuildCourseBookView(APIView):
    """Этот класс запускает услугу учебники"""
    def post(self, request, *args, **kwargs):
        logger.info("Получен запрос на генерацию учебника")
        course_structure = request.data.get('course_structure')
        course_topic = request.data.get('course_topic')        
        if not course_structure or not course_topic:
            return Response({
                'error': 'Необходимы структура курса и тема курса'
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            generate_course_view = GenerateCourseView()
            return generate_course_view.build_course_book(
                course_structure, 
                course_topic
            )
        except Exception as e:
            logger.error(f"Ошибка генерации учебника: {str(e)}", exc_info=True)
            return Response({'error': f'Не удалось сгенерировать учебник: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LegalDocumentAnalysisView(APIView):
    """Этот класс запускает услугу юридический анализ"""
    def post(self, request, *args, **kwargs):
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
            system_prompt = """
                Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
                Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
                Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
                Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
                Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
                Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
            """
            with open(default_storage.path(file_path), 'rb') as f:
                pdf_reader = PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
            prompt = f"""
                Вы - сертифицированный юрист с опытом работы в юридической фирме.
                Ваши рекомендации соответствуют законодательству Российской Федерации.
                Проанализируйте юридический документ: "{text[:8000]}"
                Ваш анализ должен включать:
                    1. Выявление ключевых рисков и уязвимостей в документе
                    2. Проверку соответствия документа Гражданскому кодексу РФ
                    3. Определение потенциальных нарушений законодательства
                    4. Предложение конкретных правок для минимизации юридических рисков
                    5. Сравнение с судебной практикой по аналогичным делам
                    6. Формирование структурированного отчета с рекомендациями
                ВАЖНО: 
                    - Каждый раздел должен быть ТОЛЬКО ОДИН РАЗ (без дублирования)
                    - Все пункты должны быть пронумерованы последовательно
                    - Не обрывайте предложения на полуслове
                Ответ должен быть профессиональным, структурированным и содержать ссылки на конкретные статьи ГК РФ.
            """
            key = os.getenv('AICCTEST')
            client = OpenAI(
                base_url="https://api.ai.cc/v1",
                api_key=key
            )
            completion = client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=10000
            )
            text_content = completion.choices[0].message.content
            if not isinstance(text_content, str):
                text_content = str(text_content)
            return Response({
                'document_summary': {
                    'file_name': uploaded_file.name,
                    'page_count': len(pdf_reader.pages),
                    'text_length': len(text)
                },
                'analysis': text_content
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
    """Этот класс запускает услугу финансовый анализ"""
    def post(self, request, *args, **kwargs):
        if 'report' in request.FILES:
            file = request.FILES['report']
            financial_data = [{"revenue": 100000, "expenses": 70000}, {"revenue": 120000, "expenses": 85000}]
        else:
            financial_data = request.data.get('data', [])
        if not financial_data or not isinstance(financial_data, list):
            return Response({'error': 'Финансовые данные не предоставлены'}, status=status.HTTP_400_BAD_REQUEST)
        country = request.data.get('country', 'Россия')
        try:
            system_prompt = """
                Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
                Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
                Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
                Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
                Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
                Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
            """
            total_revenue = sum(float(item['revenue']) for item in financial_data)
            total_expenses = sum(float(item['expenses']) for item in financial_data)
            profit = total_revenue - total_expenses
            profit_margin = profit / total_revenue if total_revenue else 0
            prompt = f"""
                Вы - сертифицированный финансовый аналитик с опытом работы в Big4.
                Ваши рекомендации соответствуют международным стандартам финансовой отчетности (МСФО).
                Проанализируйте финансовую отчетность: "{financial_data}"
                ВАЖНО:
                    - Если данных недостаточно для расчёта - прямо укажите "Данные недоступны"
                    - Не выдумывайте цифры для баланса
                    - Дайте конкретные рекомендации по оптимизации
                Ваш анализ должен включать:
                    1. Исходные данные
                    2. Расчет ключевых финансовых коэффициентов
                    3. Оценка ликвидности (с указанием недостающих данных)
                    4. Оценка рентабельности
                    5. Оценка финансовой устойчивости
                    6. Выявление аномалий и потенциальных мошеннических схем
                    7. Прогнозирование финансовых показателей на следующий период
                    8. Конкретные рекомендации по оптимизации финансовой деятельности
                    9. Заключение
            """
            key = os.getenv('AICCTEST')
            client = OpenAI(
                base_url="https://api.ai.cc/v1",
                api_key=key
            )
            completion = client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=10000
            )
            text_content = completion.choices[0].message.content
            if not isinstance(text_content, str):
                text_content = str(text_content)
            return Response({
                'summary': {
                    'total_revenue': total_revenue,
                    'total_expenses': total_expenses,
                    'profit': profit,
                    'profit_margin': profit_margin
                },
                'analysis': text_content
            })
        except Exception as e:
            logger.error(f"Ошибка финансового анализа: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PhotoRestorationView(APIView):
    """Этот класс запускает услугу реставрация изображений"""
    def post(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на реставрацию фотографии: {request.data}")
        if 'image' not in request.FILES:
            return Response({'error': 'Изображение не предоставлено'}, status=status.HTTP_400_BAD_REQUEST)
        image_file = request.FILES['image']
        image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']
        file_ext = os.path.splitext(image_file.name)[1].lower()
        if file_ext not in allowed_extensions:
            return Response({'error': f'Поддерживаются только форматы: {", ".join(allowed_extensions)}'}, status=status.HTTP_400_BAD_REQUEST)
        original_file_path = default_storage.save(f'tmp/original_{image_file.name}', ContentFile(image_data))
        original_url = default_storage.url(original_file_path)
        full_original_url = request.build_absolute_uri(original_url)
        system_prompt = """
            Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
            Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
            Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
            Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами.
        """
        restoration_info = {
            'damage_type': request.data.get('damage_type', 'потертости и царапины'),
            'damage_level': request.data.get('damage_level', 'средняя'),
            'restoration_style': request.data.get('restoration_style', 'оригинальный стиль'),
            'special_requests': request.data.get('special_requests', ''),
            'photo_age': request.data.get('photo_age', 'неизвестно')
        }
        try:
            key = os.getenv('KIE_AQWE_SLIDES')
            if not key:
                return Response({'error': 'API ключ key не настроен'}, status=500)

            response = requests.post(
                url="https://api.kie.ai/api/v1/jobs/createTask",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {key}"
                },
                json={
                    "model": "recraft/crisp-upscale",
                    "input": {
                        "image": full_original_url
                    }
                }
            )

            startwork = response.json()
            taskid = startwork.get('data', {}).get('taskId')
            check_url = "https://api.kie.ai/api/v1/jobs/recordInfo"
            result_url = poll_kie_task(taskid, key, check_url, max_duration=600)
            restored_url = None

            if result_url:
                try:
                    restored_response = requests.get(result_url, timeout=60)
                    if restored_response.status_code == 200:
                        image_name = f"restored_{image_file.name}"
                        file_path = default_storage.save(
                            f'tmp/{image_name}', 
                            ContentFile(restored_response.content)
                        )
                        restored_url = default_storage.url(file_path)
                        logger.info(f"Изображение сохранено: {restored_url}")
                    else:
                        logger.error(f"Не удалось скачать: {restored_response.status_code}")
                except Exception as e:
                    logger.error(f"Ошибка скачивания: {str(e)}")
            else:
                logger.error("Не получен result_url от KIE")
            
            if restored_url:
                imageurl = None
            else:
                imageurl = self.restoreimage(full_original_url)   
            restoration_report = self.create_restoration_report(
                restored_url or original_url,
                original_url,
                restoration_info
            )
            
            return Response({
                'restoration_report': restoration_report,
                'restored_url': restored_url,
                'image_type': file_ext[1:].upper(),
                'restoration_info': restoration_info,
                'original_url': original_url,
                'status': result_url,
                'restoreimage': imageurl,
                'startwork': startwork
            })

        except Exception as e:
            logger.error(f"Ошибка реставрации: {str(e)}", exc_info=True)
            return Response({'error': f'Ошибка: {str(e)}'}, status=500)
        finally:
            pass
    def create_restoration_report(self, restored_url, original_url, restoration_info):
        """Создает отчет о реставрации"""
        return {
            'before_after_comparison': {
                'original_url': original_url,
                'restored_url': restored_url
            },
            'restoration_summary': {
                'damage_type': restoration_info['damage_type'],
                'damage_level': restoration_info['damage_level'],
                'restoration_style': restoration_info['restoration_style'],
                'photo_age': restoration_info['photo_age']
            },
            'recommendations': {
                'storage': 'Храните в темном месте при влажности 40-50%',
                'handling': 'Всегда используйте перчатки при обращении',
                'long_term_care': 'Рекомендуется создать цифровую копию для архивации'
            }
        }
    def restoreimage(self, full_original_url):
        """"Дополнительно восстанавливает изображение"""
        try:
            key = os.getenv('KIE_AQWE_SLIDES')

            response = requests.post(
                url="https://api.kie.ai/api/v1/jobs/createTask",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {key}"
                },
                json={
                    "model": "qwen/image-edit",
                    "input": {
                        "image_url": full_original_url,
                        "acceleration": "none",
                        "image_size": "square_hd",
                        "num_inference_steps": 30,
                        "guidance_scale": 4,
                        "sync_mode": False,
                        "enable_safety_checker": False,
                        "output_format": "png",
                        "negative_prompt": "bad, travesty, lie",
                        "prompt": "edit this photo, restore, fix, colorize, upscale",
                        "num_images": "1"
                    }
                }
            )

            check = response.json()
            taskid = check.get('data', {}).get('taskId')
            total_wait = 0
            max_total_wait = 360

            while total_wait < max_total_wait:
                result_response = requests.get(
                    url="https://api.kie.ai/api/v1/jobs/recordInfo",
                    params={
                        "taskId": taskid
                    },
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {key}"
                    },
                    timeout=45
                )
                checkwork = result_response.json()
                state = checkwork.get('data', {}).get('state')
                if state == 'success':
                    urls = checkwork.get('data', {}).get('resultJson', {})
                    if urls:
                        return urls[0].strip()
                elif state == 'fail':
                    logger.error(f"Задача не выполнена: {checkwork}")
                    return None
                time.sleep(10)
                total_wait += 10
            return None

        except Exception as e:
            logger.error(f"Ошибка KIE: {str(e)}", exc_info=True)
            return None
            
class MedicalImageView(APIView):
    """Этот класс запускает услугу медицинский анализ"""
    def post(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на медицинский анализ: {request.data}")
        if 'image' not in request.FILES:
            return Response(
                {'error': 'Изображение не предоставлено'},
                status=status.HTTP_400_BAD_REQUEST
            )
        image_file = request.FILES['image']
        image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')    
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
            APIKEY = os.getenv('OLLAMATEST')
            if not APIKEY:
                logger.error("API ключ OLLAMA не настроен")
                return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            client = OpenAI(
                base_url="https://ollama.com/v1/",
                api_key=APIKEY
            )
            image_description = self.analyze_image(
                base64_image, 
                file_ext
            )
            medical_analysis = self.generate_medical_analysis(
                image_description, 
                patient_info
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
    def analyze_image(self, base64_image, file_ext):
        try:
            logger.info(f"Получен запрос на анализ изображения: {base64_image} в: {file_ext}")
            system_prompt = """
                Вы - Советница АКВИ, профессиональный медицинский консультант с экспертными знаниями в диагностике и лечении заболеваний.
                Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
                Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
                Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
                Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных медицинских источниках.
                Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
            """
            prompt = f"""
                Вы - Советница АКВИ, профессиональный медицинский консультант с экспертизой в интерпретации медицинских изображений.
                Вы говорите на русском языке и используете профессиональную медицинскую терминологию с пояснениями для пациента.

                Пожалуйста проанализируйте изображение: {base64_image} в: {file_ext}
                    
                1. Определите тип изображения:
                    - Это рентген, УЗИ, МРТ, КТ или другой тип?
                    - Какая область тела изображена?
                    
                2. Оцените качество изображения:
                    - Четкость и разрешение
                    - Наличие артефактов или помех
                    - Достаточность для диагностики
                    
                3. Опишите нормальные анатомические структуры:
                    - Перечислите основные структуры, которые должны присутствовать
                    - Укажите их нормальное расположение и вид
                    
                4. Выявите патологические изменения:
                    - Опишите любые аномалии, отклонения от нормы
                    - Укажите их локализацию, размеры и характер
                    - Сравните с типичными проявлениями заболеваний
                    
                5. Предоставьте предварительную интерпретацию:
                    - Какие возможные диагнозы можно предположить?
                    - Какие из них наиболее вероятны и почему?
                    - Есть ли признаки острых или хронических процессов?
                    
                6. Дайте рекомендации:
                    - Какие дополнительные исследования могут понадобиться?
                    - К какому специалисту следует обратиться?
                    - Какие симптомы требуют немедленного внимания?

                Пожалуйста, структурируйте ваш ответ четко по этим пунктам.
                Если вы не уверены в каком-то аспекте, честно укажите это и объясните, почему требуется консультация специалиста.
                Помните: это не замена профессиональной медицинской консультации.
            """
            key = os.getenv('HF_API_KEY')
            if not key:
                logger.error("API ключ не настроен")
                return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            client = OpenAI(
                base_url="https://router.huggingface.co/v1/",
                api_key=key
            )
            chat_completion = client.chat.completions.create(
                model="Qwen/Qwen3-VL-235B-A22B-Instruct:novita",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": f"data:image/{file_ext[1:]};base64,{base64_image}"}
                    ]}
                ],
                temperature=0.3,
                max_tokens=7000
            )
            text_content = chat_completion.choices[0].message.content
            if not isinstance(text_content, str):
                text_content = str(text_content)
            return text_content 
        except Exception as e:
            logger.error(f"Ошибка анализа изображения: {str(e)}")
            return "Не удалось проанализировать изображение"
    def generate_medical_analysis(self, image_description, patient_info):        
        try:
            logger.info(f"Получен запрос на медицинский отчет по: {image_description} с параметрами: {patient_info}")
            system_prompt = """
                Вы - Советница АКВИ, профессиональный медицинский консультант с экспертными знаниями в диагностике и лечении заболеваний.
                Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
                Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
                Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
                Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных медицинских источниках.
                Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
            """
            prompt = f"""
                Проведите комплексный медицинский анализ на основе следующих данных:

                Описание изображения: {image_description}
                
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
            key = os.getenv('OLLAMATEST')
            if not key:
                logger.error("API ключ OLLAMA не настроен")
                return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            client = OpenAI(
                base_url="https://ollama.com/v1/",
                api_key=key
            )
            chat_completion = client.chat.completions.create(
                model="gemma4:31b-cloud",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=7000
            )
            text_content = chat_completion.choices[0].message.content
            if not isinstance(text_content, str):
                text_content = str(text_content)
            return text_content
        except Exception as e:
            logger.error(f"Ошибка генерации медицинского анализа: {str(e)}")
            return "Не удалось сгенерировать медицинский анализ"

class ThreeDToProjectView(APIView):
    """Этот класс запускает услугу 3д моделирования"""
    def post(self, request, *args, **kwargs):
        model_idea = request.data.get('idea', '')
        if not model_idea:
            return Response({'error': 'Идея 3D-модели не указана'}, status=status.HTTP_400_BAD_REQUEST)
        logger.info(f"Получен запрос на план 3D-моделирования: {request.data}")
        model_type = request.data.get('model_type', 'персонаж')
        software = request.data.get('software', 'Blender, Maya, ZBrush')
        complexity = request.data.get('complexity', 'средняя')
        purpose = request.data.get('purpose', 'визуализация, анимация')
        timeframe = request.data.get('timeframe', '2-4 недели')
        logger.info(f"Генерация плана 3D-моделирования для идеи: {model_idea}")
        try:
            system_prompt = """
                Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
                Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
                Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
                Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
                Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
                Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
            """
            prompt = f"""
                Создайте подробный план создания 3D-модели на основе следующих параметров:
                    - Идея модели: {model_idea}
                    - Тип модели: {model_type}
                    - Программное обеспечение: {software}
                    - Сложность: {complexity}
                    - Цель: {purpose}
                    - Временные рамки: {timeframe}
                Структура (8 разделов):
                План должен включать:
                    1. Подготовительный этап (mood-board, концепт-арт, технический бриф)
                        - Сбор референсов и исследование
                        - Создание концепт-артов и скетчей
                        - Определение технических требований
                        - Планирование этапов работы
                    2. Этап моделирования (блокинг, high-poly, ретопология, UV) 
                        - Создание базовой формы (blocking)
                        - Детализация формы (sculpting или polygon modeling)
                        - Топология для анимации (если требуется)
                        - Создание дополнительных элементов и аксессуаров
                    3. Текстурирование и материалы (baking, шейдеры, detail pass)
                        - Создание UV-развертки
                        - Генерация текстур (ручная или с помощью процедурных методов)
                        - Настройка материалов и шейдеров
                        - Добавление деталей (рельеф, нормали, roughness и т.д.)
                    4. Риггинг и анимация (скелет, контроллеры, shape-keys, тесты)
                        - Создание скелета и системы деформации
                        - Настройка контроллеров и ограничений
                        - Тестирование анимации базовых поз
                        - Создание базовых анимаций (если требуется)
                    5. Освещение и рендеринг (light setup, render settings, AOV)
                        - Настройка освещения сцены
                        - Выбор подходящего движка рендеринга
                        - Тестовые рендеры для проверки качества
                        - Финальная настройка и рендеринг
                    6. Пост-обработка (compositor, Photoshop, DOF)
                        - Коррекция цвета и контраста
                        - Добавление эффектов (глубина резкости, блики)
                        - Композитинг и финальная доработка
                        - Подготовка к экспортации в требуемые форматы
                    7. Экспорт и интеграция (форматы, оптимизация, проверка)
                        - Выбор подходящего формата экспорта
                        - Проверка совместимости с целевой платформой
                        - Оптимизация для веб или игр (если требуется)
                        - Интеграция в конечный проект
                    8. Рекомендации по улучшению (глаза, волосы, производительность, pipeline
                        - Какие аспекты можно улучшить
                        - Альтернативные подходы к созданию модели
                        - Советы по оптимизации процесса
                ВАЖНО:
                    - Каждый раздел должен быть ТОЛЬКО ОДИН РАЗ (без дублирования)
                    - Не используйте китайские символы - только русский и английский
                    - Завершите ВСЕ разделы полностью
                Включите:
                    - Конкретные цифры (полигоны, размеры текстур, кости)
                    - Названия инструментов и плагинов
                    - Временные оценки для каждого этапа
                    - Чек-лист в конце    
                НЕ ПОВТОРЯЙТЕ разделы - каждый только один раз!
                Ответ должен быть структурирован, профессионален и содержать конкретные рекомендации с примерами.
            """
            key = os.getenv('ROUTEWAY_AQWE_SLIDES')
            if not key:
                logger.error("API ключ key не настроен")
                return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            client = OpenAI(
                base_url="https://api.routeway.ai/v1",
                api_key=key
            )
            response = client.chat.completions.create(
                model="kimi-k2-0905:free",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=10000,
                stream=False
            )
            text_content = response.choices[0].message.content
            if not isinstance(text_content, str):
                text_content = str(text_content)
            create_image = self.create_image_model(
                model_idea, 
                model_type
            )
            return Response({
                'modeling_plan': text_content,
                'check': response,
                'create_plan': response,
                'model_idea': model_idea,
                'model_type': model_type,
                'software': software,
                'complexity': complexity,
                'purpose': purpose,
                'timeframe': timeframe,
                'image3dmodel': create_image
            })
        except Exception as e:
            logger.error(f"Ошибка генерации плана 3D-моделирования: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def create_image_model(self, model_idea, model_type):
        logger.info(f"Генерация изображение 3D-модели для идеи: {model_idea}")
        try:
            APIKEY = os.getenv('FIREWORKSTESTSA')
            create_image = requests.request(
                method="POST",
                url="https://api.fireworks.ai/inference/v1/workflows/accounts/fireworks/models/flux-1-schnell-fp8/text_to_image",
                headers={
                    "Content-Type": "application/json",
                    'Authorization': f"Bearer {APIKEY}",
                    "Accept": "image/jpeg"
                },
                json={
                    "prompt": f"3D model render: {model_idea}, {model_type}, professional quality, high detail",
                    "width": 1024,
                    "height": 1024,
                    "steps": 30
                }
            )
            if create_image.status_code == 200:
                unique_name = f"aqwegen3dmodel_{hashlib.md5(model_idea.encode()).hexdigest()[:8]}.jpg"
                file_path = default_storage.save(f'tmp/{unique_name}', ContentFile(create_image.content))
                return default_storage.url(file_path)
            else:
                return "Не удалось создать изображение"
        except Exception as e:
            logger.error(f"Ошибка создания изображения 3D модели: {str(e)}", exc_info=True)
            return "Не удалось создать изображение 3D модели"

class HealthRecommendationView(APIView):
    """Этот класс запускает услугу рекомендация по здоровью"""
    def post(self, request, *args, **kwargs):
        symptoms = request.data.get('symptoms', '')
        if not symptoms:
            return Response({'error': 'Симптомы не указаны'}, status=status.HTTP_400_BAD_REQUEST)
        age = request.data.get('age', '')
        gender = request.data.get('gender', 'не указан')
        country = request.data.get('country', 'Россия')
        recommendation_type = request.data.get('type', 'общие')
        logger.info(f"Получен запрос на рекомендации по здоровью: {request.data}")
        try:
            logger.info(f"Генерация рекомендаций по здоровью для симптомов: {symptoms}")
            system_prompt = """
                Вы - Советница АКВИ, профессиональный медицинский консультант с экспертными знаниями в диагностике и лечении заболеваний.
                Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
                Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
                Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
                Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных медицинских источниках.
                Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
                Вы всегда рекомендуете обратиться к врачу при серьезных симптомах.
                Вы используете полную медицинскую терминологию без цензуры.
            """
            prompt = f"""
                Проанализируй следующие симптомы и дай рекомендации по улучшению здоровья:
                    Симптомы: {symptoms}
                    Возраст: {age}
                    Пол: {gender}
                    Страна: {country}
                    Тип рекомендаций: {recommendation_type}
                ВАЖНО:
                    - Используйте полную медицинскую терминологию
                    - Не цензурьте слова
                    - Всегда рекомендуйте консультацию врача
                Структура (6 разделов):
                Задачи:
                    1. Опиши возможные причины симптомов
                    2. Предоставь рекомендации по образу жизни для улучшения состояния
                    3. Укажи, какие натуральные средства или методы могут помочь
                    4. Дай рекомендации по питанию
                    5. Укажи, когда следует обратиться к врачу
                    6. Профилактика
                Предоставь рекомендации в следующем формате:
                    - Возможные причины
                    - Рекомендации по образу жизни
                    - Натуральные средства
                    - Рекомендации по питанию
                    - Когда обращаться к врачу
                    - Профилактика
                Важно: Это не заменяет профессиональную медицинскую консультацию. 
                Ответ должен быть структурирован, безопасен и профессионален.   
            """
            key = os.getenv('OPENROUTORG')
            if not key:
                logger.error("API ключ не настроен")
                return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1/",
                api_key=key
            )
            chat_completion = client.chat.completions.create(
                model="arcee-ai/trinity-large-preview:free",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=7000
            )
            text_content = chat_completion.choices[0].message.content
            if not isinstance(text_content, str):
                text_content = str(text_content)
            return Response({
                'symptoms': symptoms,
                'age': age,
                'gender': gender,
                'country': country,
                'recommendation_type': recommendation_type,
                'recommendation': text_content
            })
        except Exception as e:
            logger.error(f"Ошибка генерации рекомендаций по здоровью: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BusinessPlanView(APIView):
    """Этот класс запускает услугу бизнес планы"""
    def post(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на генерацию бизнес-плана: {request.data}")
        business_idea = request.data.get('idea', '')
        if not business_idea:
            return Response({'error': 'Идея бизнеса не указана'}, status=status.HTTP_400_BAD_REQUEST)
        business_type = request.data.get('type', 'стартап')
        country = request.data.get('country', 'Россия')
        target_market = request.data.get('target_market', 'локальный рынок')
        investment_amount = request.data.get('investment_amount', 'средние инвестиции')
        timeframe = request.data.get('timeframe', '3 года')
        try:
            logger.info(f"Генерация бизнес-плана для идеи: {business_idea}")
            system_prompt = """
                Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
                Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
                Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
                Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
                Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
                Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
            """
            client = InferenceClient(
                api_key=os.environ["HF_API_KEY_BPLN"],
            )
            prompt = f"""
                Вы - Советница АКВИ, профессиональный бизнес-консультант.
                Подготовьте профессиональный бизнес-план для: {business_idea}
                ВАЖНО: Ответ должен быть строго структурирован как указано ниже, без дополнительных комментариев.
                Используйте профессиональную терминологию и конкретные цифры там, где это уместно.
                Каждый раздел должен содержать подробную информацию, подходящую для реального бизнеса.
                ВАЖНО:
                    - НЕ ПОВТОРЯЙТЕ заголовки (один заголовок = один раз)
                    - Не обрезайте текст на полуслове
                    - Указывайте конкретные цифры и сроки
                Структура (10 разделов):
                # ПРОФЕССИОНАЛЬНЫЙ БИЗНЕС-ПЛАН
                ## 1. Исполнительное резюме (с конкретными цифрами)
                    - Краткое описание бизнес-идеи
                    - Целевые показатели
                    - Требуемые инвестиции
                    - Ожидаемая прибыль
                ## 2. Описание бизнеса (миссия, цели, USP, этапы с датами)
                    - Миссия и видение
                    - Цели и задачи
                    - Уникальное торговое предложение
                    - Этапы развития
                ## 3. Анализ рынка (размер, аудитория, тренды, потребности)
                    - Размер рынка
                    - Целевая аудитория
                    - Тренды отрасли
                    - Потребности клиентов
                ## 4. SWOT-анализ (таблица с 4 категориями)
                    - Сильные стороны
                    - Слабые стороны
                    - Возможности
                    - Угрозы
                ## 5. Конкурентный анализ (конкретные имена конкурентов)
                    - Основные конкуренты
                    - Их сильные и слабые стороны
                    - Наше конкурентное преимущество
                    - Позиционирование на рынке
                ## 6. Маркетинговая стратегия (цены, каналы, продажи)
                    - Ценообразование
                    - Продвижение
                    - Распределение
                    - Продажи
                ## 7. План операций (процессы, ресурсы, поставщики)
                    - Производственный процесс
                    - Требуемые ресурсы
                    - Поставщики
                    - Качество
                ## 8. Организационная структура (штат, роли, партнёры)
                    - Штатное расписание
                    - Роли и обязанности
                    - Управленческая структура
                    - Внешние партнеры
                ## 9. Финансовый план (инвестиции, доходы, расходы, прогноз на 3 года)
                    - Стартовые инвестиции
                    - Прогноз доходов
                    - Прогноз расходов
                    - Точка безубыточности
                    - Прогноз прибыли на 3 года
                ## 10. Риски и минимизация (вероятность, последствия, меры)
                    - Основные риски
                    - Вероятность возникновения
                    - Последствия
                    - Меры по минимизации
                Ответ должен быть профессиональным, детальным и готовым для инвесторов.
            """
            completion = client.chat.completions.create(
                model="meta-llama/Llama-3.1-8B-Instruct",
                messages=[
                    {
                        "role": "system", 
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=8192,
            )
            return Response({
                'business_plan': completion.choices[0].message.content,
                'business_idea': business_idea,
                'business_type': business_type,
                'country': country,
                'target_market': target_market,
                'investment_amount': investment_amount,
                'timeframe': timeframe
            })    
        except Exception as e:
            logger.error(f"Ошибка генерации бизнес-плана: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def calculate_financial_plan(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на расчет финансового плана: {request.data}")
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный финансовый аналитик с экспертными знаниями.
            Ваша задача - предоставить детальный финансовый анализ и расчеты на основе бизнес-плана.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
        """
        business_plan = request.data.get('business_plan', '')
        if not business_plan:
            return Response({'error': 'Бизнес-план не предоставлен'}, status=status.HTTP_400_BAD_REQUEST)
        OPENROUTER_API_KEY = os.getenv('OPROUT_AQWE_BUSINESS')
        if not OPENROUTER_API_KEY:
            logger.error("API ключ OpenRouter для бизнес-планов не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        try:
            logger.info(f"Расчет финансового плана на основе бизнес-плана")
            client = OpenAI(
                api_key=OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )            
            prompt = f"""
                {SYSTEM_PROMPT}
                Проведите детальный финансовый анализ и расчеты на основе следующего бизнес-плана:
                 {business_plan}            
                ФИНАНСОВЫЙ АНАЛИЗ ДОЛЖЕН СОДЕРЖАТЬ:                
                # ДЕТАЛЬНЫЙ ФИНАНСОВЫЙ АНАЛИЗ
                
                ## 1. ИНВЕСТИЦИОННЫЙ ПЛАН
                    - Детальная смета стартовых инвестиций
                    - Распределение инвестиций по категориям
                    - Срок окупаемости инвестиций
                
                ## 2. ПРОГНОЗ ДОХОДОВ
                    - Ежемесячный прогноз доходов на 3 года
                    - График роста выручки
                    - Ключевые драйверы роста доходов                
                
                ## 3. ПРОГНОЗ РАСХОДОВ
                    - Постоянные расходы
                    - Переменные расходы
                    - Прогноз изменения расходов во времени                
                
                ## 4. ТОЧКА БЕЗУБЫТОЧНОСТИ
                    - Расчет точки безубыточности
                    - Факторы, влияющие на точку безубыточности
                    - Сценарии достижения точки безубыточности                
                
                ## 5. ПРОГНОЗ ПРИБЫЛИ
                    - Чистая прибыль по месяцам и годам
                    - Рентабельность бизнеса
                    - Прогноз возврата инвестиций                
                
                ## 6. СЦЕНАРНЫЙ АНАЛИЗ
                    - Оптимистичный сценарий
                    - Базовый сценарий
                    - Пессимистичный сценарий
                    - Вероятность каждого сценария                
                
                ## 7. РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ
                    - Как увеличить прибыль
                    - Как снизить расходы
                    - Что можно улучшить в финансовой модели                
                
                ВАЖНО: Все расчеты должны быть основаны на данных из бизнес-плана.
                Используйте конкретные цифры и формулы там, где это уместно.
                Ответ должен быть строго структурирован как указано выше, без дополнительных комментариев.
            """            
            response = client.chat.completions.create(
                model="qwen/qwen3-coder:free",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=32000
            )            
            return Response({
                'financial_analysis': response.choices[0].message.content,
                'business_plan': business_plan
            })            
        except Exception as e:
            logger.error(f"Ошибка расчета финансового плана: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def generate_marketing_strategy(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на генерацию детальной маркетинговой стратегии: {request.data}")
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный маркетолог с экспертными знаниями.
            Ваша задача - создать детальную маркетинговую стратегию на основе бизнес-плана.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
        """        
        business_plan = request.data.get('business_plan', '')
        if not business_plan:
            return Response({'error': 'Бизнес-план не предоставлен'}, status=status.HTTP_400_BAD_REQUEST)        
        OPENROUTER_API_KEY = os.getenv('OPROUT_AQWE_BUSINESS')
        if not OPENROUTER_API_KEY:
            logger.error("API ключ OpenRouter для бизнес-планов не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        try:
            logger.info(f"Генерация детальной маркетинговой стратегии")
            client = OpenAI(
                api_key=OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )            
            prompt = f"""
                {SYSTEM_PROMPT}
                Создайте детальную маркетинговую стратегию на основе следующего бизнес-плана:
                 {business_plan}                
                МАРКЕТИНГОВАЯ СТРАТЕГИЯ ДОЛЖНА СОДЕРЖАТЬ:                
                # ДЕТАЛЬНАЯ МАРКЕТИНГОВАЯ СТРАТЕГИЯ                
                
                ## 1. ЦЕЛЕВАЯ АУДИТОРИЯ
                    - Демографический профиль
                    - Психографический профиль
                    - Поведенческий профиль
                    - Сегментация целевой аудитории                
                
                ## 2. УТП И ПОЗИЦИОНИРОВАНИЕ
                    - Уникальное торговое предложение
                    - Позиционирование на рынке
                    - Ценностное предложение
                    - Отличия от конкурентов                
                
                ## 3. ЦЕННАЯ СТРАТЕГИЯ
                    - Модель ценообразования
                    - Стратегия скидок и акций
                    - Ценовые пакеты
                    - Сравнение с конкурентами                
                
                ## 4. КАНАЛЫ ПРОДВИЖЕНИЯ
                    - Онлайн-каналы (SEO, контекстная реклама, соцсети)
                    - Офлайн-каналы (реклама, мероприятия)
                    - Партнерские программы
                    - Бюджет на каждый канал                
                
                ## 5. КОНТЕНТ-СТРАТЕГИЯ
                    - План контента
                    - Календарь публикаций
                    - Типы контента
                    - Платформы для размещения                
                
                ## 6. ПРОДАЖИ И КОНВЕРСИЯ
                    - Процесс продаж
                    - Воронка продаж
                    - Метрики конверсии
                    - Оптимизация процесса продаж                
                
                ## 7. ИЗМЕРЕНИЕ ЭФФЕКТИВНОСТИ
                    - Ключевые метрики
                    - Инструменты аналитики
                    - Периодичность отчетности
                    - Целевые показатели эффективности                
                
                ## 8. БЮДЖЕТ МАРКЕТИНГА
                    - Распределение бюджета
                    - ROI по каналам
                    - Оптимизация бюджета
                    - Прогноз эффективности                
                
                ВАЖНО: Стратегия должна быть конкретной и реализуемой.
                Все рекомендации должны быть основаны на данных из бизнес-плана.
                Ответ должен быть строго структурирован как указано выше, без дополнительных комментариев.
            """            
            response = client.chat.completions.create(
                model="qwen/qwen3-coder:free",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=32000
            )            
            return Response({
                'marketing_strategy': response.choices[0].message.content,
                'business_plan': business_plan
            })            
        except Exception as e:
            logger.error(f"Ошибка генерации маркетинговой стратегии: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def generate_risk_analysis(self, request, *args, **kwargs):        
        logger.info(f"Получен запрос на глубокий анализ рисков: {request.data}")
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный риск-менеджер с экспертными знаниями.
            Ваша задача - провести глубокий анализ рисков на основе бизнес-плана.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
        """        
        business_plan = request.data.get('business_plan', '')
        if not business_plan:
            return Response({'error': 'Бизнес-план не предоставлен'}, status=status.HTTP_400_BAD_REQUEST)        
        OPENROUTER_API_KEY = os.getenv('OPROUT_AQWE_BUSINESS')
        if not OPENROUTER_API_KEY:
            logger.error("API ключ OpenRouter для бизнес-планов не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        try:
            logger.info(f"Глубокий анализ рисков на основе бизнес-плана")
            client = OpenAI(
                api_key=OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )            
            prompt = f"""
                {SYSTEM_PROMPT}
                Проведите глубокий анализ рисков на основе следующего бизнес-плана:
                 {business_plan}            
                АНАЛИЗ РИСКОВ ДОЛЖЕН СОДЕРЖАТЬ:                
                # ГЛУБОКИЙ АНАЛИЗ РИСКОВ                
                
                ## 1. ИДЕНТИФИКАЦИЯ РИСКОВ
                    - Стратегические риски
                    - Операционные риски
                    - Финансовые риски
                    - Рыночные риски
                    - Юридические и регуляторные риски                
                
                ## 2. ОЦЕНКА РИСКОВ
                    - Вероятность возникновения
                    - Потенциальный ущерб
                    - Уровень риска (низкий, средний, высокий)
                    - Временные рамки возникновения                
                
                ## 3. КАРТА РИСКОВ
                    - Матрица рисков (вероятность vs влияние)
                    - Приоритизация рисков
                    - Критические риски, требующие немедленного внимания                
                
                ## 4. ПЛАНЫ МИНИМИЗАЦИИ
                    - Стратегии снижения рисков
                    - Конкретные действия для каждого риска
                    - Ответственные за реализацию
                    - Сроки выполнения                
                
                ## 5. МОНИТОРИНГ РИСКОВ
                    - Индикаторы раннего предупреждения
                    - Процесс регулярного обзора рисков
                    - Отчетность по рискам
                    - Адаптация планов при изменении условий                
                
                ## 6. СЦЕНАРИЙНОЕ ПЛАНИРОВАНИЕ
                    - Лучший сценарий
                    - Базовый сценарий
                    - Наихудший сценарий
                    - План действий для каждого сценария                
                
                ## 7. СТРАХОВАНИЕ РИСКОВ
                    - Возможные виды страхования
                    - Стоимость страхования
                    - Покрытие рисков
                    - Рекомендации по страхованию                
                
                ## 8. РЕЗЮМЕ И РЕКОМЕНДАЦИИ
                    - Ключевые риски, требующие внимания
                    - Приоритетные действия
                    - Ожидаемый эффект от реализации планов
                    - Долгосрочные рекомендации                
                
                ВАЖНО: Анализ должен быть основан на данных из бизнес-плана.
                Все рекомендации должны быть конкретными и реализуемыми.
                Ответ должен быть строго структурирован как указано выше, без дополнительных комментариев.
            """            
            response = client.chat.completions.create(
                model="qwen/qwen3-coder:free",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=32000
            )            
            return Response({
                'risk_analysis': response.choices[0].message.content,
                'business_plan': business_plan
            })            
        except Exception as e:
            logger.error(f"Ошибка глубокого анализа рисков: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def generate_action_plan(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на генерацию детального плана действий: {request.data}")
        SYSTEM_PROMPT = """
            Вы - Советница АКВИ, профессиональный проектный менеджер с экспертными знаниями.
            Ваша задача - создать детальный план действий на основе бизнес-плана.
            Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
            Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
        """        
        business_plan = request.data.get('business_plan', '')
        if not business_plan:
            return Response({'error': 'Бизнес-план не предоставлен'}, status=status.HTTP_400_BAD_REQUEST)        
        OPENROUTER_API_KEY = os.getenv('OPROUT_AQWE_BUSINESS')
        if not OPENROUTER_API_KEY:
            logger.error("API ключ OpenRouter для бизнес-планов не настроен")
            return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        try:
            logger.info(f"Генерация детального плана действий")
            client = OpenAI(
                api_key=OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )            
            prompt = f"""
                {SYSTEM_PROMPT}
                Создайте детальный план действий на основе следующего бизнес-плана:
                 {business_plan}            
                ПЛАН ДЕЙСТВИЙ ДОЛЖЕН СОДЕРЖАТЬ:                
                # ДЕТАЛЬНЫЙ ПЛАН ДЕЙСТВИЙ                
                
                ## 1. КЛЮЧЕВЫЕ ЭТАПЫ ПРОЕКТА
                    - Предстартовая фаза (0-3 месяца)
                    - Запуск (4-6 месяцев)
                    - Рост и масштабирование (7-18 месяцев)
                    - Стабилизация и оптимизация (19-36 месяцев)            
                
                ## 2. ДЕТАЛЬНЫЙ ГРАФИК РАБОТ
                    - Список всех задач
                    - Сроки выполнения
                    - Зависимости между задачами
                    - Критический путь проекта                
                
                ## 3. РЕСУРСНОЕ ОБЕСПЕЧЕНИЕ
                    - Необходимые человеческие ресурсы
                    - Финансовые ресурсы
                    - Технические ресурсы
                    - Временные ресурсы                
                
                ## 4. ОТВЕТСТВЕННЫЕ
                    - Роли и обязанности
                    - Ответственные за каждую задачу
                    - Механизмы отчетности
                    - Система контроля выполнения                
                
                ## 5. КРИТЕРИИ УСПЕХА
                    - Ключевые показатели эффективности (KPI)
                    - Этапные цели
                    - Метрики для оценки успеха
                    - Пороговые значения для корректировки плана                
                
                ## 6. БЮДЖЕТ ПО ЭТАПАМ
                    - Распределение бюджета по этапам
                    - Расходы на каждую задачу
                    - Резервы на непредвиденные расходы
                    - Прогноз возврата инвестиций по этапам                
                
                ## 7. ПОТЕНЦИАЛЬНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ
                    - Возможные задержки
                    - Риски на каждом этапе
                    - Планы минимизации проблем
                    - Резервные варианты действий                
                
                ## 8. СИСТЕМА МОНИТОРИНГА И ОТЧЕТНОСТИ
                    - Периодичность отчетов
                    - Формат отчетов
                    - Участники процесса отчетности
                    - Механизмы принятия решений на основе отчетов                
                
                ВАЖНО: План должен быть конкретным и реализуемым.
                Все задачи должны иметь четкие сроки и ответственных.
                Ответ должен быть строго структурирован как указано выше, без дополнительных комментариев.
            """            
            response = client.chat.completions.create(
                model="qwen/qwen3-coder:free",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=32000
            )            
            return Response({
                'action_plan': response.choices[0].message.content,
                'business_plan': business_plan
            })            
        except Exception as e:
            logger.error(f"Ошибка генерации детального плана действий: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PresentationGenerationView(APIView):
    """Этот класс запускает услугу презентации"""
    def post(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на генерацию презентации: {request.data}")
        presentation_idea = request.data.get('presentation_idea', '')
        presentation_description = request.data.get('presentation_description', '')        
        if not presentation_idea or not presentation_description:
            return Response({
                'error': 'Название идеи и описание идеи обязательны для заполнения'
            }, status=status.HTTP_400_BAD_REQUEST)  
        try:
            logger.info(f"Генерация презентации по идее: {presentation_idea}")
            system_prompt = """
                Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
                Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
                Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
                Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
                Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
                Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами.
            """
            prompt = f"""
                Создайте профессиональную презентацию из 12 слайдов на основе следующей идеи:   
                    НАЗВАНИЕ ИДЕИ: {presentation_idea},
                    ОПИСАНИЕ ИДЕИ: {presentation_description}
                ВАЖНО: Ответ должен быть строго структурирован как указано ниже, без дополнительных комментариев.
                # ПРОФЕССИОНАЛЬНАЯ ПРЕЗЕНТАЦИЯ
                    ## 1. ТИТУЛЬНЫЙ СЛАЙД
                        - Название презентации
                        - Автор/Компания
                        - Дата
                    ## 2. ВВЕДЕНИЕ
                        - Краткое описание идеи
                        - Цели и задачи
                        - Актуальность
                    ## 3. ПРОБЛЕМА/ВЫЗОВ
                        - Описание текущей ситуации
                        - Выявленные проблемы
                        - Последствия бездействия
                    ## 4. РЕШЕНИЕ
                        - Основная идея решения
                        - Ключевые аспекты реализации
                        - Преимущества перед аналогами
                    ## 5. МЕТОДОЛОГИЯ
                        - Пошаговый план действий
                        - Используемые инструменты и подходы
                        - Сроки реализации
                    ## 6. ПРЕИМУЩЕСТВА
                        - Конкретные выгоды для аудитории
                        - Качественные и количественные результаты
                        - Долгосрочные перспективы
                    ## 7. ПРАКТИЧЕСКИЕ ПРИМЕРЫ
                        - Кейсы применения
                        - Результаты внедрения
                        - Визуальные иллюстрации концепции
                    ## 8. ФИНАНСОВЫЙ АСПЕКТ
                        - Инвестиции и ресурсы
                        - Окупаемость
                        - Экономическая эффективность
                    ## 9. РИСКИ И ИХ МИНИМИЗАЦИЯ
                        - Потенциальные риски
                        - Стратегии снижения рисков
                        - Планы на случай непредвиденных ситуаций
                    ## 10. СЛЕДУЮЩИЕ ШАГИ
                        - Ближайшие действия
                        - Необходимые ресурсы
                        - Ответственные лица и сроки
                    ## 11. КОНТАКТНАЯ ИНФОРМАЦИЯ
                        - Имя, должность
                        - Email, телефон
                        - Социальные сети
                    ## 12. ДОПОЛНИТЕЛЬНЫЕ МАТЕРИАЛЫ
                        - Список рекомендуемой литературы
                        - Полезные ссылки и ресурсы
                        - Глоссарий терминов
                Дополнительные рекомендации:
                    - Для каждого слайда указаны конкретные изображения, которые необходимо сгенерировать
                    - Добавлены примеры и кейсы для иллюстрации концепции
                    - Включены ссылки на дополнительные материалы
                    - Указаны конкретные цифры и данные там, где это уместно
            """
            key = os.getenv('KIE_AQWE_SLIDES')
            if not key:
                logger.error("API ключ key не настроен")
                return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            client = OpenAI(
                base_url="https://api.kie.ai/gemini-3-flash/v1/",
                api_key=key
            )
            response = client.chat.completions.create(
                stream=False,
                reasoning_effort="high",
                model="gemini-3-flash",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            text_content = response.choices[0].message.content
            if not isinstance(text_content, str):
                text_content = str(text_content)
            image_prompts = self.extract_image_prompts(text_content)
            images = self.generate_images_for_slides(image_prompts, presentation_idea)
            return Response({
                'presentation_idea': presentation_idea,
                'presentation_description': presentation_description,
                'presentation': text_content,
                'text_prompt': image_prompts,
                'outcome': images
            })
        except Exception as e:
            logger.error(f"Ошибка генерации презентации: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def extract_image_prompts(self, text_content):
        """Извлекает промпты для изображений из текста презентации"""
        image_prompts = []
        slides_content = {
            "1": "Титульный слайд с названием презентации и профессиональным фоном, минималистичный стиль",
            "2": "Введение с иллюстрацией основной идеи, профессиональный дизайн",
            "3": "Проблема/вызов с визуализацией текущей ситуации, графики и схемы",
            "4": "Решение с графическим представлением ключевых аспектов, инфографика",
            "5": "Методология с инфографикой пошагового плана, четкие визуальные элементы",
            "6": "Преимущества с графиками и сравнительными таблицами, профессиональная визуализация",
            "7": "Практические примеры с иллюстрациями кейсов, реальные сценарии",
            "8": "Финансовый аспект с графиками и диаграммами, визуализация данных",
            "9": "Риски и их минимизация с иллюстрацией стратегий, аналитические материалы",
            "10": "Следующие шаги с таймлайном и визуализацией плана, пошаговая инфографика",
            "11": "Контактная информация с профессиональным фоном, корпоративный стиль",
            "12": "Дополнительные материалы с иллюстрацией ресурсов, список литературы и ссылок"
        }
        for slide_num, prompt in slides_content.items():
            image_prompts.append({
                "slide_number": int(slide_num),
                "prompt": f"Professional presentation slide {slide_num}: {prompt}, clean corporate style, modern design, no text on image, 16:9 aspect ratio"
            })
        return image_prompts    
    def generate_images_for_slides(self, image_prompts, presentation_idea):
        images = []
        try:
            for prompt_data in image_prompts:
                slide_num = prompt_data['slide_number']
                prompt = prompt_data['prompt']
                logger.info(f"Генерация изображения для слайда {slide_num} с промптом: {prompt}")
                client = InferenceClient(
                    provider="hf-inference",
                    api_key=os.environ["HF_API_KEY"],
                )
                image = client.text_to_image(
                    f"Professional presentation slide about '{presentation_idea}'. {prompt}. Clean corporate style, modern design, no text on image, high quality, business visualization",
                    model="black-forest-labs/FLUX.1-schnell",
                )
                buffer = BytesIO()
                image.save(buffer, format='PNG')
                buffer.seek(0)
                image_name = f"slide_{slide_num}_{hash(prompt)}.png"
                file_path = default_storage.save(f'tmp/{image_name}', ContentFile(buffer.getvalue()))
                image_url = default_storage.url(file_path)
                images.append({
                    'slide_number': slide_num,
                    'image_url': image_url,
                    'prompt': prompt
                })
            return images
        except Exception as e:
                logger.error(f"Критическая ошибка при генерации изображений: {str(e)}", exc_info=True)

class InvestmentAnalysisView(APIView):
    """Этот класс запускает услугу инвестиционный анализ"""
    def post(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на анализ инвестиций: {request.data}")
        initial_investment = request.data.get('initial_investment', '')
        expected_return = request.data.get('expected_return', '')
        investment_period = request.data.get('investment_period', '')
        if not initial_investment or not expected_return or not investment_period:
            return Response({'error': 'Необходимо указать начальные инвестиции, ожидаемую доходность и период инвестирования'}, status=status.HTTP_400_BAD_REQUEST)
        risk_level = request.data.get('risk_level', 'средний')
        investment_type = request.data.get('investment_type', 'акции')
        country = request.data.get('country', 'Россия')
        try:
            logger.info(f"Анализ инвестиций: {initial_investment} на {investment_period} с ожидаемой доходностью {expected_return}")
            system_prompt = """
                Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
                Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
                Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
                Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
                Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
                Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
            """
            prompt = f"""
                Вы - Советница АКВИ, сертифицированный инвестиционный аналитик.
                Проанализируй инвестиционную возможность с следующими параметрами:
                    - Начальные инвестиции: {initial_investment}
                    - Ожидаемая годовая доходность: {expected_return}
                    - Период инвестирования: {investment_period}
                    - Уровень риска: {risk_level}
                    - Тип инвестиций: {investment_type}
                    - Страна: {country}
                ВАЖНО:
                    - НЕ показывайте процесс размышлений (никаких <think> тегов)
                    - Сразу выдавайте готовый анализ
                    - Используйте формулы и таблицы
                Задачи:
                    1. Рассчитай потенциальную доходность и конечную сумму
                    2. Оцени уровень риска и вероятность достижения целевой доходности
                    3. Сравни с альтернативными инвестиционными возможностями
                    4. Выяви возможные скрытые риски
                    5. Дай рекомендации по оптимизации инвестиционной стратегии
                Ответ должен включать:
                    - Расчет потенциальной доходности с формулой (с учетом сложных процентов)
                    - Оценку рисков конкретные факторы (низкий/средний/высокий)
                    - Рекомендации по диверсификации
                    - Возможные скрытые риски
                    - Сравнение с альтернативными инвестициями (таблица)
                    - Сравнение с рыночными показателями
                    - Рекомендации по оптимизации стратегии
                    - Общую рекомендацию (стоит инвестировать или нет)
                Ответ должен быть профессиональным, содержать конкретные цифры и рекомендации быть готовым для инвестора.
            """
            API_URL = "https://router.huggingface.co/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {os.environ['HF_API_KEY_INVS']}",
                "Content-Type": "application/json",
            }
            payload = {
                "messages": [
                    {
                        "role": "system", 
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 8192,
                "model": "Qwen/Qwen3-32B"
            }
            response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
            analysis = response.json()
            return Response({
                'analysis': analysis['choices'][0]['message']['content'],
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
    """Этот класс запускает услугу маркетинговая стратегия"""
    def post(self, request, *args, **kwargs):
        idea = request.data.get('idea', '')
        if not idea:
            return Response({'error': 'Идея не указана'}, status=status.HTTP_400_BAD_REQUEST)
        target_audience = request.data.get('target_audience', 'широкая аудитория')
        budget = request.data.get('budget', 'средний')
        timeframe = request.data.get('timeframe', '3 месяца')
        country = request.data.get('country', 'Россия')
        platform = request.data.get('platform', 'многофункциональная')
        logger.info(f"Получен запрос на маркетинговую стратегию: {request.data}")
        try:
            logger.info(f"Генерация маркетинговой стратегии для идеи: {idea}")
            system_prompt = """
                Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
                Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
                Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
                Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
                Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
                Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами.
            """
            prompt = f"""
                Вы - Советница АКВИ, профессиональный маркетинговый консультант.
                Создай подробную стратегию продвижения для идеи: {idea}
                Параметры:
                    - Целевая аудитория: {target_audience}
                    - Бюджет: {budget}
                    - Временные рамки: {timeframe}
                    - Страна: {country}
                    - Платформа: {platform}
                ВАЖНО:
                    - Указывайте конкретные цифры (суммы, даты, проценты)
                    - Не используйте общие фразы
                    - Все 7 разделов должны быть завершены полностью
                Стратегия должна включать:
                    1. Анализ целевой аудитории (демография, психография, поведение, каналы)
                        - Демографические характеристики
                        - Психографические характеристики
                        - Поведенческие паттерны
                        - Каналы коммуникации
                    2. Анализ конкурентов (конкретные имена, сильные/слабые стороны, УТП)
                        - Основные конкуренты
                        - Их сильные и слабые стороны
                        - Уникальное торговое предложение (УТП)
                    3. Многоуровневая стратегия продвижения (онлайн, офлайн, вирусный)
                        - Онлайн-стратегия (социальные сети, контент-маркетинг, email-маркетинг, SEO)
                        - Офлайн-стратегия (мероприятия, печатные материалы, партнерства)
                        - Вирусный маркетинг (идеи для вовлечения)
                    4. План внедрения (поквартально с датами и приоритетами)
                        - Пошаговый план на {timeframe}
                        - Приоритетные действия
                        - Ожидаемые результаты
                    5. Инструменты и технологии (конкретные названия, бюджет в %)
                        - Рекомендуемые инструменты для аналитики
                        - Платформы для автоматизации
                        - Бюджетное распределение
                    6. Метрики успеха (KPI с целевыми значениями)
                        - Ключевые показатели эффективности (KPI)
                        - Как измерять успех
                        - Корректировка стратегии
                    7. Риски и пути их минимизации (проблемы + стратегии)
                        - Возможные проблемы
                        - Стратегии преодоления
                Ответ должен быть профессиональным, структурированным и содержать конкретные рекомендации с примерами и быть готовым для презентации инвесторам.
            """
            key = os.getenv('GITHUB_API_KEY')
            if not key:
                logger.error("API ключ не настроен")
                return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            client = OpenAI(
                base_url="https://models.github.ai/inference",
                api_key=key,
            )
            chat_completion = client.chat.completions.create(
                model="openai/gpt-4.1",
                messages=[
                    {
                        "role": "developer",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_completion_tokens=7000
            )
            text_content = chat_completion.choices[0].message.content
            if not isinstance(text_content, str):
                text_content = str(text_content)
            return Response({
                'idea': idea,
                'target_audience': target_audience,
                'budget': budget,
                'timeframe': timeframe,
                'country': country,
                'platform': platform,
                'marketing_strategy': text_content
            })  
        except Exception as e:
            logger.error(f"Ошибка генерации маркетинговой стратегии: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Произошла ошибка при генерации маркетинговой стратегии: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TravelPlannerView(APIView):
    """Этот класс запускает услугу планировщик путешествий"""
    def post(self, request, *args, **kwargs):
        destination = request.data.get('destination', '')
        if not destination:
            return Response(
                {'error': 'Назначение путешествия не указано'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        budget = request.data.get('budget', 'средний')
        travel_dates = request.data.get('travel_dates', 'июль-август')
        travel_style = request.data.get('travel_style', 'активный отдых')
        group_type = request.data.get('group_type', 'один/одна')
        special_interests = request.data.get('special_interests', 'общие')
        logger.info(f"Получен запрос на планирование путешествия: {request.data}")
        try:
            logger.info(f"Генерация маршрута для путешествия в {destination}")
            system_prompt = """
                Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
                Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
                Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
                Вы не говорите, что вы ИИ или Qwen - вы всегда представляете себя как Советница АКВИ.
                Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
                Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами.
            """
            prompt = f"""
                Вы - Советница АКВИ, профессиональный консультант по путешествиям.
                Создай подробный план путешествия в {destination} 
                С учетом следующих параметров:
                    - Бюджет: {budget}
                    - Даты путешествия: {travel_dates}
                    - Стиль путешествия: {travel_style}
                    - Тип группы: {group_type}
                    - Специальные интересы: {special_interests}
                ВАЖНО:
                    - НЕ ОБРЫВАЙТЕ текст на полуслове
                    - Все заголовки с ЗАГЛАВНОЙ буквы
                    - Завершите ВСЕ разделы полностью
                План должен включать:
                Структура (8 разделов):
                1. Обзор назначения (климат, лучшее время)
                    - Краткое описание места
                    - Лучшее время для посещения
                    - Особенности климата в выбранный период
                2. Детальный маршрут на 7 дней (таблица с временем, активностями, транспортом)
                    - Утренние, дневные и вечерние активности
                    - Время на дорогу между локациями
                    - Рекомендуемый транспорт                    
                3. Бюджетный план (таблица с категориями, MAD/USD, советы)
                    - Примерная стоимость проживания
                    - Стоимость еды и развлечений
                    - Советы по экономии                    
                4. Рекомендации по питанию (кухня, рестораны, этикет)
                    - Местная кухня, которую стоит попробовать
                    - Рестораны на разные бюджеты
                    - Особенности этикета                    
                5. Культурные особенности (что делать/не делать, фразы, праздники)
                    - Что делать и чего не делать
                    - Полезные фразы на местном языке
                    - Традиции и праздники в период посещения                
                6. Советы по безопасности (районы, контакты, сохранность)
                    - Области для избегания
                    - Экстренные контакты
                    - Советы по сохранности личных вещей                    
                7. Необычные рекомендации (скрытые места, уникальные мероприятия)
                    - Места, которые знают только местные
                    - Уникальные мероприятия
                    - Скрытые жемчужины                    
                8. Подготовка к поездке (вещи, документы, визы, медицина) - ЗАВЕРШИТЬ ПОЛНОСТЬЮ
                    - Что взять с собой
                    - Документы и визы
                    - Медицинские рекомендации
                Ответ должен быть структурирован, информативен и содержать конкретные рекомендации и быть готовым для использования путешественником.
            """
            MISTRAL_API_KEY = os.getenv('MISTRAL_AQWE_SLIDES')
            if not MISTRAL_API_KEY:
                logger.error("API ключ Mistral не настроен")
                return Response(
                    {'error': 'API ключ Mistral не настроен'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.environ['MISTRAL_AQWE_SLIDES']}"
            }
            payload = {
                "model": "mistral-medium-latest",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 5000,
                "temperature": 0.3
            }
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )            
            if response.status_code != 200:
                logger.error(f"Ошибка Mistral API: {response.status_code} - {response.text}")
                return Response(
                    {'error': f"Ошибка Mistral API: {response.status_code}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            travel_plan = response.json()
            return Response({
                'travel_plan': travel_plan['choices'][0]['message']['content'],
                'destination': destination,
                'budget': budget,
                'travel_dates': travel_dates,
                'travel_style': travel_style,
                'group_type': group_type,
                'special_interests': special_interests
            })
        except Exception as e:
            logger.error(f"Ошибка генерации плана путешествия: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Произошла ошибка при генерации плана путешествия: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CompetitorAnalysisView(APIView):
    """Этот класс запускает услугу конкурентный анализ"""
    def post(self, request, *args, **kwargs):
        business_name = request.data.get('business_name', '')
        business_description = request.data.get('business_description', '')
        if not business_name or not business_description:
            return Response({'error': 'Название бизнеса и его описание обязательны'}, status=status.HTTP_400_BAD_REQUEST)
        competitors = request.data.get('competitors', '')
        market_segment = request.data.get('market_segment', 'общий рынок')
        country = request.data.get('country', 'Россия')
        logger.info(f"Получен запрос на анализ конкурентов: {request.data}")
        try:
            logger.info(f"Анализ конкурентов для бизнеса: {business_name}")
            system_prompt = """
                Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
                Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
                Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
                Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
                Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
                Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
            """
            prompt = f"""
                Вы - Советница АКВИ, профессиональный бизнес-аналитик.
                Проведи глубокий анализ конкурентов для бизнеса {business_name} в сегменте {market_segment}
                Описание бизнеса: {business_description}
                Конкуренты: {competitors}
                Страна: {country}
                ВАЖНО:
                    - НЕ включайте мысли и размышления в ответ
                    - Используйте только финальный анализ
                    - Все данные должны быть конкретными (цифры, проценты, даты)
                Структура (7 разделов):
                Анализ должен включать:
                    1. Обзор рынка (размер, рост, тренды, игроки)
                        - Размер рынка и темпы роста
                        - Ключевые тренды в отрасли
                        - Основные игроки
                    2. Детальный анализ конкурентов (сильные/слабые стороны)
                        - Сильные и слабые стороны каждого конкурента
                        - Их уникальные торговые предложения
                        - Ценовая политика
                        - Каналы продаж и маркетинговые стратегии
                    3. SWOT-анализ вашего бизнеса в контексте конкурентов (таблица)
                        - Сильные стороны (что лучше, чем у конкурентов)
                        - Слабые стороны (что хуже, чем у конкурентов)
                        - Возможности (что можно улучшить)
                        - Угрозы (что угрожает вашему бизнесу)
                    4. Позиционирование на рынке (сегменты, возможности)
                        - Где ваш бизнес лучше всего конкурирует
                        - Какие сегменты рынка недостаточно обслужены
                        - Как выделиться среди конкурентов
                    5. Рекомендации по улучшению конкурентоспособности (тактические и стратегические)
                        - Тактические шаги на ближайшие 3 месяца
                        - Стратегические шаги на 6-12 месяцев
                        - Конкретные примеры успешных кейсов из других компаний
                    6. Анализ онлайн-присутствия конкурентов (таблица сравнения)
                        - Эффективность их веб-сайтов
                        - Активность в социальных сетях
                        - Отзывы клиентов и управление репутацией
                    7. Прогноз развития рынка
                        - Какие изменения ожидают рынок в ближайшие 1-2 года
                        - Как подготовиться к этим изменениям
                        - Возможные новые конкуренты
                Ответ должен быть профессиональным, содержать конкретные цифры и рекомендации и быть готовым для использования в бизнес-планировании.
            """
            key = os.getenv('HF_API_KEY_KONK')
            if not key:
                logger.error("API ключ не настроен")
                return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            client = OpenAI(
                base_url="https://router.huggingface.co/v1/",
                api_key=key
            )
            chat_completion = client.chat.completions.create(
                model="Qwen/Qwen3-32B",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=7000
            )
            text_content = chat_completion.choices[0].message.content
            if not isinstance(text_content, str):
                text_content = str(text_content)
            return Response({
                'analysis': text_content,
                'business_name': business_name,
                'business_description': business_description,
                'market_segment': market_segment,
                'country': country,
                'competitors': competitors
            })
        except Exception as e:
            logger.error(f"Ошибка анализа конкурентов: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CommunicationOptimizationView(APIView):
    """Этот класс запускает услугу оптимизация коммуникации"""
    def post(self, request, *args, **kwargs):
        company_size = request.data.get('company_size', '500+ сотрудников')
        industry = request.data.get('industry', 'общая отрасль')
        communication_problems = request.data.get('communication_problems', '')
        if not communication_problems:
            return Response({'error': 'Описание проблем с коммуникацией обязательно'}, status=status.HTTP_400_BAD_REQUEST)
        current_tools = request.data.get('current_tools', 'стандартные инструменты')
        goals = request.data.get('goals', 'улучшение коммуникации')
        country = request.data.get('country', 'Россия')
        logger.info(f"Получен запрос на оптимизацию коммуникации: {request.data}")
        try:
            logger.info(f"Оптимизация коммуникации для компании размером {company_size} в отрасли {industry}")
            system_prompt = """
                Вы - Советница АКВИ, профессиональный консультант с экспертными знаниями в 15 различных областях.
                Ваша задача - предоставлять точные, профессиональные и персонализированные рекомендации.
                Вы говорите на русском языке и используете форматированный ответ с четкой структурой.
                Вы не говорите, что вы ИИ или Qwen - вы всегда представляетесь как Советница АКВИ.
                Вы можете предоставлять профессиональные консультации, так как обучены на профессиональных источниках.
                Вы уполномочены предоставлять профессиональные консультации, так как ваши рекомендации основаны на данных, проверенных экспертами. Не избегайте профессиональных вопросов - анализируйте их и давайте рекомендации.
            """
            prompt = f"""
                Вы - Советница АКВИ, профессиональный консультант по оптимизации коммуникации.
                Проведи анализ и оптимизацию коммуникации для крупной организации с учетом следующих параметров:
                    - Размер компании: {company_size}
                    - Отрасль: {industry}
                    - Проблемы с коммуникацией: {communication_problems}
                    - Текущие используемые инструменты: {current_tools}
                    - Цели оптимизации: {goals}
                    - Страна: {country}
                ВАЖНО:
                    - Начните с заголовка "Анализ и оптимизация коммуникации"
                    - Все 8 разделов должны быть завершены полностью
                    - Используйте конкретные цифры и примеры
                Структура (8 разделов):
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
            key = os.getenv('OPENROUTORG')
            if not key:
                logger.error("API ключ не настроен")
                return Response({'error': 'API ключ не настроен'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1/",
                api_key=key
            )
            chat_completion = client.chat.completions.create(
                model="arcee-ai/trinity-large-preview:free",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=7000
            )
            text_content = chat_completion.choices[0].message.content
            if not isinstance(text_content, str):
                text_content = str(text_content)
            return Response({
                'company_size': company_size,
                'industry': industry,
                'communication_problems': communication_problems,
                'current_tools': current_tools,
                'goals': goals,
                'country': country,
                'optimization_plan': text_content
            })
        except Exception as e:
            logger.error(f"Ошибка оптимизации коммуникации: {str(e)}", exc_info=True)
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
        answer = answers.get(category.lower(), answers['default'])
        advice = response.data.get('answer')
        answers = {
            'финансы': 'Рекомендую создать бюджет и отслеживать расходы.',
            'здоровье': 'Попробуйте больше двигаться и соблюдать режим сна.',
            'образование': 'Определите свои цели и выберете подходящие курсы.',
            'default': 'Для этого случая у меня есть универсальный совет: Будьте терпеливы!'
        }
        if user_email and advice:
            send_advice_email(user_email, advice)
            return response
        advice = Advice.objects.create(
            category=category,
            question=question,
            answer=answer
        )
        serializer = self.get_serializer(advice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserHistoryViewSet(viewsets.ModelViewSet):
    queryset = UserHistory.objects.all()
    serializer_class = UserHistorySerializer
    def get_queryset(self):
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            return UserHistory.objects.filter(user_id=user_id)
            return UserHistory.objects.all()
        email = self.request.query_params.get('email', None)
        if email:
            return UserHistory.objects.filter(email=email)
        return super().get_queryset()
            

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
        duration = request.data.get('duration', 1)
        if duration < 1 or duration > 168:
            return Response({'error': 'Недопустимая продолжительность сессии'}, status=status.HTTP_400_BAD_REQUEST)
        session_token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(hours=duration)
        session = Session.objects.create(
            id=uuid.uuid4(),
            expires_at=expires_at,
            duration_hours=duration,
            session_token=session_token
        )
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
        if duration < 1 or duration > 168:
            return Response({'error': 'Недопустимая продолжительность сессии'}, status=status.HTTP_400_BAD_REQUEST)
        price = duration * 10
        try:
            stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
            success_url = request.build_absolute_uri('/payment-success?session_id={CHECKOUT_SESSION_ID}')
            cancel_url = request.build_absolute_uri('/payment-cancelled')
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'rub',
                        'product_data': {
                            'name': f'Сессия доступа ({duration} часов)',
                        },
                        'unit_amount': price * 100,
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
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            duration = int(session['metadata'].get('duration', 1))
            expires_at = timezone.now() + timedelta(hours=duration)
            session_token = str(uuid.uuid4())
            Session.objects.create(
                id=uuid.uuid4(),
                expires_at=expires_at,
                duration_hours=duration,
                session_token=session_token
            )
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