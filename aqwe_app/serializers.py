from rest_framework import serializers
from aqwe_app.models import Advice
from aqwe_app.models import UserHistory

class AdviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advice
        fields = ['id', 'name', 'email', 'category', 'question', 'answer', 'notes', 'created_at']

class UserHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserHistory
        fields = ['user_id', 'advice', 'created_at']