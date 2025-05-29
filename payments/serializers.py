from rest_framework import serializers
from .models import Payment
from tickets.models import Ticket

class PaymentSerializer(serializers.ModelSerializer):
    # Bilet məlumatlarını avtomatik gətirir
    ticket_id = serializers.CharField(source='ticket.ticket_id', read_only=True)
    amount = serializers.DecimalField(source='ticket.price', max_digits=10, decimal_places=2, read_only=True)
    currency = serializers.CharField(source='ticket.currency', read_only=True)

    class Meta:
        model = Payment
        # Serialize ediləcək sahələr
        fields = [
            'id',
            'transaction_id',
            'ticket_id',
            'amount',
            'currency',
            'payment_method',
            'status',
            'payment_url',
            'created_at'
        ]
        # Dəyişdirilə bilməyən sahələr
        read_only_fields = [
            'id',
            'transaction_id',
            'ticket_id',
            'amount',
            'currency',
            'status',
            'payment_url',
            'created_at'
        ] 