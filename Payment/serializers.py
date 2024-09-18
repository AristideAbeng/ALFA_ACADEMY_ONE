from rest_framework import serializers

class PaymentSerializer(serializers.Serializer):

    user_id = serializers.IntegerField()  # The ID of the user making the payment
    payment_status = serializers.ChoiceField(choices=[('success', 'Success'), ('failed', 'Failed')])  # Payment status
    transaction_id = serializers.CharField(max_length=255, required=True)  # Unique transaction ID
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)  # Payment amount
    payment_method = serializers.CharField(max_length=100)  # Payment method (e.g., credit card, mobile money)
   

    def validate(self, data):
        # You can add custom validation here if necessary
        return data
