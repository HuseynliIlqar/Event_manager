from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, TicketViewSet, TicketCheckViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'ticket-check', TicketCheckViewSet, basename='ticket-check')

app_name = 'tickets'

urlpatterns = [
    path('', include(router.urls)),
]
