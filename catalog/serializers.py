from rest_framework import serializers
from .models import Notification
from .models import Book, Fandom

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['message', 'created_at', 'is_read']





class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class FandomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fandom
        fields = '__all__'
