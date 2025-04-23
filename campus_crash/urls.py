from django.urls import path
from . import views
from .views import register, verify_email
from django.http import HttpResponse


app_name = 'campus_crash'
urlpatterns = [
 
    path('', views.index, name='index'),
    path('users/', views.user_list, name='user_list'),
    path('notifications/', views.notifications, name='notifications'),
   
    path('settings/', views.settings, name='settings'),
    path('logout/', views.logout_user, name='logout'),
    path('login/', views.login_user, name='login'),
    path("register/", views.register, name="register"),

    path("verify/<uidb64>/<token>/", views.verify_email, name="verify_email"),
    path('chat/<int:user_id>/', views.chat_view, name='chat_room'),



   
]


