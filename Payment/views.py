import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Payment
from authentication.models import User
from .serializers import PaymentSerializer
import logging

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

        # Extract payment details from the request
        user_id = request.data.get('user_id')  # Ensure user_id is passed in the request
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the User instance from the user_id
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Extract payment details from the request
        amount = request.data.get('amount')
        currency = request.data.get('currency')
        description = request.data.get('description', '')
        reference = request.data.get('reference', '')
        callback = request.data.get('callback', '')
        customer = request.data.get('customer')
        channel = request.data.get('channel')  # Channel for payment

        if not customer or not customer.get('email') and not customer.get('phone'):
            return Response({"error": "Customer must have either an email or phone number."}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare data for Notch Pay API
        payment_data = {
            "amount": amount,
            "currency": currency,
            "description": description,
            "reference": reference,
            "callback": callback,
            "customer": customer
        }

        # Make the API request to Notch Pay
        response = requests.post(
            f"{settings.NOTCH_PAY_BASE_URL}/payments",
            headers={
                "Authorization": f"{settings.NOTCH_PAY_PUBLIC_KEY}",  # Replace with your actual public key
                "Content-Type": "application/json"
            },
            json=payment_data
        )

        if response.status_code == 201:
            response_data = response.json()
            transaction_id = response_data['transaction']['reference']
            transaction_amount = response_data['transaction']['amount']
            transaction_currency = response_data['transaction']['currency']
            transaction_status = response_data['transaction']['status']
            
            # Proceed with charge initiation
            if response_data['status'] == 'Accepted' and transaction_amount == amount and transaction_currency == currency:
                charge_data = {
                    "channel": channel,
                    "data": {
                        "phone": customer.get('phone')
                    }
                }

                # Initiate the charge
                charge_response = requests.put(
                    f"{settings.NOTCH_PAY_BASE_URL}/payments/{transaction_id}",
                    headers={
                        "Authorization": f"{settings.NOTCH_PAY_PUBLIC_KEY}",
                        "Content-Type": "application/json"
                    },
                    json=charge_data
                )

                if charge_response.status_code == 202:
                    # Save transaction details if necessary
                    Payment.objects.create(
                        transaction_id=transaction_id,
                        amount=amount,
                        status='pending',  # Update status as needed
                        payment_method=channel,
                        user=user # If applicable
                    )
                    return Response(charge_response.json(), status=status.HTTP_202_ACCEPTED)
                else:
                    return Response(charge_response.json(), status=charge_response.status_code)
            else:
                return Response({"error": "Payment initialization failed or invalid amount/currency"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(response.json(), status=response.status_code)


class NotchPayWebhookView(APIView):
    def post(self, request):
        # Log the incoming webhook request for debugging
        logger = logging.getLogger(__name__)
        logger.info(f"Webhook received: {request.data}")

        # Extract the event and data from the request
        event = request.data.get('event')
        data = request.data.get('data')

        if not event or not data:
            return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if event == 'payment.initialized':
                # Handle payment initialized event
                # You can save this to the database or log it for further processing
                logger.info(f"Payment initialized: {data}")
                return Response({"message": "Payment initialized received"}, status=status.HTTP_200_OK)

            elif event == 'payment.complete':
                # Handle payment complete event
                logger.info(f"Payment completed: {data}")
                # Process the payment completion
                return Response({"message": "Payment complete received"}, status=status.HTTP_200_OK)

            else:
                # Unrecognized event type
                logger.warning(f"Unrecognized event type: {event}")
                return Response({"error": "Unrecognized event type"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Log the exception for debugging
            logger.error(f"Error processing webhook: {e}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyPaymentView(APIView):

    def get(self, request, reference):
        # Make the API request to verify the payment using the reference
        response = requests.get(
            f"{settings.NOTCH_PAY_BASE_URL}/payments/{reference}",
            headers={
                "Authorization": f"Bearer {settings.NOTCH_PAY_PUBLIC_KEY}",  # Use your public key here
                "Content-Type": "application/json"
            }
        )

        if response.status_code == 200:
            # Extract payment data from the response
            notchpay_response = response.json()
            payment_status = notchpay_response.get('payment', {}).get('status', 'unknown')
            transaction_reference = notchpay_response.get('payment', {}).get('reference', '')
            amount = notchpay_response.get('payment', {}).get('amount', 0)
            currency = notchpay_response.get('payment', {}).get('currency', '')

            # Update the payment status in your database
            Payment.objects.filter(transaction_id=transaction_reference).update(
                status=payment_status,
                amount=amount,
                currency=currency
            )

            # Return the payment status
            return Response({
                "status": "success",
                "payment_status": payment_status,
                "reference": transaction_reference,
                "amount": amount,
                "currency": currency,
            }, status=status.HTTP_200_OK)
        else:
            # Handle error response from Notch Pay API
            return Response({
                "error": "Failed to verify payment",
                "details": response.json()
            }, status=response.status_code)