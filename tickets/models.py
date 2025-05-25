import uuid
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')  # Seller
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Ticket(models.Model):
    ticket_id = models.CharField(max_length=50, unique=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sold_tickets')  # organizer
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchased_tickets')
    seat_number = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='AZN')
    is_paid = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticket_id} - {self.event.name}"
