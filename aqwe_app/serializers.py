from rest_framework import serializers
from aqwe_app.models import Advice
from aqwe_app.models import UserHistory

class AdviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advice
        fields = ['id', 'category', 'question', 'answer', 'created_at']

class UserHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserHistory
        fields = ['user_id', 'advice', 'created_at']