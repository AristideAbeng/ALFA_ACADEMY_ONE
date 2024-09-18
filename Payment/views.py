from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Payment
from authentication.models import User
from .serializers import PaymentSerializer

class PaymentStatusView(APIView):
    def post(self, request, user_id):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            # Extract validated data
            payment_status = serializer.validated_data['payment_status']
            transaction_id = serializer.validated_data['transaction_id']
            amount = serializer.validated_data['amount']
            payment_method = serializer.validated_data['payment_method']

            # Optionally, save the payment information
            Payment.objects.create(
                user_id=user_id,
                transaction_id=transaction_id,
                status=payment_status,
                amount=amount,
                method=payment_method
            )

            # Respond based on payment status
            if payment_status == 'success':
                return Response({"message": "Payment successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
