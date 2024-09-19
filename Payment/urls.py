from django.urls import path
from .views import PaymentStatusView,InitiatePaymentView, NotchPayWebhookView, VerifyPaymentView, PaymentSSEView

urlpatterns = [
    # Other URL patterns...
    
    # URL for handling payment status updates
    path('status/<int:user_id>/', PaymentStatusView.as_view(), name='payment-status'),
    path('initiate/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('webhook/', NotchPayWebhookView.as_view(), name='notchpay-webhook'),
     path('verify-payment/<str:reference>/', VerifyPaymentView.as_view(), name='verify-payment'),
     path('payment-status-stream/', PaymentSSEView.as_view(), name='payment_sse'),
]
