from django.urls import include, path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('For-copyright-holders/', views.For_copyright_holders, name='For_copyright_holders'),
    path('user-agreement/', views.user_agreement, name='user_agreement'),
    path('Reference/', views.Reference, name='Reference'),
    path('Write-to-support/', views.Write_to_support, name='Write_to_support'),
    path('Contacts/', views.Contacts, name='Contacts'),
    path('money_problem/', views.money_problem, name='money_problem'),
    path('Suggest_improvements/', views.Suggest_improvements, name='Suggest_improvements'),
    path('thanks/', views.thanks, name='thanks'),
    path('FAQ/', views.faq, name='faq'),
    path("__debug__/", include("debug_toolbar.urls")),
]

handler404 = "main.views.page_not_found_view"
