# urls.py
from django.conf import settings
from django.urls import path
from .views import api_login, api_logout, api_register, get_csrf_token, notifications, profile_settings
from .views import LoginView, RegistrationView, LogoutView  # Your existing views

urlpatterns = [
    # Web views (keep your existing web views)
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('notification/', notifications, name='notification'),
    path('profile-settings/', profile_settings, name='profile-settings'),
 
    
    # API endpoints
    path('v1/register/', api_register, name='api_register'),
    path('v1/login/', api_login, name='api_login'),
    path('v1/logout/', api_logout, name='api_logout'),
    path('v1/csrf/', get_csrf_token, name='get_csrf'),

]

