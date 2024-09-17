from django.shortcuts import render
from .models import User
from . import serializers
from rest_framework.views import APIView
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from django.contrib.auth.hashers import make_password,check_password
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly,IsAdminUser
import random
from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from django.db import transaction

# Create your views here.
class UserCreateView(APIView):

    serializer_class = serializers.UserCreationSerializer
    parser_classes = [FormParser,MultiPartParser]
    

    def post(self,request,format=None):

        data = request.data

        serializer = self.serializer_class(data=data)

        if serializer.is_valid():

            serializer.save()

            return Response(data={"data":serializer.data,"status":201},status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors ,status=status.HTTP_400_BAD_REQUEST)

class UserGetDetailView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserDetailSerializer  # Update to appropriate serializer

    def get(self, request, user_email):
        # Ensure that the user is either an admin or the authenticated user
        if not request.user.is_staff and user_email != request.user.email:
            return Response({"error": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = get_object_or_404(User, email=user_email)
        serializer = self.serializer_class(instance=user, context={'request': request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_email):
        # Retrieve the user from the database
        user = get_object_or_404(User, email=user_email)

        # Check if the user making the request is the same as the user being updated
        if user.email != request.user.email:
            return Response(data={"error": "You don't have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        # Update the user
        serializer = self.serializer_class(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

