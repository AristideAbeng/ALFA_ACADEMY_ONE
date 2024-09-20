from rest_framework.views import APIView
from rest_framework.response import Response
from Notifications.serializers import NotificationSerializer
from rest_framework import status
from authentication.models import User
from .models import Notification
from django.shortcuts import get_object_or_404
from authentication.models import User

class GetNotifications(APIView):

     def get(self, request, user_id):
        # Fetch the user
        user = get_object_or_404(User, id=user_id)

        # Get the unread notifications for the user
        unread_notifications = Notification.objects.filter(user=user, is_read=False).order_by('-created_at')

        # Serialize the unread notifications
        serializer = NotificationSerializer(unread_notifications, many=True)

        # Mark these notifications as read
        unread_notifications.update(is_read=True)

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)