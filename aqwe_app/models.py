from django.db import models

class Advice(models.Model):
    category = models.CharField(max_length=100)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:50]

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
# Create your models here.
