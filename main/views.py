from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from catalog.models import Book
from .models import Settings
from Advertisement.models import *
from Advertisement.views import del_adv
from catalog.serializers import BookSerializer
from django.views.generic import ListView, TemplateView
from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Count

class HomePageView(ListView):
    model = Book
    serializer_class = BookSerializer
    template_name = 'main/index.html'

    def adv_show(self):
        del_adv()
        adv = Advertisement.objects.filter(location='main')
        adv_books = list()
        for book in adv:
            adv_books.append(book.book_id)

        adv_books = Book.objects.filter(id__in=adv_books)

        return adv_books

    def new_books(self):
        end_of_month = timezone.now()
        start_of_month = end_of_month - timezone.timedelta(days=30)
        new_books = Book.objects.filter(
        pub_date__range=(start_of_month, end_of_month)
        ).order_by('-pub_date')[:8]
        return new_books

    def last_updated_books(self):
        end_of_month = timezone.now()
        start_of_month = end_of_month - timezone.timedelta(days=30)
        last_updated_books = Book.objects.filter(
        book_chapters__created_at__range=(start_of_month, end_of_month)
        ).distinct().order_by('-book_chapters__created_at')[:6]
        return last_updated_books

    def trending_books(self):
        trending_books = Book.objects.order_by('-trending_score')[:6]
        return trending_books

    def top_day_books(self):
        end_of_day = timezone.now()
        start_of_day = end_of_day - timezone.timedelta(days=1)

        top_day_books = (
            Book.objects
            .annotate(num_ratings=Count('book_ratings'))
            .filter(book_ratings__timestamp__range=(start_of_day, end_of_day))
            .order_by('-num_ratings') # Отримати топ-6 книг
        )[:6]
        return top_day_books

    def top_week_books(self):
        # Визначте початок і кінець останнього дня
        end_of_day = timezone.now()
        start_of_day = end_of_day - timezone.timedelta(days=7)

        top_week_books = (
            Book.objects
            .annotate(num_ratings=Count('book_ratings'))
            .filter(book_ratings__timestamp__range=(start_of_day, end_of_day))
            .order_by('-num_ratings') # Отримати топ-6 книг
        )[:6]
        return top_week_books

    def top_month_books(self):
        # Визначте початок і кінець останнього дня
        end_of_day = timezone.now()
        start_of_day = end_of_day - timezone.timedelta(days=30)

        top_month_books = (
            Book.objects
            .annotate(num_ratings=Count('book_ratings'))
            .filter(book_ratings__timestamp__range=(start_of_day, end_of_day))
            .order_by('-num_ratings') # Отримати топ-6 книг
        )[:6]
        return top_month_books

    def top_general_books(self):
        # Визначте початок і кінець останнього дня
        end_of_day = timezone.now()
        start_of_day = end_of_day - timezone.timedelta(days=365)

        top_general_books = (
            Book.objects
            .annotate(num_ratings=Count('book_ratings'))
            .filter(book_ratings__timestamp__range=(start_of_day, end_of_day))
            .order_by('-num_ratings') # Отримати топ-6 книг
        )[:6]
        return top_general_books



def For_copyright_holders(request):
    return render(request, 'main/For_copyright_holders.html')

def Reference(request):
    return render(request, 'main/Reference.html')

def Write_to_support(request):
    return render(request, 'main/Write_to_support.html')
def Contacts(request):
    return render(request, 'main/Contacts.html')

def thanks(request):
    return render(request, 'main/thanks.html')

def Suggest_improvements(request):
    return render(request, 'main/Suggest_improvements.html')

def money_problem(request):
    return render(request, 'main/money_problem.html')
def user_agreement(request):
    return render(request, 'main/user_agreement.html')

def faq(request):
    return render(request, 'main/faq.html')

def page_not_found_view(request, exception):
    return render(request, 'main/404.html', status=404)
