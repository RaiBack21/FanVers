from django.urls import path, include
from .views import login_modal_view, signup_modal_view, logout_view, ProfileDetail, ProfileUpdate
from . import views
from .dialogs import get_or_create_dialog
from rest_framework_simplejwt.views import TokenObtainPairView

app_name = 'users'


urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('login_modal/', login_modal_view, name='login_modal'),
    path('signup_modal/', signup_modal_view, name='signup_modal'),
    path('logout/', logout_view, name='logout'),
    path('profile/', ProfileDetail.as_view(), name='profile'),
    path('profile/detail/<str:username>/', views.OtherUserProfileDetail.as_view(), name='other_profile_detail'),
    path('profile/list/', views.ProfileListView.as_view(), name='translators'),
    path('edit-account/', ProfileUpdate.as_view(), name='ProfileUpdate'),
    path('purchase-chapter/<int:chapter_id>/', views.purchase_chapter, name='purchase_chapter'),
    path('add_funds/', views.add_funds, name='add_funds'),
    path('users/purchase-chapter/<int:chapter_id>/', views.purchase_chapter, name='purchase_chapter'),
    path('commission-stats/', views.commission_stats, name='commission_stats'),
    path('dialogs/', views.dialogs_list, name='dialogs_list'),
    path('dialog/<int:dialog_id>/', views.dialog_view, name='dialog_view'),
    path('dialog/create/', views.create_dialog, name='create_dialog'),
    path('user/<str:username>/dialog/', views.create_dialog, name='create_dialog'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('save-token/', views.save_token, name='save_token'),
]
