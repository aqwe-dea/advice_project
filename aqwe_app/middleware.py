from django.utils import timezone
from django.http import JsonResponse
from .models import Session
import logging

logger = logging.getLogger(__name__)

class SessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        session_token = request.COOKIES.get('session_token')
        request.session_valid = False
        request.session_data = None
        if session_token:
            try:
                session = Session.objects.get(session_token=session_token)
                if session.is_valid():
                    request.session_valid = True
                    request.session_data = {
                        'id': str(session.id),
                        'expires_at': session.expires_at,
                        'duration_hours': session.duration_hours,
                        'remaining_time': session.remaining_time()
                    }
                else:
                    # Сессия истекла, но оставляем информацию для уведомления
                    request.session_data = {
                        'id': str(session.id),
                        'expires_at': session.expires_at,
                        'duration_hours': session.duration_hours,
                        'remaining_time': 0
                    }
            except Session.DoesNotExist:
                logger.warning(f"Сессия не найдена: {session_token}")
        response = self.get_response(request)
        # Добавляем заголовок для фронтенда
        if hasattr(request, 'session_valid'):
            response['X-Session-Valid'] = str(request.session_valid).lower()
        return response