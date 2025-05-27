from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('auth_system.urls')),
    path('api/ticket_system/', include('tickets.urls')),
    path('api/payments/', include('payments.urls', namespace='payments')),
]
