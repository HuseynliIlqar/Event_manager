import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class TicketType(models.TextChoices):
    VIP = 'VIP', _('VIP')
    STANDARD = 'STANDARD', _('Standard')
    EARLY_BIRD = 'EARLY_BIRD', _('Early Bird')
    STUDENT = 'STUDENT', _('Student')
    SENIOR = 'SENIOR', _('Senior')
    CHILD = 'CHILD', _('Child')

class EventCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
    category = models.ForeignKey(EventCategory, on_delete=models.PROTECT, related_name='events')
    location = models.CharField(_('Location'), max_length=255)
    start_time = models.DateTimeField(_('Start Time'))
    end_time = models.DateTimeField(_('End Time'))
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')  # Seller
    max_participants = models.PositiveIntegerField(_('Max Participants'))
    current_participants = models.PositiveIntegerField(_('Current Participants'), default=0)
    image = models.ImageField(_('Image'), upload_to='event_images/', blank=True, null=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
        ordering = ['-start_time']


class Ticket(models.Model):
    ticket_id = models.CharField(max_length=50, unique=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sold_tickets')  # organizer
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchased_tickets')
    ticket_type = models.CharField(
        max_length=20,
        choices=TicketType.choices,
        default=TicketType.STANDARD,
        verbose_name=_('Ticket Type')
    )
    seat_number = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='AZN')
    is_paid = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_id = str(uuid.uuid4()).replace('-', '')[:12].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.event.name} ({self.get_ticket_type_display()})"

    class Meta:
        verbose_name = _('Ticket')
        verbose_name_plural = _('Tickets')
        ordering = ['-created_at']
