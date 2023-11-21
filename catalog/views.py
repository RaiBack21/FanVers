from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from .models import Book, Tag, Fandom, Country, Genres, Chapter, Comment, Like, Dislike, Rating, Quality, Income
from .forms import BookForm, ChapterForm, CommentForm
from .forms import EditBookForm
from Advertisement.models import Advertisement
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from users.models import Profile, Bookmark
import logging
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views import View
from django.db.models import Count, Sum
from django.http import JsonResponse, HttpResponseForbidden
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import BookSerializer
from rest_framework import generics
from .filters import BookFilter
from django_filters.widgets import BooleanWidget
import django_filters
from rest_framework.renderers import TemplateHTMLRenderer
from django.db.models import Q, F
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer, FandomSerializer
from datetime import date, datetime
import requests
from rest_framework.decorators import api_view
from django.conf import settings
from django.db import transaction
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from Advertisement.models import Advertisement

class Catalog(ListView):
    model = Book
    template_name = 'catalog/catalog.html'
    context_object_name = 'books'

    def get(self, request):
        genres = Genres.objects.all().values('name', 'id')
        tags = Tag.objects.all().values('name', 'id')
        fandoms = Fandom.objects.all().values('name', 'id')
        order = request.GET.get('order', 'title')

        if request.GET.getlist('bookid'):
            books = request.GET.getlist('bookid')
            books = Book.objects.filter(id__in=books)
        else:
            books = Book.objects.all()

        books = book_filter(self.request, books, order)

        content = {
            'books': books, 'genres': genres, 'tags': tags,
            'fandoms': fandoms, 'order': order
        }
        return render(request, 'catalog/catalog.html', content)

    def adv_show(self):
        Advertisement.objects.filter(end_date__lt=date.today()).delete()
        adv = Advertisement.objects.filter(location='catalog')
        adv_books = list()
        for book in adv:
            adv_books.append(book.book_id)

        listbooks = Book.objects.filter(id__in=adv_books)

        return listbooks

class BookBase(DetailView):
    model = Book
    context_object_name = 'book'
    template_name = 'catalog/about.html'

    def get(self, request, slug):
        book = get_object_or_404(Book, slug=slug)

        today = timezone.now().date()
        comment_form = CommentForm()

        translator_books = Book.objects.filter(user=book.user)[:8]
        chapters = Chapter.objects.filter(book=book.id).order_by('created_at')
        comments = Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(book), object_id=book.id,
        parent__isnull=True).annotate(likes_count=Count('likes'
        ), dislikes_count=Count('dislikes')).order_by('-published')
        comments_reply = Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(book), object_id=book.id,
        parent__isnull=False).annotate(likes_count=Count('likes'
        ), dislikes_count=Count('dislikes')).order_by('-published')
        us = request.user
        context = {
        'slug': book.slug, 'book': book, 'translator_books': translator_books,
        'chapters':chapters, 'comments': comments,
        'comments_reply': comments_reply, 'today': today,
        'comment_form': comment_form, 'us': us
        }
        if book.user != request.user:
            return render(request, 'catalog/about.html', context)
        else:
            return render(request, 'catalog/admin-about-book.html', context)


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            if request.POST.get("parent"):
                comment.parent_id = int(request.POST.get("parent"))
            comment.content_type = ContentType.objects.get_for_model(self.object)
            comment.object_id = self.object.id
            comment.owner = request.user.profile
            likes_count = 0
            dislikes_count = 0
            comment.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse(
                    {'text': comment.text, 'id': comment.id,
                     'owner': comment.owner.user.username,
                     'likes_count': likes_count,
                     'dislikes_count': dislikes_count,
                     'parentid': comment.parent_id
                     })  # Возвращаем JSON
            messages.success(request, 'Ваш комментарий появится после проверки модератором')
            return redirect('catalog:Book_Base', slug=self.object.slug)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': form.errors}, status=400)

class BookmarkListView(ListView):
    model = Bookmark
    context_object_name = 'bookmarks'
    template_name = 'catalog/bookmarks.html'

    def get(self, request):
        bookmarks = Bookmark.objects.filter(user_profile_id=request.user.id)
        return render(request, 'catalog/bookmarks.html', {'bookmarks': bookmarks})

def get_bookmarks_all(request):
    bookmarks = Bookmark.objects.filter(user_profile_id=request.user.id)
    return render(request, 'catalog/bookmarks.html', {'bookmarks': bookmarks})

def get_bookmarks_read(request):
    bookmarks = Bookmark.objects.filter(user_profile_id=request.user.id).filter(group='READ')
    return render(request, 'catalog/bookmarks.html', {'bookmarks': bookmarks})

def get_bookmarks_special(request):
    bookmarks = Bookmark.objects.filter(user_profile_id=request.user.id).filter(group='SPECIAL')
    return render(request, 'catalog/bookmarks.html', {'bookmarks': bookmarks})

def get_bookmarks_in_plans(request):
    bookmarks = Bookmark.objects.filter(user_profile_id=request.user.id).filter(group='IN_PLANS')
    return render(request, 'catalog/bookmarks.html', {'bookmarks': bookmarks})

def get_bookmarks_left(request):
    bookmarks = Bookmark.objects.filter(user_profile_id=request.user.id).filter(group='LEFT')
    return render(request, 'catalog/bookmarks.html', {'bookmarks': bookmarks})

def get_bookmarks_end_read(request):
    bookmarks = Bookmark.objects.filter(user_profile_id=request.user.id).filter(group='END_READ')
    return render(request, 'catalog/bookmarks.html', {'bookmarks': bookmarks})

@method_decorator(require_POST, name='post')
class BookmarkActionView(View):
    def post(self, request, slug):
        user = request.user
        new_group = request.POST.get('group')

        print('User:', user)  # Печатаем пользователя для отладки
        print('New Group:', new_group)  # Печатаем новую группу для отладки

        # Находим книгу по slug
        book = Book.objects.get(slug=slug)

        print('Book:', book)  # Печатаем найденную книгу для отладки

        # Проверяем, существует ли уже запись Bookmark для этого пользователя и книги
        bookmark, created = Bookmark.objects.get_or_create(user_profile=user.profile, book=book)

        print('Bookmark:', bookmark)  # Печатаем объект закладки для отладки

        # Обновляем значение группы
        if new_group:
            bookmark.group = new_group
        bookmark.save()

        print('Bookmark Group Updated:', bookmark.group)  # Печатаем обновленную группу для отладки

        # Возвращаем JSON-ответ
        # return JsonResponse({'success': True})
        return redirect('catalog:Book_Base', slug=book.slug)

@method_decorator(login_required, name='dispatch')
class LikeCommentView(View):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        like, created = Like.objects.update_or_create(user=request.user, comment=comment)

        if not created:
            like.delete()

        dislike = Dislike.objects.filter(user=request.user, comment=comment).first()
        if dislike:
            dislike.delete()

        return JsonResponse({'likes': comment.likes.count(), 'dislikes': comment.dislikes.count()})


@method_decorator(login_required, name='dispatch')
class DislikeCommentView(View):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        dislike, created = Dislike.objects.update_or_create(user=request.user, comment=comment)

        if not created:
            dislike.delete()

        like = Like.objects.filter(user=request.user, comment=comment).first()
        if like:
            like.delete()

        return JsonResponse({'likes': comment.likes.count(), 'dislikes': comment.dislikes.count()})


@method_decorator(login_required, name='dispatch')
class DeleteCommentView(View):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)

        # Проверяем, что пользователь - автор комментария
        if comment.owner.user != request.user:
            return HttpResponseForbidden("You are not allowed to delete this comment")

        comment.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})

        return redirect('catalog:Book_Base',
                        slug=comment.book.slug)  # Редирект на страницу книги (нужно добавить поле book в модель Comment)


@login_required
def rate_book(request):
    if request.method == 'POST':
        book_id = int(request.POST.get('book_id'))
        stars = request.POST.get('stars')
        print(book_id, flush=True)
        #
        book = get_object_or_404(Book, id=book_id)
        averge_rating = book.avg_rating()

        user = request.user
        rating, created = Rating.objects.update_or_create(book=book, user=user, defaults={'stars': stars})
        rating.stars = stars
        rating.timestamp = timezone.now()
        rating.save()

        # Получить новый средний рейтинг
        avg_rating = book.avg_rating()
        # Ответите с новым средним рейтингом
        return JsonResponse({'avg_rating': avg_rating})
    else:
        return HttpResponseBadRequest("Invalid HTTP method")


@login_required
def get_user_rating(request):
    if request.method == 'GET':
        user = request.user
        book_id = request.GET.get('book_id')
        book = get_object_or_404(Book, id=book_id)
        try:
            avg_rating = book.avg_rating()
        except Rating.DoesNotExist:
            avg_rating = None

        return JsonResponse({'user_rating': avg_rating})

@login_required
def quality_translation(request):
    if request.method == 'POST':
        book_id = int(request.POST.get('book_id'))
        stars = request.POST.get('starsb')
        print(book_id, flush=True)
        book = get_object_or_404(Book, id=book_id)
        averge_quality = book.avg_quality()

        user = request.user
        quality, created = Quality.objects.get_or_create(book=book, user=user, defaults={'stars': stars})
        quality.stars = stars
        quality.save()

        avg_quality = book.avg_quality()
        return JsonResponse({'avg_quality': avg_quality})
    else:
        return HttpResponseBadRequest("Invalid HTTP method")


@login_required
def get_user_quality(request):
    if request.method == 'GET':
        user = request.user
        book_id = request.GET.get('book_id')
        book = get_object_or_404(Book, id=book_id)
        try:
            avg_quality = book.avg_quality()
        except Quality.DoesNotExist:
            avg_quality = None

        return JsonResponse({'user_quality': avg_quality})

class TagList(ListView):
    model = Tag
    template_name = 'catalog/tag_list.html'
    context_object_name = 'tags'

    def get_tag(self):
        return Tag.objects.all()

class TagDetail(DetailView):
    model = Tag
    template_name = 'catalog/tag_detail.html'
    context_object_name = 'tag'


class FandomList(ListView):
    model = Fandom
    template_name = 'catalog/fandom_list.html'
    context_object_name = 'fandoms'

    def get_fandom(self):
        return Fandom.objects.all()


class FandomDetail(DetailView):
    model = Fandom
    template_name = 'catalog/fandom_detail.html'
    context_object_name = 'fandom'


class GenresList(ListView):
    model = Genres
    template_name = 'catalog/genres_list.html'
    context_object_name = 'genres'

    def get_genre(self):
        return Genres.objects.all()


class GenresDetail(DetailView):
    model = Genres
    template_name = 'catalog/genres_detail.html'
    context_object_name = 'genre'



class CountryList(ListView):
    model = Country
    template_name = 'catalog/country_list.html'
    context_object_name = 'countries'

    def get_country(self):
        return Country.objects.all()


class CountryDetail(DetailView):
    model = Country
    template_name = 'catalog/country_detail.html'
    context_object_name = 'country'




def book_list(request):  # Определяем функцию представления для списка книг.
    book_filter = BookFilter(request.GET, queryset=Book.objects.all(),
                             request=request)  # Создаем экземпляр фильтра с параметрами запроса.
    return render(request, 'template_name.html',
                  {'filter': book_filter})  # Рендерим шаблон, передавая ему экземпляр фильтра.


def edit_chapter(request, book_slug, chapter_slug):
    book = get_object_or_404(Book, slug=book_slug)
    chapter = get_object_or_404(Chapter, book=book, slug=chapter_slug)

    if request.method == 'POST':
        form = ChapterForm(request.POST, instance=chapter)
        if form.is_valid():
            form.save()
            messages.success(request, 'Глава успешно обновлена.')
            return redirect('catalog:chapter_detail', book_slug=book_slug, chapter_slug=chapter_slug)
    else:
        form = ChapterForm(instance=chapter)

    return render(request, 'catalog/chapter_edit.html', {'form': form, 'chapter': chapter})


class ChapterDetail(DetailView):
    model = Chapter
    template_name = 'catalog/chapter_detail.html'
    context_object_name = 'chapter'

    def get(self, request, book_slug, chapter_slug):
        book = get_object_or_404(Book, slug=book_slug)
        chapter = get_object_or_404(Chapter, slug=chapter_slug)

        today = timezone.now().date()
        comment_form = CommentForm()



        book_chapters = Chapter.objects.filter(
            book_id=book.id).select_related("book").order_by('created_at')
        prev_chap = book_chapters.filter(
            created_at__lt=chapter.created_at).order_by('-created_at').first()
        next_chap = book_chapters.filter(
            created_at__gt=chapter.created_at).order_by('created_at').first()


        comments = Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(chapter), object_id=chapter.id,
        parent__isnull=True).annotate(likes_count=Count('likes'
        ), dislikes_count=Count('dislikes')).order_by('-published')

        comments_reply = Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(chapter), object_id=chapter.id,
        parent__isnull=False).annotate(likes_count=Count('likes'
        ), dislikes_count=Count('dislikes')).order_by('-published')

        us = request.user

        context = {
        'book_slug': book.slug, 'chapter_slug': chapter.slug, 'book': book,
        'chapter':chapter, 'comments': comments,
        'comments_reply': comments_reply, 'today': today,
        'comment_form': comment_form, 'us': us, 'book_chapters': book_chapters,
        'prev_chap': prev_chap, 'next_chap': next_chap
        }

        if book.user != request.user:
            return render(request, 'catalog/chapter_detail.html', context)
        else:
            return render(request, 'catalog/chapter_detail.html', context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            if request.POST.get("parent"):
                comment.parent_id = int(request.POST.get("parent"))
            comment.content_type = ContentType.objects.get_for_model(self.object)
            comment.object_id = self.object.id
            comment.owner = request.user.profile
            likes_count = 0
            dislikes_count = 0
            comment.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse(
                    {'text': comment.text, 'id': comment.id,
                     'owner': comment.owner.user.username,
                     'likes_count': likes_count,
                     'dislikes_count': dislikes_count,
                     'parentid': comment.parent_id
                     })  # Возвращаем JSON
            messages.success(request, 'Ваш комментарий появится после проверки модератором')
            return redirect('catalog:Book_Base', slug=self.object.slug)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': form.errors}, status=400)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        book_slug = self.kwargs.get('book_slug')
        chapter_slug = self.kwargs.get('chapter_slug')

        if book_slug is not None and chapter_slug is not None:
            chapter = get_object_or_404(Chapter, slug=chapter_slug)
            chapter.chapter_views += 1
            chapter.save()
            if chapter_slug == 'edit':
                # Обработка для редактирования главы
                # Возможно, перенаправление или что-то другое
                return HttpResponseRedirect(
                    reverse('catalog:chapter_edit', kwargs={'book_slug': book_slug, 'chapter_slug': chapter_slug}))

            return get_object_or_404(queryset, book__slug=book_slug, slug=chapter_slug)


class ChapterCreate(LoginRequiredMixin, CreateView):
    model = Chapter
    form_class = ChapterForm
    template_name = 'catalog/chapter_form.html'

    def form_valid(self, form):
        book_slug = self.kwargs['book_slug']
        book = get_object_or_404(Book, slug=book_slug)
        form.instance.book = book

        # If a file was uploaded
        if form.instance.file:
            try:
                # Read the file and put its content into the 'content' field
                file_content = form.instance.file.read().decode('utf-8')
                form.instance.content = file_content
            except Exception as e:
                messages.error(self.request, f"Error reading file: {str(e)}")
                return super().form_invalid(form)
        elif not form.instance.content:
            messages.error(self.request, "You must provide chapter content or upload a file.")
            return super().form_invalid(form)

        form.instance.content_length = len(form.instance.content)

        # После сохранения или редактирования главы, обновите счетчик символов пользователя и комиссию.
        user_profile = self.request.user.profile
        user_profile.total_symbols = user_profile.total_symbols_count()
        user_profile.save()  # Сохраните профиль, чтобы обновить подсчет символов и комиссию

        return super().form_valid(form)

    def get_success_url(self):
        book_slug = self.object.book.slug  # здесь мы получаем slug из созданной главы
        chapter_slug = self.object.slug
        return reverse('catalog:chapter_detail', kwargs={'book_slug': book_slug, 'chapter_slug': chapter_slug})


def setting_book(request, book_slug_setting_book):
    book = get_object_or_404(Book, slug=book_slug_setting_book)
    genres = Genres.objects.all()
    tags = Tag.objects.all()
    fandoms = Fandom.objects.all()

    if request.method == 'POST':
        form = EditBookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user
            book.adult_content = form.cleaned_data.get('is_adult', False)
            book.save()
            form.save_m2m()
            messages.success(request, 'Книга успешно обновлена.')
            return redirect('catalog:Book_Base', slug=book.slug)
    else:
        initial_data = {
            'tags': [tag.id for tag in book.tags.all()],
            'fandoms': [fandom.id for fandom in book.fandoms.all()],
            'country': book.country.id if book.country else None,
            'genres': [genre.id for genre in book.genres.all()],
            'is_adult': book.adult_content,
            'status': Book.status,  # Добавляем начальное значение для статуса
        }
        form = EditBookForm(instance=book, initial=initial_data)

    return render(request, 'catalog/book_edit.html', {
    'form': form, 'book': book, 'genres': genres, 'tags': tags,
     'fandoms': fandoms})


def get_additional_data(request):  # для обработки Ajax-запроса setting_book
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        book_id = request.GET.get('book_id')
        book = get_object_or_404(Book, id=book_id)
        form = EditBookForm(instance=book)

        data = {
            'tags': list(Tag.objects.values('id', 'name')),
            'initial_tags': list(form.get_initial_tags().values_list('id', flat=True)),
            'fandoms': list(book.fandoms.values('id', 'name')),
            'initial_fandoms': list(form.get_initial_fandoms().values_list('id', flat=True)),
            'country': book.country.id if book.country else None,
            'initial_country': form.get_initial_country().id if form.get_initial_country() else None,
            'genres': list(book.genres.values('id', 'name')),
            'initial_genres': list(form.get_initial_genres().values_list('id', flat=True)),
            # Повторите для остальных полей
        }

        return JsonResponse(data)

#
import logging

logger = logging.getLogger(__name__)

class NotificationListView(ListView):
        model = Notification
        template_name = 'catalog/notifications.html'
        context_object_name = 'notifications'

class NotificationListAPIView(APIView):
    def get(self, request, *args, **kwargs):

        logger.info("-------------------- NotificationListAPIView get")

        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)  # Получаем session_key из кук
        user_id = -1
        try:
            session = Session.objects.get(session_key=session_key)  # Находим соответствующую сессию
            user_id = session.get_decoded().get('_auth_user_id')  # Получаем ID пользователя из сессии

            user = User.objects.get(id=user_id)  # Находим пользователя по ID

        except Session.DoesNotExist:
            user = None

        if user is not None:
            # Пользователь аутентифицирован, вы можете использовать user для дальнейших действий
            logger.info("-------------------- NotificationListAPIView User Found: " + user.username)

            user_prof = Profile.objects.filter(user_id=user_id)
            notifications = Notification.objects.filter(user_profile=user_prof[0])  # вмене тут раніше було  (user_profile=user_profile)
            logger.info("-------------------- NotificationListAPIView Notification.objects.all() : " + str(len(notifications)) )

            serializer = NotificationSerializer(notifications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Доступ запрещен"}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
def get_notifications(request):
    # Получение токена из заголовка запроса
    token = request.headers.get('Authorization', '').split(' ')[1]  # Извлечение токена из заголовка
    # Остальная часть вашего кода остается без изменений
    api_url = 'http://localhost:port/api/notifications/'

    try:
        headers = {
            'Authorization': f'Bearer {token}'
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:  # Успешный запрос
            data = response.json()
            # Обработка данных, полученных от API
            print('Успешно получены уведомления:', data)
        else:
            print('Ошибка при получении уведомлений:', response.status_code)

    except requests.exceptions.RequestException as e:
        print('Ошибка при выполнении запроса:', e)


if __name__ == "__main__":
    get_notifications()

logger = logging.getLogger(__name__)


@login_required
def book_create(request):
    logger.info("Start book_create")
    genres = Genres.objects.all()
    tags = Tag.objects.all()
    fandoms = Fandom.objects.all()
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)

        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user
            book.is_adult = form.cleaned_data.get('is_adult', False)
            book.status = Book.TRANSLATING
            book.save()
            form.save_m2m()
            messages.success(request, "The book was created successfully!")
            print(f"Redirecting to: catalog:Book_Base, slug={book.slug}")
            # return render(request, 'catalog/create-translation.html', {'form': form, 'genres': genres, 'tags': tags, 'fandoms': fandoms, 'book_id': book.id})
            return redirect('catalog:Book_Base', slug=book.slug)
        else:
            logger.info("Form is not valid: %s" % form.errors)
            print("Form is not valid")
            print(form.errors)
            form = BookForm(request.POST, request.FILES)
        return render(request, 'catalog/create-translation.html', {'form': form})

    else:
        form = BookForm(request.POST or None, request.FILES or None, initial={'status': Book.TRANSLATING})
    return render(request, 'catalog/create-translation.html', {'form': form, 'genres': genres, 'tags': tags, 'fandoms': fandoms})

def ajax_cost(request, book_slug_setting_book):
    location = request.GET.get('location')
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')
    genre = request.GET.get("genre")
    tag = request.GET.get("tag")
    fandom = request.GET.get("fandom")

    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')
    days = end_date - start_date

    if genre or tag or fandom:
        price = 15
        cost = (days.days) * price
    else:
        price = 30
        cost = (days.days) * price

    results = {cost: cost}
    return HttpResponse(results)

def ajax_cost_sum(request, book_slug_setting_book):
    cost1 = int(request.GET.get('cost1'))
    cost2 = int(request.GET.get('cost2'))
    cost3 = int(request.GET.get('cost3'))
    cost4 = int(request.GET.get('cost4'))
    cost5 = int(request.GET.get('cost5'))
    cost = cost1+cost2+cost3+cost4+cost5
    results = {cost: cost}
    return HttpResponse(results)

@login_required
def book_advertisement_settings(request, book_slug_setting_book):
    genres = Genres.objects.all()
    tags = Tag.objects.all()
    fandoms = Fandom.objects.all()
    cost = 0
    cost1 = 0
    cost2 = 0
    cost3 = 0
    cost4 = 0
    cost5 = 0
    days = 0
    start_date = ''
    end_date = ''
    start_dateg = ''
    end_dateg = ''
    start_datet = ''
    end_datet = ''
    start_datef = ''
    end_datef = ''
    start_datec = ''
    end_datec = ''

    # if request.method == 'GET':
        # location = request.GET.get('location')
        # start = request.GET.get('start_date')
        # end = request.GET.get('end_date')
        # if start and end:
        #     start_date = datetime.strptime(start, '%Y-%m-%d')
        #     end_date = datetime.strptime(end, '%Y-%m-%d')

        # return redirect('catalog:book_create')

    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        book = get_object_or_404(Book, id=book_id)

        cost = int(request.POST.get('cost'))
        cost1 = request.POST.get('cost1')
        cost2 = request.POST.get('cost2')
        cost3 = request.POST.get('cost3')
        cost4 = request.POST.get('cost4')
        cost5 = request.POST.get('cost5')

        location = request.POST.get('location')
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        if start and end:
            start_date = datetime.strptime(start, '%Y-%m-%d')
            end_date = datetime.strptime(end, '%Y-%m-%d')

        locationc = request.POST.get('locationc')
        startc = request.POST.get('start_datec')
        endc = request.POST.get('end_datec')
        if startc and endc:
            start_datec = datetime.strptime(startc, '%Y-%m-%d')
            end_datec = datetime.strptime(endc, '%Y-%m-%d')

        locationg = request.POST.get('locationg')
        genre = request.POST.get('genre')
        startg = request.POST.get('start_dateg')
        endg = request.POST.get('end_dateg')
        if startg and endg:
            start_dateg = datetime.strptime(startg, '%Y-%m-%d')
            end_dateg = datetime.strptime(endg, '%Y-%m-%d')

        locationt = request.POST.get('locationt')
        tag = request.POST.get('tag')
        startt = request.POST.get('start_datet')
        endt = request.POST.get('end_datet')
        if startt and endt:
            start_datet = datetime.strptime(startt, '%Y-%m-%d')
            end_datet = datetime.strptime(endt, '%Y-%m-%d')

        locationf = request.POST.get('locationf')
        fandom = request.POST.get('fandom')
        startf = request.POST.get('start_datef')
        endf = request.POST.get('end_datef')
        if startf and endf:
            start_datef = datetime.strptime(startf, '%Y-%m-%d')
            end_datef = datetime.strptime(endf, '%Y-%m-%d')

        user_balance = request.user.profile.balance
        if user_balance < cost:
            results = messages.error(request, 'На рахунку не достатньо коштів.')
            return HttpResponse(results)
        else:
            if start_date and end_date:
                with transaction.atomic():
                    request.user.profile.balance -= int(cost1)
                    request.user.profile.save()

                    advertisement = Advertisement(
                        user=request.user,
                        book=book,
                        start_date=start_date,
                        end_date=end_date,
                        location=location,
                        cost=int(cost1)
                    )
                    advertisement.save()

            if start_datec and end_datec:
                with transaction.atomic():
                    request.user.profile.balance -= int(cost2)
                    request.user.profile.save()

                    advertisement = Advertisement(
                        user=request.user,
                        book=book,
                        start_date=start_datec,
                        end_date=end_datec,
                        location=locationc,
                        cost=int(cost2)
                    )
                    advertisement.save()

            if start_dateg and end_dateg:
                with transaction.atomic():
                    request.user.profile.balance -= int(cost3)
                    request.user.profile.save()

                    advertisement = Advertisement(
                        user=request.user,
                        book=book,
                        start_date=start_dateg,
                        end_date=end_dateg,
                        location=locationg,
                        genre=genre,
                        cost=int(cost3)
                    )
                    advertisement.save()

            if start_datet and end_datet:
                with transaction.atomic():
                    request.user.profile.balance -= int(cost4)
                    request.user.profile.save()

                    advertisement = Advertisement(
                        user=request.user,
                        book=book,
                        start_date=start_datet,
                        end_date=end_datet,
                        location=locationt,
                        tag=tag,
                        cost=int(cost4)
                    )
                    advertisement.save()

            if start_datef and end_datef:
                with transaction.atomic():
                    request.user.profile.balance -= int(cost5)
                    request.user.profile.save()

                    advertisement = Advertisement(
                        user=request.user,
                        book=book,
                        start_date=start_datef,
                        end_date=end_datef,
                        location=locationf,
                        fandom=fandom,
                        cost=int(cost5)
                    )
                    advertisement.save()
            return HttpResponseRedirect('')


@login_required
def become_translator(request):
    # Это извлекает объект группы с именем 'Перекладач' из базы данных.
    translator_group = Group.objects.get(name='Перекладач')
    # Это добавляет текущего пользователя (пользователя, который отправил запрос) в группу 'Перекладач'.
    request.user.groups.add(translator_group)

    # Обновление группы в профиле пользователя
    profile = Profile.objects.get(user=request.user)
    profile.group = translator_group
    profile.save()

    # Получаем обновленную группу
    user = request.user
    user_group = user.groups.first()

    context = {
        'user_group': user_group
    }

    return render(request, 'users/profile.html')


# Аналогично предыдущему представлению, этот декоратор проверяет, вошел ли пользователь в систему перед тем,
# как получить доступ к этому представлению.
@login_required
def become_freelancer(request):
    # Это извлекает объект группы с именем 'Фрілансер' из базы данных.
    freelancer_group = Group.objects.get(name='Фрілансер')
    # Это добавляет текущего пользователя в группу 'Фрілансер'.
    request.user.groups.add(freelancer_group)

    # Обновление группы в профиле пользователя
    profile = Profile.objects.get(user=request.user)
    profile.group = freelancer_group
    profile.save()

    user = request.user
    user_group = user.groups.first()

    context = {
        'user_group': user_group
    }

    return render(request, 'users/profile.html')


@login_required
def change_group(request, new_group_name):
    all_groups = ['Читач', 'Перекладач', 'Фрілансер']
    new_group = Group.objects.get(name=new_group_name)
    if new_group.name not in all_groups:
        raise PermissionDenied
    else:
        # Удаляем пользователя из всех групп
        for group_name in all_groups:
            try:
                group = Group.objects.get(name=group_name)
                request.user.groups.remove(group)
            except Group.DoesNotExist:
                continue
        # Добавляем пользователя в новую группу
        request.user.groups.add(new_group)
        return redirect('home')


class BookSearchView(CountryList, GenresList, TagList, FandomList, Book, ListView):
    serializer_class = BookSerializer
    template_name = 'catalog/search.html'

    def get_queryset(self):
        # order = request.GET.get('order')
        queryset = Book.objects.all()
        # book_filter(request, queryset, order)

        return queryset

    def adv_show(self):
        Advertisement.objects.filter(end_date__lt=date.today()).delete()
        listbooks = None

        selected_genres = self.request.GET.getlist('genres')
        selected_tags = self.request.GET.getlist('tags')
        selected_fandoms = self.request.GET.getlist('fandoms')

        if selected_genres or selected_tags or selected_fandoms:
            listbooks = Book.objects.all()

            if selected_genres:
                idbook=list(Book.objects.values_list('id', flat=True))

                listbooks = listbooks.filter(
                advertisement__location='genres',
                advertisement__genre__in=selected_genres,
                advertisement__book_id__in=idbook)

            if selected_tags:
                idbook=list(Book.objects.values_list('id', flat=True))

                listbooks = listbooks.filter(
                advertisement__location='tags',
                advertisement__tag__in=selected_tags,
                advertisement__book_id__in=idbook)

            if selected_fandoms:
                idbook=list(Book.objects.values_list('id', flat=True))

                listbooks = listbooks.filter(
                advertisement__location='fandoms',
                advertisement__fandom__in=selected_fandoms,
                advertisement__book_id__in=idbook)

            if len(list(listbooks)) <= 5:
                if selected_genres and selected_tags:
                    idbook=list(Book.objects.values_list('id', flat=True))

                    listbooks1 = Book.objects.filter(
                    advertisement__location='genres',
                    advertisement__genre__in=selected_genres,
                    advertisement__book_id__in=idbook)

                    listbooks2 = Book.objects.filter(
                    advertisement__location='tags',
                    advertisement__tag__in=selected_tags,
                    advertisement__book_id__in=idbook)

                    listbooks = listbooks1.union(listbooks2)

                if selected_genres and selected_fandoms:
                    idbook=list(Book.objects.values_list('id', flat=True))

                    listbooks1 = Book.objects.filter(
                    advertisement__location='genres',
                    advertisement__genre__in=selected_genres,
                    advertisement__book_id__in=idbook)

                    listbooks2 = Book.objects.filter(
                    advertisement__location='fandoms',
                    advertisement__fandom__in=selected_fandoms,
                    advertisement__book_id__in=idbook)

                    listbooks = listbooks1.union(listbooks2)

                if selected_tags and selected_fandoms:
                    idbook=list(Book.objects.values_list('id', flat=True))

                    listbooks1 = Book.objects.filter(
                    advertisement__location='tags',
                    advertisement__tag__in=selected_tags,
                    advertisement__book_id__in=idbook)

                    listbooks2 = Book.objects.filter(
                    advertisement__location='fandoms',
                    advertisement__fandom__in=selected_fandoms,
                    advertisement__book_id__in=idbook)

                    listbooks = listbooks1.union(listbooks2)

                if selected_genres and selected_tags and selected_fandoms:
                    idbook=list(Book.objects.values_list('id', flat=True))

                    listbooks1 = Book.objects.filter(
                    advertisement__location='genres',
                    advertisement__genre__in=selected_genres,
                    advertisement__book_id__in=idbook)

                    listbooks2 = Book.objects.filter(
                    advertisement__location='tags',
                    advertisement__tag__in=selected_tags,
                    advertisement__book_id__in=idbook)

                    listbooks3 = Book.objects.filter(
                    advertisement__location='fandoms',
                    advertisement__fandom__in=selected_fandoms,
                    advertisement__book_id__in=idbook)


                    listbooks = listbooks1.union(listbooks2, listbooks3)

        return listbooks

def book_filter(request, queryset, order):
    filtred_book = queryset

    selected_text = request.GET.get("q")
    if selected_text:
        filtred_book = filtred_book.filter(title__istartswith=selected_text)

    is_adult_yes = request.GET.get('is_adult_yes')
    is_adult_no = request.GET.get('is_adult_no')
    if is_adult_no:
        filtred_book = filtred_book.all()
    elif is_adult_yes:
        filtred_book = filtred_book.filter(adult_content=False)

    selected_genres = request.GET.getlist("genres")
    if selected_genres:
        filtred_book = filtred_book.filter(genres__in=selected_genres)

    selected_tags = request.GET.getlist("tags")
    if selected_tags:
        filtred_book = filtred_book.filter(tags__in=selected_tags)

    selected_fandoms = request.GET.getlist("fandoms")
    if selected_fandoms:
        filtred_book = filtred_book.filter(fandoms__in=selected_fandoms)

    selected_ex_genres = request.GET.getlist("ex_genres")
    if selected_ex_genres:
        filtred_book = filtred_book.exclude(genres__in=selected_ex_genres)

    selected_ex_tags = request.GET.getlist("ex_tags")
    if selected_ex_tags:
        filtred_book = filtred_book.exclude(tags__in=selected_ex_tags)

    selected_ex_fandoms = request.GET.getlist("ex_fandoms")
    if selected_ex_fandoms == ['all']:
        filtred_book = filtred_book.filter(fandoms=None)
    else:
        filtred_book = filtred_book.exclude(fandoms__in=selected_ex_fandoms)

    min_chapter_count = request.GET.get("chapters_min")
    max_chapter_count = request.GET.get("chapters_max")
    if min_chapter_count:
        filtred_book = filtred_book.alias(chapters=Count("book_chapters")).filter(chapters__gte=min_chapter_count)
    if max_chapter_count:
        filtred_book = filtred_book.alias(chapters=Count("book_chapters")).filter(chapters__lte=max_chapter_count)
    if min_chapter_count and max_chapter_count:
        filtred_book = filtred_book.alias(chapters=Count("book_chapters")).filter(Q(chapters__gte=min_chapter_count) &
            Q(chapters__lte=max_chapter_count))

    viewed_books = request.GET.get('viewed_books')
    if viewed_books:
        if request.user.is_authenticated:
            user = request.user
            filtred_book = filtred_book.exclude(viewed_by__id=user.id)
        else:
            filtred_book = filtred_book.all()

    ex_all_fandoms = request.GET.get('ex_all_fandoms')
    if ex_all_fandoms:
        filtred_book = filtred_book.filter(fandoms=None)

    completed = request.GET.get('completed')
    if completed:
        filtred_book = filtred_book.filter(status='Завершено')

    translating = request.GET.get('translating')
    if translating:
        filtred_book = filtred_book.filter(status='Перекладається')

    bookmarks = request.GET.get('bookmarks')
    if bookmarks:
        user = request.user
        user_bookmark = Bookmark.objects.filter(user_profile_id=user.id).filter(book_id__in=filtred_book).values('book_id')
        filtred_book = filtred_book.exclude(id__in=user_bookmark)

    # selected_country = self.request.GET.getlist("country")
    # if selected_country:
    #     queryset = queryset.filter(country__in=selected_country)

    #Sorting books
    if order == 'title':
        filtred_book = filtred_book.order_by('title')
    if order == 'pub_date':
        filtred_book = filtred_book.order_by('pub_date')
    if order == 'last_updated':
        filtred_book = filtred_book.order_by('last_updated')
    if order == 'ratings':
        filtred_book = filtred_book.annotate(count_rating=Count('book_ratings'))
        filtred_book = filtred_book.order_by('-count_rating')
    if order == 'views':
        filtred_book = filtred_book.annotate(views=Count('viewed_by'))
        filtred_book = filtred_book.order_by('-views')
    if order == 'quality':
        filtred_book = filtred_book.annotate(count_quality=Count('book_quality'))
        filtred_book = filtred_book.order_by('-count_quality')
    if order == 'free_pages':
        filtred_book = filtred_book.annotate(price=Count('book_chapters__price'))
        filtred_book = filtred_book.order_by('price')
    if order == 'pages':
        filtred_book = filtred_book.annotate(pages=Sum('book_chapters__content_length'))
        filtred_book = filtred_book.order_by('-pages')
    if order == 'chapters':
        filtred_book = filtred_book.annotate(chapters=Count('book_chapters'))
        filtred_book = filtred_book.order_by('-chapters')
    if order == 'bookmarks_sort':
        filtred_book = filtred_book.annotate(bookmarks_sort=Count('bookmark'))
        filtred_book = filtred_book.order_by('-bookmarks_sort')



    return filtred_book.distinct()

class Search(CountryList, GenresList, TagList, FandomList, Book, ListView):
    serializer_class = BookSerializer
    template_name = 'catalog/search_results.html'

    def get_queryset(self):
        return Book.objects.filter(title__icontains=self.request.GET.get('q', ''))

class OwnTranslationsListView(ListView):
    model = Book
    template_name = 'catalog/own-translations.html'

    def get(self, request):
        user = request.user
        books = (Book.objects.
            filter(user_id=user.id).
            select_related('user').
            annotate(total_income=Sum("income__amount"))).annotate(today_book_income=Sum("income__amount", filter=Q(income__datetime__date=date.today())))
        total_chars = sum(ch.content_length for ch in Chapter.objects.filter(book__user=self.request.user))
        total_pages =  total_chars//1500
        if total_chars < 5000:
            commission_rate = 15
        elif total_chars < 10000:
            commission_rate = 12
        else:
            commission_rate = 5

        context = {
            'books': books, 'total_chars': total_chars,
            'commission_rate': commission_rate, 'total_pages': total_pages,
        }
        return render(request, 'catalog/own-translations.html', context)

class LeftTranslationsListView(ListView):
    model = Book
    template_name = 'catalog/left-translations.html'

    def get(self, request):
        genres = Genres.objects.all().values('name', 'id')
        tags = Tag.objects.all().values('name', 'id')
        fandoms = Fandom.objects.all().values('name', 'id')
        order = request.GET.get('order', 'title')

        if request.GET.getlist('bookid'):
            books = request.GET.getlist('bookid')
            print(books)
            books = Book.objects.filter(id__in=books)
            print(books)
        else:
            books = Book.objects.filter(status='Покинутий')
            print(books)

        books = book_filter(self.request, books, order)
        print(books)

        content = {
            'books': books, 'genres': genres, 'tags': tags,
            'fandoms': fandoms, 'order': order
        }

        return render(request, 'catalog/left-translations.html', content)

class TitleAutocompleteView(View):
    def get(self, request):
        query = request.GET.get('query')
        books = Book.objects.filter(title__icontains=query)[:5]
        data = [{'title': book.title} for book in books]
        return JsonResponse(data, safe=False)


class GenresAutocompleteView(View):
    def get(self, request):
        query = request.GET.get('query')
        genres = Genres.objects.filter(name__icontains=query)[:5]
        data = [{'name': genre.name} for genre in genres]
        return JsonResponse(data, safe=False)


class TagsAutocompleteView(View):
    def get(self, request):
        query = request.GET.get('query')
        tags = Tag.objects.filter(name__icontains=query)[:5]
        data = [{'name': tag.name} for tag in tags]
        return JsonResponse(data, safe=False)


class FandomAutocompleteView(View):
    def get(self, request):
        query = request.GET.get('query')
        fandoms = Fandom.objects.filter(name__icontains=query)[:5]
        data = [{'name': fandom.name} for fandom in fandoms]
        return JsonResponse(data, safe=False)


class BookAdultAutocompleteView(View):
    def get(self, request):
        query = request.GET.get('query')
        books = Book.objects.filter(title__icontains=query, is_adult=True)[:5]
        data = [{'title': book.title} for book in books]
        return JsonResponse(data, safe=False)


class BookNotAdultAutocompleteView(View):
    def get(self, request):
        query = request.GET.get('query')
        books = Book.objects.filter(title__icontains=query, is_adult=False)[:5]
        data = [{'title': book.title} for book in books]
        return JsonResponse(data, safe=False)
