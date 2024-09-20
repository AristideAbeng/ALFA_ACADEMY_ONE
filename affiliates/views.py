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
