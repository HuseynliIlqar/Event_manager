from django.db import models
from django.conf import settings
from tickets.models import Ticket

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    PAYMENT_METHOD = (
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True)  # Hər ödəniş üçün unikal identifikator
    payment_system_id = models.CharField(max_length=100, blank=True, null=True)  # Xarici ödəniş sistemindən gələn ID
    payment_url = models.URLField(blank=True, null=True)  # Ödəniş səhifəsinin linki
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.ticket.ticket_id}"

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'ticket']  # Eyni istifadəçi eyni bilet üçün təkrar ödəniş edə bilməz

    @property
    def amount(self):
        return self.ticket.price

    @property
    def currency(self):
        return self.ticket.currency
