from django import forms
from .models import Book, Tag, Fandom, Genres, Country, Chapter, Comment
from dal import autocomplete
from django_ckeditor_5.widgets import CKEditor5Widget
from django.forms import ModelForm


class BookForm(forms.ModelForm):


    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    fandoms = forms.ModelMultipleChoiceField(
        queryset=Fandom.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    genres = forms.ModelMultipleChoiceField(
        queryset=Genres.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )

    status = forms.ChoiceField(choices=Book.STATUS_CHOICES)

    is_adult = forms.BooleanField(required=False)

    title = forms.CharField()

    title_en = forms.CharField()

    author = forms.CharField()

    class Meta:
        model = Book
        fields = ['title', 'title_en', 'author', 'tags', 'fandoms', 'country', 'image', 'images', 'genres', 'description',
                  'is_adult', 'status']

        widgets = {
            'description': forms.Textarea(attrs={'rows': 10, 'cols': 10}),
            'status': forms.HiddenInput(),
        }

        labels = {
            'description': 'Опис'
        }



class EditBookForm(forms.ModelForm):


    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    fandoms = forms.ModelMultipleChoiceField(
        queryset=Fandom.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    genres = forms.ModelMultipleChoiceField(
        queryset=Genres.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )

    status = forms.ChoiceField(choices=Book.STATUS_CHOICES)
    is_adult = forms.BooleanField(required=False)
    title = forms.CharField()
    title_en = forms.CharField()
    author = forms.CharField()

    class Meta:
        model = Book
        fields = ['title', 'title_en', 'author', 'tags', 'fandoms', 'country', 'image', 'images', 'genres', 'description',
                  'is_adult', 'status']

        widgets = {
            'description': forms.Textarea(attrs={'rows': 10, 'cols': 10}),
            'status': forms.HiddenInput(),
        }

        labels = {
            'description': 'Опис'
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Устанавливаем виджет для status
        self.fields['status'].widget = forms.Select(choices=Book.STATUS_CHOICES)

        self.fields['tags'].initial = self.instance.tags.all()
        self.fields['fandoms'].initial = self.instance.fandoms.all()
        self.fields['country'].initial = self.instance.country
        self.fields['genres'].initial = self.instance.genres.all()
    # Методы для получения начальных данных
    def get_initial_tags(self):
        return self.instance.tags.all()

    def get_initial_tags(self):
        return self.instance.tags.all()

    def get_initial_fandoms(self):
        return self.instance.fandoms.all()

    def get_initial_country(self):
        return self.instance.country

    def get_initial_genres(self):
        return self.instance.genres.all()

class TagAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Tag.objects.none()

        qs = Tag.objects.all().order_by('name')

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

class FandomAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Fandom.objects.none()

        qs = Fandom.objects.all().order_by('name')

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

class GenresAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Genres.objects.none()

        qs = Genres.objects.all().order_by('name')

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

class CountryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Country.objects.none()

        qs = Country.objects.all().order_by('name')

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['title', 'content', 'file', 'price']
        widgets = {
            'content': CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"},
                config_name="default"  # Вы можете указать другой config_name в зависимости от настроек CKEditor5
            ),
            'file': forms.FileInput(attrs={'accept': 'text/plain'}),
        }
        help_texts = {
            'file': 'You can upload a text file instead of typing in the content.',
        }





class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {'text': forms.Textarea()}

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control input-box form-ensurance-header-control', 'placeholder': 'Ваш коментар'})
