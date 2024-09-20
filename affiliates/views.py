from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Affiliate
from authentication.models import User

class GetAffiliateByUserID(APIView):

    def get(self, request, user_id):
        # Try to retrieve the Affiliate linked to the provided user_id
        user = get_object_or_404(User, id=user_id)
        affiliate = get_object_or_404(Affiliate, user=user)
        
        # Return the affiliate data
        return Response({
            'user': affiliate.user.id,
            'referrer': affiliate.referrer.user.id if affiliate.referrer else None,
            'direct_points': affiliate.direct_points,
            'indirect_points': affiliate.indirect_points,
            'withdrawed_points':affiliate.withdrawed_points
        }, status=status.HTTP_200_OK)

class GetAffiliateStatisticsByUserID(APIView):

    def get(self, request, user_id):
        # Get the user and their affiliate object
        user = get_object_or_404(User, id=user_id)
        affiliate = get_object_or_404(Affiliate, user=user)
        
        # Get all affiliates that the user referred (direct referrals)
        direct_affiliates = Affiliate.objects.filter(referrer=affiliate)
        
        # Initialize counters for active and inactive affiliates
        active_affiliates = 0
        inactive_affiliates = 0
        
        # Check each direct affiliate
        for direct_affiliate in direct_affiliates:
            # Check if this affiliate has their own referrals (i.e., they are active)
            if Affiliate.objects.filter(referrer=direct_affiliate).exists():
                active_affiliates += 1
            else:
                inactive_affiliates += 1

        # Return the counts for active and inactive affiliates
        return Response({
            'user_id': user.id,
            'active_affiliates': active_affiliates,
            'inactive_affiliates': inactive_affiliates,
        }, status=status.HTTP_200_OK)