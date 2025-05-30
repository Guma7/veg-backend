from django.urls import path
from . import views

urlpatterns = [
    path('delete-all/', views.delete_all_users, name='delete_all_users'),
    path('', views.get_user_info, name='user_info'),
    path('me/', views.get_user_info, name='current_user_info'),
    path('profile/', views.update_profile, name='update_profile'),
    path('<str:username>/', views.get_user_by_username, name='get_user_by_username'),
]