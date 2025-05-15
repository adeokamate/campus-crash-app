from django.urls import path
from . import views
from .views import register, verify_email
from django.http import HttpResponse


app_name = 'campus_crash'
urlpatterns = [
 

    # General Navigation
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('users/', views.user_list, name='user_list'),
  
    path('messages/', views.messages_view, name='messages'),
   path('settings/', views.settings_view, name='settings'),
    path('logout/', views.logout_user, name='logout'),
    path('login/', views.login_user, name='login'),

    # Registration & Verification
    path('register/', views.register, name='register'),
    path('verify/', views.verify_code, name='verify_code'),
    path('verify/<uidb64>/<token>/', views.verify_email, name='verify_email'),

    # Chat System
    path('chat/id/<int:chat_id>/', views.chat_detail, name='chat_detail'),           # View chat by chat ID
    path('chat/user/<int:user_id>/', views.chat_view, name='chat_with_user'),         # Start/view chat with a user

    # Match Making
    path('match_make/', views.match_make, name='match_make'),

   path('support/', views.support_view, name='support'),


]

