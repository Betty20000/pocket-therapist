from rest_framework import serializers
from .models import A2AMessage

class A2AMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = A2AMessage
        fields = "__all__"
