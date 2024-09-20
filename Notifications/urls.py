# notifications/urls.py

from django.urls import path
from .views import GetNotifications,GetAllNotifications

urlpatterns = [
    path('notifications/<int:user_id>/', GetNotifications.as_view(), name='user-notifications'),
    path('all/<int:user_id>/', GetAllNotifications.as_view(), name='all user-notifications'),
]
