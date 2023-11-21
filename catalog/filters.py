import django_filters
from .models import Book, Genres, Country, Tag, Fandom
from django_filters import rest_framework as filters



def get_client_ip(request):
    """Получение IP пользоваеля"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class BookFilter(django_filters.FilterSet):
    # Добавьте фильтры для жанров, страны, количества глав и других полей
    genres = django_filters.ModelMultipleChoiceFilter(field_name='genres__name', to_field_name='name', queryset=Genres.objects.all())
    country = django_filters.ModelChoiceFilter(field_name='country__name', to_field_name='name', queryset=Country.objects.all())
    tags = django_filters.ModelMultipleChoiceFilter(field_name='tags__name', to_field_name='name', queryset=Tag.objects.all())
    fandoms = django_filters.ModelMultipleChoiceFilter(field_name='fandoms__name', to_field_name='name', queryset=Fandom.objects.all())

    is_adult = django_filters.BooleanFilter(method='filter_is_adult')


    class Meta:
        model = Book
        fields = ['genres', 'country', 'tags', 'fandoms', 'is_adult']


    def filter_is_adult(self, queryset, name, value):
        # Фильтруем книги на основе результата метода is_adult
        if value:
            return queryset.filter(is_adult=True)
        return queryset.exclude(is_adult=True)
