from django.contrib import admin
from django.urls import path
from chatapp import views
from .views import *

urlpatterns = [
    # path('admin/', admin.site.urls),
    path("", views.index, name = "home"),
    path('groq/', groq_api, name='groq_api'),
    path('signup/', signup, name='signup'),
    path('signin/', signin, name='signin'),
    path('google_login/', views.google_login, name='google_login'),  # Step 1: Redirect to Google OAuth
    path('callback_google_trial/', views.callback_google_trial, name='google_callback'),  # Step 2: Handle OAuth callback
    path('refresh_token/', signin, name='refresh_token'),
    path('add_bot/', add_bot, name='add_bot'),
    path('get_all_bots/', get_all_bots, name='get_all_bots'),
    path('get_bot_by_id/', get_bot_by_id, name='get_bot_by_id'),
    path('chat_generation/', chat_generation, name='chat_generation'),
    path('show_chat/', show_chat, name='show_chat'),
    path('create_user_bots/', create_user_bots, name='create_user_bots'),
    path('get_image/', get_image, name='get_image'),
    
]

