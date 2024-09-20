from rest_framework import serializers
from .models import Publications

class PublicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publications
        fields = ['id', 'user', 'title', 'content', 'image_url', 'date_published', 'last_updated']
        read_only_fields = ['id', 'date_published', 'last_updated']
