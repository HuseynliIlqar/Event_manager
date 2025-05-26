from django.contrib import admin
from .models import Event, Ticket, EventCategory

@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'start_time', 'end_time', 'location', 'is_active')
    list_filter = ('category', 'is_active', 'start_time')
    search_fields = ('name', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-start_time',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'event', 'ticket_type', 'seller', 'customer', 'price', 'is_paid', 'is_used', 'created_at')
    list_filter = ('ticket_type', 'is_paid', 'is_used', 'created_at')
    search_fields = ('ticket_id', 'event__name', 'seller__username', 'customer__username')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('ticket_id', 'event', 'ticket_type', 'seat_number')
        }),
        ('Pricing', {
            'fields': ('price', 'currency')
        }),
        ('Status', {
            'fields': ('is_paid', 'is_used')
        }),
    )
