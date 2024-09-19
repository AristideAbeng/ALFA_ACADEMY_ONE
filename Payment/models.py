from django.db import models
from authentication.models import User

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    PAYMENT_CURRENCY_CHOICES = [
        ('XAF', 'XAF'),

    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    currency = models.CharField(max_length=7, choices=PAYMENT_CURRENCY_CHOICES, default='XAF')
    transaction_id = models.CharField(max_length=100, null=True, blank=True)  # Optional, if payment gateway provides this
    payment_method = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Payment by {self.user.email} - Status: {self.status}"