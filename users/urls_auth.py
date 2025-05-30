from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.update_profile, name='update_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('me/', views.get_user_info, name='user_info'),
    path('csrf/', views.get_csrf_token, name='get_csrf_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]