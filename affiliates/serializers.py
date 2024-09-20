from rest_framework import serializers
from .models import Affiliate, User

class AffiliateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Affiliate
        fields = ['user', 'referrer', 'points','withdrawed_points']

    def create(self, validated_data):
        # This might be expanded to include custom logic
        return super().create(validated_data)
