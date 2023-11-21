from django.db import models
from django.contrib.auth.models import User
from catalog.models import Book, Fandom, Genres, Tag
from users.models import Profile

class Advertisement(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    book = models.ForeignKey('catalog.Book', on_delete=models.DO_NOTHING)  # Связь с моделью книги
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=50, blank=True, null=True)
    fandom = models.IntegerField(blank=True, null=True)  # Фендом
    genre = models.IntegerField(blank=True, null=True)   # Жанр
    tag = models.IntegerField(blank=True, null=True)     # Тег
    cost = models.DecimalField(max_digits=10, decimal_places=2)     # Стоимость рекламы
