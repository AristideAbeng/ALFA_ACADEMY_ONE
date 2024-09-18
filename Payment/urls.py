from django.urls import path
from .views import PaymentStatusView

urlpatterns = [
    # Other URL patterns...
    
    # URL for handling payment status updates
    path('status/<int:user_id>/', PaymentStatusView.as_view(), name='payment-status'),
]
