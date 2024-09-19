from django.db import transaction
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Payment
from authentication.models import User
from .serializers import PaymentSerializer
import logging
import json
import hmac
import hashlib
from django.http import JsonResponse
from Events.models import Event
from django.http import StreamingHttpResponse
import time
from affiliates.models import Affiliate


logger = logging.getLogger(__name__)


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
        amount = 3000
        currency = 'XAF'
        description = request.data.get('description', '')
        reference = request.data.get('reference', '')
        callback = request.data.get('callback', '')
        customer = request.data.get('customer')
        channel = request.data.get('channel','cm.mobile')  # Channel for payment

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
                    response_data = charge_response.json()
                    response_data['reference'] = transaction_id
                    return Response(data=response_data, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response(charge_response.json(), status=charge_response.status_code)
            else:
                return Response({"error": "Payment initialization failed or invalid amount/currency"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(response.json(), status=response.status_code)


class NotchPayWebhookView(APIView):

    def post(self, request, *args, **kwargs):
        # Fetch the secret key from environment variables
        logger.info('Webhook received.')

        secret_key = settings.NOTCH_PAY_PUBLIC_KEY.encode('utf-8')
        calculated_hash = hmac.new(
            secret_key,
            request.body,
            hashlib.sha256
        ).hexdigest()

        notch_signature = request.headers.get('x-notch-signature', '')

        logger.debug(f"Calculated hash: {calculated_hash}")
        logger.debug(f"Notch signature: {notch_signature}")

        #if calculated_hash != notch_signature:
        #    logger.warning('Invalid signature detected.')
        #    return JsonResponse({"error": "Invalid signature"}, status=400)

        # Parse the event data from the request body
        event = json.loads(request.body)
        event_id = event.get('id')

        # Idempotency: Check if this event has already been processed
        if Event.objects.filter(event_id=event_id).exists():
            logger.info('Duplicate event received.')
            return JsonResponse({"status": "duplicate"}, status=200)

        # Store the event ID to prevent duplicate processing
        Event.objects.create(event_id=event_id)

        # Handle the event type
        event_type = event['event']
        
        if event_type == 'payment.complete':
            # Update payment status in the database
            logger.info(f"Handling payment completion for event ID: {event_id}")
            self.update_payment_status(event)

        # Add more event types here as needed

        # Immediately return a 200 response to acknowledge receipt of the webhook
        return JsonResponse({"status": "success"}, status=200)

    def update_payment_status(self, event):
        # Extract the transaction ID from event data
        transaction_id = event['data']['reference']
        payment_status = event['data']['status']

        # Fetch the payment from the database using the transaction ID
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
            if payment.status != payment_status:
                # Update the payment status
                payment.status = payment_status
                payment.save()
        except Payment.DoesNotExist:
            # Handle case if the payment is not found
            logger.info(f"Payment to update not found")
            pass

   

class VerifyPaymentView(APIView):

    @transaction.atomic  # Ensures all operations inside this method are wrapped in a transaction
    def get(self, request, reference):
        # Make the API request to verify the payment using the reference
        response = requests.get(
            f"{settings.NOTCH_PAY_BASE_URL}/payments/{reference}",
            headers={
                "Authorization": settings.NOTCH_PAY_PUBLIC_KEY,  # Use your public key here
                "Content-Type": "application/json"
            }
        )

        if response.status_code == 200:
            # Extract payment data from the response
            notchpay_response = response.json()
            logger.info(f"NotchPayResponse For payment_verification: {notchpay_response}")
            payment_status = notchpay_response.get('transaction', {}).get('status', 'unknown')
            transaction_reference = notchpay_response.get('transaction', {}).get('reference', '')
            amount = notchpay_response.get('transaction', {}).get('amount', 0)
            currency = notchpay_response.get('transaction', {}).get('currency', '')

            # Update the payment status in your database
            Payment.objects.filter(transaction_id=transaction_reference).update(
                status=payment_status,
                amount=amount,
                currency=currency
            )

            # Handle affiliate logic if payment is complete
            if payment_status == 'complete':
                # Get the user who made the payment
                payment = Payment.objects.get(transaction_id=transaction_reference)
                user = payment.user

                # Check if the user is already an affiliate, if not create an entry
                affiliate, created = Affiliate.objects.get_or_create(user=user)

                if created:
                    # The user has a referrer_id, we assign it to the affiliate
                    if user.referrer_id:
                        try:
                            referrer = User.objects.get(id=user.referrer_id)
                            affiliate.referrer = referrer.affiliate
                            affiliate.save()
                        except User.DoesNotExist:
                            logger.error("Referrer does not exist")

                # Handle affiliate points logic (for direct and indirect referrers)
                if affiliate.referrer:
                    # Direct referrer gets 1500 points
                    referrer_affiliate = affiliate.referrer
                    referrer_affiliate.direct_points += 1500
                    referrer_affiliate.save()

                    # Indirect referrer (Level 2) gets 150 points
                    if referrer_affiliate.referrer:
                        indirect_referrer_affiliate = referrer_affiliate.referrer
                        indirect_referrer_affiliate.indirect_points += 150
                        indirect_referrer_affiliate.save()

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