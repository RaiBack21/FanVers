from django.urls import path
from .views import book_create, edit_chapter, setting_book,  TitleAutocompleteView,   GenresAutocompleteView, TagsAutocompleteView, FandomAutocompleteView, BookAdultAutocompleteView, BookNotAdultAutocompleteView
from .forms import TagAutocomplete, FandomAutocomplete, CountryAutocomplete, GenresAutocomplete
from .views import (
    Catalog, BookBase, TagList, TagDetail, GenresList, GenresDetail, FandomList, FandomDetail, CountryList, CountryDetail, ChapterCreate, ChapterDetail)
from .views import become_translator, become_freelancer
from .views import change_group, NotificationListAPIView, BookSearchView, BookmarkActionView
from . import views
from .views import *
from django.http import HttpResponse

app_name = 'catalog'

urlpatterns = [
    path('', Catalog.as_view(), name='catalog'),
    path('search/', BookSearchView.as_view(), name='search'),
    path('search_results/', Search.as_view(), name='search_results'),
    path('books/new/', book_create, name='book_create'),
    path('book/<slug:book_slug_setting_book>/adv/', book_advertisement_settings, name='book_advertisement_settings'),
    path('book/<slug:book_slug_setting_book>/ajax_cost/', ajax_cost, name='ajax_cost'),
    path('book/<slug:book_slug_setting_book>/ajax_cost_sum/', ajax_cost_sum, name='ajax_cost_sum'),
    path('book/<slug:book_slug>/create_chapter/', ChapterCreate.as_view(), name='create_chapter'),
    path('book/<slug:book_slug>/<slug:chapter_slug>/', ChapterDetail.as_view(), name='chapter_detail'),
    path('book/<slug:book_slug>/<slug:chapter_slug>/edit/', edit_chapter, name='chapter_edit'),
    path('tags-autocomplete/', TagAutocomplete.as_view(), name='tags-autocomplete'),
    path('fandoms-autocomplete/', FandomAutocomplete.as_view(), name='fandoms-autocomplete'),
    path('country-autocomplete/', CountryAutocomplete.as_view(), name='country-autocomplete'),
    path('genres-autocomplete/', GenresAutocomplete.as_view(), name='genres-autocomplete'),
    path('book/<slug:slug>/', BookBase.as_view(), name='Book_Base'),
    path('book/<slug:book_slug_setting_book>', setting_book, name='setting_book'),
    path('tags/', TagList.as_view(), name='tag_list'),
    path('tags/<int:pk>/', TagDetail.as_view(), name='tag_detail'),
    path('fandoms/', FandomList.as_view(), name='fandom_list'),
    path('fandoms/<int:pk>/', FandomDetail.as_view(), name='fandom_detail'),
    path('genres/', GenresList.as_view(), name='genres_list'),
    path('genres/<int:pk>/', GenresDetail.as_view(), name='genres_detail'),
    path('countries/', CountryList.as_view(), name='country_list'),
    path('countries/<int:pk>/', CountryDetail.as_view(), name='country_detail'),
    path('change_group/<str:new_group_name>/', change_group, name='change_group'),
    path('become_translator/', become_translator, name='become_translator'),
    path('become_freelancer/', become_freelancer, name='become_freelancer'),
    path('like_comment/<int:comment_id>/', views.LikeCommentView.as_view(), name="like_comment"),
    path('dislike_comment/<int:comment_id>/', views.DislikeCommentView.as_view(), name="dislike_comment"),
    path('delete_comment/<int:comment_id>/', views.DeleteCommentView.as_view(), name="delete_comment"),
    path('rate_book/', views.rate_book, name='rate_book'),
    path('get_user_rating', views.get_user_rating, name='get_user_rating'),
    path('quality_translation/', views.quality_translation, name='quality_translation'),
    path('get_user_quality/', views.get_user_quality, name='get_user_quality'),
    path('ajax/autocomplete/title/', TitleAutocompleteView.as_view(), name='title_autocomplete'),
    path('ajax/autocomplete/genres/', GenresAutocompleteView.as_view(), name='genres_autocomplete'),
    path('ajax/autocomplete/tags/', TagsAutocompleteView.as_view(), name='tags_autocomplete'),
    path('ajax/autocomplete/fandom/', FandomAutocompleteView.as_view(), name='fandom_autocomplete'),
    path('ajax/autocomplete/adult/', BookAdultAutocompleteView.as_view(), name='book_adult_autocomplete'),
    path('ajax/autocomplete/not-adult/', BookNotAdultAutocompleteView.as_view(), name='book_not_adult_autocomplete'),
    path('get_additional_data/', views.get_additional_data, name='get_additional_data'),
    path('api/notifications/', NotificationListAPIView.as_view(), name='notification-list'),
    path('notifications/', NotificationListView.as_view(), name='notification-lists'),
    path('catalog/book/<slug:slug>/bookmark/', BookmarkActionView.as_view(), name='bookmark_action'),
    path('catalog/bookmarks/', BookmarkListView.as_view(), name='bookmarks'),
    path('catalog/bookmarks/all/', get_bookmarks_all, name='all'),
    path('catalog/bookmarks/read/', get_bookmarks_read, name='read'),
    path('catalog/bookmarks/special/', get_bookmarks_special, name='special'),
    path('catalog/bookmarks/in_plans/', get_bookmarks_in_plans, name='in_plans'),
    path('catalog/bookmarks/left/', get_bookmarks_left, name='left'),
    path('catalog/bookmarks/end_read/', get_bookmarks_end_read, name='end_read'),
    path('catalog/mytranslations/', OwnTranslationsListView.as_view(), name='own-translations'),
    path('catalog/left_translations/', LeftTranslationsListView.as_view(), name='left-translations'),
]
