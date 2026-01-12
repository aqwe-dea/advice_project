import uuid
from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, datetime
from django.utils import timezone

class Advice(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    category = models.CharField(max_length=100)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        category = self.category or 'Без категории'
        question = self.question[:50] if self.question else 'Без вопроса'
        return f'{category}: {question}...'

class UserHistory(models.Model):
    user_id = models.CharField(max_length=100)
    advice = models.ForeignKey(Advice, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.user_id} - {self.advice.question[:50]}'
    
class StripeSettings(models.Model):
    public_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    live_mode = models.BooleanField(default=False)
    def __str__(self):
        return "Stripe Settings"

class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    duration_hours = models.IntegerField(default=1)
    session_token = models.CharField(max_length=255, unique=True, null=True, blank=True)
    def __str__(self):
        return f"Session {self.id} - Expires: {self.expires_at}"
    def is_valid(self):
        return self.is_active and self.expires_at > timezone.now()
    def remaining_time(self):
        if not self.is_valid():
            return 0
        return max(0, (self.expires_at - timezone.now()).total_seconds())
# Create your models here.
