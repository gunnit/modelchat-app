from django.contrib import admin
from django.urls import path, include
from chat import views


urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/process_message/', views.process_message, name='process_message'),
    path('telegram_webhook/', views.telegram_webhook, name='telegram_webhook'),
    path('model_dashboard/', views.model_dashboard, name='model_dashboard'),
    path('fan_dashboard/', views.fan_dashboard, name='fan_dashboard'),
    path('after_login_redirect/', views.after_login_redirect, name='after_login_redirect'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('update_digital_persona/', views.update_digital_persona, name='update_digital_persona'),
]
