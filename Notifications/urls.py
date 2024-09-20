# notifications/urls.py

from django.urls import path
from .views import GetNotifications

urlpatterns = [
    path('notifications/<int:user_id>/', GetNotifications.as_view(), name='user-notifications'),
]
