import os
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.core.files import File
from django.urls import reverse
from django.contrib.auth.models import User
from slugify import slugify
from django.db.models import Avg, Sum
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from ckeditor.fields import RichTextField
from django.utils import timezone
from django.db.models.signals import pre_save
from model_utils import FieldTracker
from celery import shared_task
from datetime import timedelta
from celery import current_app
from decimal import *

import logging

logger = logging.getLogger(__name__)


def create_slug(title):
    return slugify(title)


def book_image_path(instance, filename):
    book_name = instance.title
    book_name = book_name.replace(' ', '_')
    book_name = clean_filename(book_name)
    path = f'catalog/image/{book_name}/'
    return os.path.join(path, filename)


def book_directory_path(instance, filename):
    local_cleaned_filename = clean_filename(filename)
    return f'books/{instance.slug}/{local_cleaned_filename}'


def chapter_directory_path(instance, filename):
    local_cleaned_filename = clean_filename(filename)
    return f'chapters\\{local_cleaned_filename}'


def clean_filename(filename):
    invalid_chars = {'/', '\\', '?', '%', '*', ':', '|', '"', '<', '>', '.'}
    for c in invalid_chars:
        filename = filename.replace(c, '')
    return filename


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:tag_detail', args=[str(self.pk)])


class Fandom(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:fandom_detail', args=[str(self.pk)])


class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:country_detail', args=[str(self.pk)])


class Genres(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:genres_detail', args=[str(self.pk)])


def get_reergard_user():
    return User.objects.get(username='Reergard')


class Chapter(models.Model):
    book = models.ForeignKey('catalog.Book', on_delete=models.CASCADE, related_name='book_chapters')
    title = models.CharField(max_length=255)
    content = RichTextField(blank=True, null=True)
    file = models.FileField(upload_to=chapter_directory_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(blank=False, null=False)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)  # Цена главы
    purchased_by = models.ManyToManyField(User, blank=True, related_name="purchased_chapters")
    content_length = models.PositiveIntegerField(default=0)
    chapter_views = models.ManyToManyField(User, blank=True, through='ViewedChapters',
                                       related_name="viewed_chapters")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

        if self.file:
            chapter_file_path = os.path.join(settings.MEDIA_ROOT, 'books', self.book.slug, self.file.name)
            with open(chapter_file_path, 'wb') as f:
                for chunk in self.file.chunks():
                    f.write(chunk)

        content = self.content
        print(content)
        if content != None:
            chapter_file_path = os.path.join(settings.MEDIA_ROOT, 'books', self.book.slug, 'chapters')
            if not os.path.exists(chapter_file_path):
                os.mkdir(chapter_file_path)
            chapter_file_path = os.path.join(settings.MEDIA_ROOT, 'books', self.book.slug, 'chapters', f'{self.book.slug}_{self.slug}')
            with open(chapter_file_path, 'w') as f:
                    f.write(content)



class Book(models.Model):
    TRANSLATING = 'Перекладається'
    COMPLETED = 'Завершено'
    WAITING = 'Очікування нових розділів'
    ABANDONED = 'Покинутий'
    PAUSE = 'Перерва'

    STATUS_CHOICES = [
        (TRANSLATING, 'Перекладається'),
        (COMPLETED, 'Завершено'),
        (WAITING, 'Очікування нових розділів'),
        (ABANDONED, 'Покинутий'),
        (PAUSE, 'Перерва'),
    ]

    id = models.AutoField(primary_key=True)

    user = models.ForeignKey(User, on_delete=models.SET(get_reergard_user), related_name='books')
    title = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, null=True)
    author = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag)
    genres = models.ManyToManyField(Genres)
    fandoms = models.ManyToManyField(Fandom)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to=book_directory_path, blank=True, null=True)
    images = models.ImageField(upload_to=book_directory_path, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    viewed_by = models.ManyToManyField(User, blank=True, through='ViewedBooks',
                                       related_name="viewed_books")  # Связь "многие ко многим" с моделью User, позволяет отслеживать, кто из пользователей просмотрел книгу.
    trending_score = models.IntegerField(default=0)
    pub_date = models.DateField(verbose_name='Дата створення', default=timezone.now)  # Дата створення
    last_updated = models.DateTimeField(default=timezone.now)
    file = models.FileField(upload_to='books/', blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=TRANSLATING)
    notification_sent = models.BooleanField(default=False)
    tracker = FieldTracker(fields=['last_updated'])
    chapters_amount = models.IntegerField(default=0)
    adult_content = models.BooleanField(default=False)
    comments = GenericRelation('catalog.Comment')


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            num = 2
            while Book.objects.filter(slug=self.slug).exists():
                self.slug = "{}-{}".format(slugify(self.title), num)
                num += 1

        if not self.image:
            no_image_path = os.path.join(settings.STATICFILES_DIRS[0], 'catalog/image/no_image.jpg')
            self.image.save('no_image.jpg', File(open(no_image_path, 'rb')))

        if self.pk:
            previous_image = Book.objects.get(pk=self.pk).image
            if self.image != previous_image:
                if previous_image:
                    previous_image_path = os.path.join(settings.MEDIA_ROOT, str(previous_image))
                    if os.path.exists(previous_image_path):
                        os.remove(previous_image_path)

        if self.status == Book.ABANDONED:  # через tasks
            self.last_updated = timezone.now()

        if self.tracker.has_changed('last_updated'):
            self.notification_sent = False


        super().save(*args, **kwargs)

    def avg_rating(self):
        avg = self.book_ratings.all().aggregate(Avg('stars'))
        return round(avg.get('stars__avg') or 0, 2)

    def avg_quality(self):
        avg = self.book_quality.all().aggregate(Avg('stars'))
        return round(avg.get('stars__avg') or 0, 2)

    @property
    def chapters_count(self):  # количество глав
        chapters = self.book_chapters.count()
        return chapters

    def is_adult(self):
        return self.is_adult

    def set_status(self, new_status):
        self.status = new_status
        self.save()

    def update_status_to_abandoned(self):
        if self.status == 'translating':
            self.status = 'abandoned'
            self.status_date = timezone.now()
            self.save()

    def update_last_activity(self):
        self.last_updated = timezone.now()

    def update_status(self, new_status):
        self.status = new_status
        self.save(update_fields=['status'])

def update_trending_score():
    books = Book.objects.all()
    for book in books:
        views_last_week = book.viewed_by.filter(viewedbooks__revision_date__gte=timezone.now() - timedelta(days=7)).count()
        book.trending_score = views_last_week
        book.save()


class ViewedBooks(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    revision_date = models.DateField(verbose_name='Дата перегляду', auto_now_add=True)

class ViewedChapters(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    revision_date = models.DateField(verbose_name='Дата перегляду', auto_now_add=True)

class Income(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    buyer =  models.ForeignKey(User, on_delete=models.CASCADE, related_name="buyer")
    seller =  models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    datetime =  models.DateTimeField(auto_now_add=True)

from users.models import Profile


def get_default_user_profile():

    try:
        default_profile = Profile.objects.get(is_default=True)
        return default_profile
    except Profile.DoesNotExist:
        return None


class Notification(models.Model):
    user_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, default=get_default_user_profile, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message

    # DEBUG !!!!!!!!!!!!!!!
    # def send_abandoned_notification(self):
    #     # Проверяем статус книги и время последнего обновления
    #     book = self.user_profile.books.filter(status=Book.TRANSLATING).first()
    #     if book and book.last_updated < timezone.now() - timedelta(minutes=2):
    #         # Отправляем задачу Celery для отправки уведомления
    #
    #         print("BOOOOOOK ID = " + book.id)
    #         logger.info("BOOOOOOK ID = " + book.id)
    #
    #         with open('C:\\Users\\user\\Desktop\\my_log.txt', 'w') as f:  # думаю тут помилка бо юзер не той
    #             f.write("BOOOOOOK ID = " + book.id)
    #             f.close()
    #         current_app.send_task('catalog.tasks.send_abandoned_notification', args=[book.id]) #


class Rating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.IntegerField(
    validators=[MinValueValidator(1), MaxValueValidator(5)],
    default=None, null=True, blank=True
    )
    timestamp = models.DateTimeField(default=timezone.now)


@receiver(post_save, sender=Rating)
def update_book_avg_rating(sender, instance, **kwargs):
    instance.book.save()  # будет вызван метод save книги, который обновит средний рейтинг

class Quality(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_quality')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=None, null=True,
                                blank=True)


@receiver(post_save, sender=Quality)
def update_book_avg_quality(sender, instance, **kwargs):
    instance.book.save()

class Comment(models.Model):
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    text = models.TextField()
    published = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    parent = models.ForeignKey(
    'self', on_delete=models.CASCADE, blank=True, null=True
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-published']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def approve(self):
        self.approved = True
        self.save()

    def __str__(self):
        return self.text


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')

    def __str__(self):
        return f"{self.user.username} likes {self.comment.text[:20]}"


class Dislike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='dislikes')

    def __str__(self):
        return f"{self.user.username} dislikes {self.comment.text[:20]}"
