from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Publications
from .serializers import PublicationsSerializer

# Get all publications sorted by last_updated
class GetAllPublications(APIView):
    
    def get(self, request):
        publications = Publications.objects.all().order_by('-last_updated')  # Sorted by last_updated
        serializer = PublicationsSerializer(publications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Get, update, and delete a specific publication by ID
class PublicationDetail(APIView):
    
    # Get a publication by ID
    def get(self, request, publication_id):
        publication = get_object_or_404(Publications, id=publication_id)
        serializer = PublicationsSerializer(publication)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Update a publication by ID
    def put(self, request, publication_id):
        publication = get_object_or_404(Publications, id=publication_id)
        serializer = PublicationsSerializer(publication, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a publication by ID
    def delete(self, request, publication_id):
        publication = get_object_or_404(Publications, id=publication_id)
        publication.delete()
        return Response({"message": "Publication deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
