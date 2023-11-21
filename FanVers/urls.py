from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('catalog/', include(('catalog.urls', 'catalog'), namespace='catalog')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('Advertisement/', include(('Advertisement.urls', 'Advertisement'), namespace='Advertisement')),
    path('ckeditor/', include('ckeditor_uploader.urls')), #текстовый редактор CKEditor
    re_path(r'^public/(?P<path>.*)$', serve, {'document_root': settings.BASE_DIR / 'public'}), #временное отображение папки public

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = "main.views.page_not_found_view"
