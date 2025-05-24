from rest_framework import serializers
from .models import Event, Ticket

class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'organizer']


class TicketSerializer(serializers.ModelSerializer):
    event = serializers.StringRelatedField(read_only=True)
    seller = serializers.StringRelatedField(read_only=True)
    customer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['created_at']
