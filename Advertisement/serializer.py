from rest_framework import serializers, generics
from datetime import date
from .models import Advertisement



class AdvSerializer(serializers.ModelSerializer):
    active = serializers.BooleanField(default=True, read_only=True)

    class Meta:
        model = Advertisement
        fields = '__all__'
