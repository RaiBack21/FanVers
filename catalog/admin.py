from django.contrib import admin
from .models import Book, Tag, Fandom, Country, Genres, Chapter, Comment
from .tasks import send_abandoned_notification
import logging

logger = logging.getLogger(__name__)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # actions = ['send_abandoned_notification']
    list_display = ['title', 'title_en', 'author', 'get_tags', 'get_fandoms', 'get_country', 'get_genres']
    list_filter = ['author', 'tags', 'fandoms', 'country', 'genres']
    search_fields = ['title', 'author__name']

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    def get_genres(self, obj):
        return ", ".join([genres.name for genres in obj.genres.all()])

    def get_fandoms(self, obj):
        return ", ".join([fandom.name for fandom in obj.fandoms.all()])

    def get_country(self, obj):
        return obj.country.name

    def get_chapter(self, obj):
        return ",".join([chapter.title for chapter in obj.chapters.all()])

    # DEBUG !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # def send_abandoned_notification(self, request, queryset):
    #     for book in queryset:
    #
    #         print("BOOOOOOK ID = " + book.id)
    #         logger.info("BOOOOOOK ID = " + book.id)
    #
    #         with open('C:\\Users\\user\\Desktop\\my_log.txt', 'w') as f:  # думаю тут помилка бо юзер не той
    #             f.write("BOOOOOOK ID = " + book.id)
    #             f.close()
    #
    #         send_abandoned_notification.delay(book.id)
    #     self.message_user(request, f"Уведомления отправлены для {queryset.count()} книг.")
    #
    # send_abandoned_notification.short_description = "Отправить уведомление о покинутой книге"

    # actions = [send_abandoned_notification]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Fandom)
class FandomAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Genres)
class GenresAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title ']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['text', 'owner' ,'parent']
    search_fields = [all]
