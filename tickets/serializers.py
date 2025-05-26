from rest_framework import serializers
from .models import Event, Ticket, EventCategory

class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    category = EventCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=EventCategory.objects.all(),
        write_only=True,
        source='category'
    )

    class Meta:
        model = Event
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(),
        write_only=True,
        source='event'
    )
    seller = serializers.ReadOnlyField(source='seller.username')
    customer = serializers.ReadOnlyField(source='customer.username')
    ticket_type_display = serializers.CharField(source='get_ticket_type_display', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'ticket_id', 'event', 'event_id', 'ticket_type', 'ticket_type_display',
            'seller', 'customer', 'price', 'currency', 'seat_number',
            'is_paid', 'is_used', 'created_at'
        ]
        read_only_fields = ('ticket_id', 'created_at')

