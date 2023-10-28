from django.contrib import admin
from django.urls import path, include
from chat import views


urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/process_message/', views.process_message, name='process_message'),
    path('telegram_webhook/', views.telegram_webhook, name='telegram_webhook'),
]
