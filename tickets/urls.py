from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .models import Ticket, Event
from .views import EventViewSet, TicketViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'tickets', TicketViewSet, basename='ticket')

urlpatterns = [
    path('', include(router.urls)),
]
