import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Payment
from authentication.models import User
from .serializers import PaymentSerializer

class PaymentStatusView(APIView):
    def post(self, request, user_id):
        # Serializer validation
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            # Extract validated data
            payment_status = serializer.validated_data['payment_status']
            transaction_id = serializer.validated_data['transaction_id']
            amount = serializer.validated_data['amount']
            payment_method = serializer.validated_data['payment_method']

            # Make API request to Notch Pay for verification
            response = requests.get(
                f"{settings.NOTCH_PAY_BASE_URL}/payments/{transaction_id}/verify",
                headers={
                    "Authorization": f"Bearer {settings.NOTCH_PAY_PRIVATE_KEY}"
                }
            )

            # Check if the request to Notch Pay was successful
            if response.status_code == 200:
                notchpay_response = response.json()

                # Verify the transaction status from Notch Pay
                notchpay_status = notchpay_response.get('status')
                if notchpay_status == 'success':
                    # Payment successful, save to database
                    Payment.objects.create(
                        user_id=user_id,
                        transaction_id=transaction_id,
                        status='success',
                        amount=amount,
                        method=payment_method
                    )

                    # Respond with success
                    return Response({"message": "Payment successful"}, status=status.HTTP_200_OK)
                else:
                    # Payment failed, respond with failure
                    return Response({"message": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Handle error from Notch Pay
                return Response({"error": "Error verifying payment with Notch Pay"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Invalid serializer data
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InitiatePaymentView(APIView):

    def post(self, request):
        # Fetch the payment details from the frontend request
        amount = request.data.get('amount')
        currency = request.data.get('currency')
        email = request.data.get('email')

        # Prepare the request payload
        payload = {
            "amount": amount,
            "currency": currency,
            "email": email,
            "redirect_url": "http://localhost:4200/payment",  # Update with the correct URL
        }

        # Make the API request to Notch Pay
        response = requests.post(
            f"{settings.NOTCH_PAY_BASE_URL}/payments",
            headers={
                "Authorization": f"Bearer {settings.NOTCH_PAY_PRIVATE_KEY}",
                "Content-Type": "application/json"
            },
            json=payload
        )

        if response.status_code == 201:
            # Return payment URL to the frontend to redirect user
            payment_url = response.json().get('data').get('link')
            return Response({"payment_url": payment_url}, status=status.HTTP_201_CREATED)
        else:
            return Response(response.json(), status=response.status_code)

# Handle Webhooks for Payment Verification
class NotchPayWebhookView(APIView):

    
    def post(self, request):
        # This is triggered when Notch Pay sends a payment verification
        payment_data = request.data

        # Verify the payment status and handle it accordingly
        if payment_data.get('status') == 'success':
            # Update the payment status in your database
            # You can fetch the user/order associated with this payment
            return Response({"message": "Payment verified"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)