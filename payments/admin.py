from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # Admin panelində göstəriləcək sahələr
    list_display = ('transaction_id', 'user', 'ticket', 'amount', 'currency', 'payment_method', 'status', 'created_at')
    
    # Filterlər
    list_filter = ('status', 'payment_method', 'created_at')
    
    # Axtarış sahələri
    search_fields = ('transaction_id', 'user__username', 'ticket__ticket_id')
    
    # Dəyişdirilə bilməyən sahələr
    readonly_fields = ('transaction_id', 'payment_system_id', 'created_at', 'updated_at')
    
    # Sıralama
    ordering = ('-created_at',)

    def amount(self, obj):
        """Biletin qiymətini göstərir"""
        return obj.amount

    def currency(self, obj):
        """Biletin valyutasını göstərir"""
        return obj.currency
