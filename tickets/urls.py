from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .models import Ticket, Event
from .views import EventViewSet, TicketViewSet, TicketCheckView

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'tickets', TicketViewSet, basename='ticket')

urlpatterns = [
    path('', include(router.urls)),
    path('tickets/<str:ticket_id>/check/', TicketCheckView.as_view(), name='ticket-check'),]
