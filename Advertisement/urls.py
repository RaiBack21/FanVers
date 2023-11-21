from django.urls import path
from .views import *


app_name = 'Advertisement'

urlpatterns = [
       # path('catalog/books/new/', book_advertisement_settings, name='book_advertisement_settings'),
       # path('catalog/books/new/ajax_cost/', ajax_cost, name='ajax_cost'),
       # path('catalog/books/new/ajax_cost_sum/', ajax_cost_sum, name='ajax_cost_sum'),
       path('autocomplete/fandom/', autocomplete_fandom, name='autocomplete_fandom'),
       path('autocomplete/genre/', autocomplete_genre, name='autocomplete_genre'),
       path('autocomplete/tag/', autocomplete_tag, name='autocomplete_tag'),
]
