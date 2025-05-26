from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'transaction_id', 'amount', 'currency', 'payment_method', 
                 'status', 'created_at', 'updated_at', 'description']
        read_only_fields = ['transaction_id', 'created_at', 'updated_at'] 