from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from chat import views


urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('home/', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/process_message/', views.process_message, name='process_message'),
    path('telegram_webhook/', views.telegram_webhook, name='telegram_webhook'),
    path('model_dashboard/', views.model_dashboard, name='model_dashboard'),
    path('fan_dashboard/', views.fan_dashboard, name='fan_dashboard'),
    path('after_login_redirect/', views.after_login_redirect, name='after_login_redirect'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('update_digital_persona/', views.update_digital_persona, name='update_digital_persona'),
    path('how_it_works/', views.how_it_works, name='how_it_works'),
    # in urls.py
    path('chat_with_model/<str:model_username>/', views.chat_with_model, name='chat_with_model'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
