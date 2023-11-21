from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import Group
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from catalog.models import Book, Chapter
from catalog import models as mod
from django.db.models import Sum, Count
from django.conf import settings
from django.utils import timezone
import uuid  # Для генерации уникальных токенов
import os
from django.utils.translation import gettext_lazy as _




# Функция для генерации токена
def generate_token():
    return str(uuid.uuid4())  # Генерирует случайный уникальный токен


def upload_to(instance, filename):
    # Определение пути загрузки изображения
    if instance.user.username:
        return 'users/profile_images/{}/{}'.format(instance.user.username, filename)
    else:
        return 'users/profile_images/no_image.png'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    username = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    image = models.ImageField(null=True, blank=True, default='users/profile_images/no_image.png', upload_to=upload_to)
    created = models.DateTimeField(auto_now_add=True)
    bookmarks = models.ManyToManyField(Book, through='Bookmark')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_symbols = models.PositiveIntegerField(default=0)
    unread_messages = models.PositiveIntegerField(default=0)
    token = models.CharField(max_length=255, default=generate_token)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Профіль'
        verbose_name_plural = 'Профілі'



    def __str__(self):
        if self.image:
            # Если у пользователя есть изображение, возвращаем строку с именем пользователя и путем к изображению
            return "Id:{}, {}, Image:{}".format(self.id, self.username, self.image.url)

        else:
            # Если у пользователя нет изображения, возвращаем строку только с именем пользователя
            return "Id:{}, {}".format(self.id, self.username)


    def get_absolute_url(self):
        return reverse('profile', kwargs={'pk': self.user.id})

    def total_symbols_count(self):
        # Получаем все главы всех книг пользователя и суммируем длины их содержимого
        total_symbols = Chapter.objects.filter(book__user=self.user).aggregate(
            total_content_length=Sum('content_length'))
        return total_symbols['total_content_length'] or 0

    def calculate_commission_rate(self):
        total_symbols = self.total_symbols_count()
        if total_symbols < 5000:
            return 0.15  # 15%
        elif total_symbols < 10000:
            return 0.12  # 12%
        elif total_symbols >= 50000:
            return 0.05  # 5%
        return 0  # Для всех других случаев, хотя это условие скорее всего не будет выполнено

    def total_activity(self):
        author = User.objects.get(id=self.user_id)
        author_books = Book.objects.filter(user_id=author)
        total_comments = (mod.Comment.objects.
            filter(content_type__model="book").
            filter(object_id__in=author_books).count()
        )
        total_ratings = (mod.Rating.objects.
            filter(book__in=author_books).aggregate(total_likes=Count('stars'))
        )
        total_activity = (total_comments +
        (total_ratings['total_likes'] if total_ratings['total_likes'] else 0))
        return total_activity

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            username=instance.username,
            email=instance.email
        )



class Bookmark(models.Model):
    READ = 'Читаю'
    IN_PLANS = 'В Планах'
    END_READ = 'Прочитав'
    SPECIAL = 'Особливі'
    LEFT = 'Кинув'
    GROUP_CHOICES = [
        (READ , 'Читаю'),
        (IN_PLANS, 'В планах'),
        (END_READ, 'Прочитав'),
        (SPECIAL, 'Особливі'),
        (LEFT, 'Кинув'),
    ]

    user_profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    group = models.CharField(max_length=10, choices=GROUP_CHOICES, default=READ)

    class Meta:
        unique_together = ('user_profile', 'book')



class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

class Dialog(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2')

class Message(models.Model):
    dialog = models.ForeignKey(Dialog, on_delete=models.CASCADE, default=None)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    text = models.TextField(default='')
    date_created = models.DateTimeField(default=timezone.now)


    class Meta:
        ordering = ['date_created']

    def __str__(self):
        return self.message
