from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from .models import Ticket, Event
from .serializers import TicketSerializer, EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(organizer=self.request.user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            event = self.get_queryset().get(pk=pk)
        except Event.DoesNotExist:
            raise NotFound("Event not found.")
        serializer = self.get_serializer(event)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(organizer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            event = self.get_queryset().get(pk=pk)
        except Event.DoesNotExist:
            raise NotFound("Event not found.")

        serializer = self.get_serializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save(organizer=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        try:
            event = self.get_queryset().get(pk=pk)
        except Event.DoesNotExist:
            raise NotFound("Event not found.")

        serializer = self.get_serializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(organizer=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            event = self.get_queryset().get(pk=pk)
        except Event.DoesNotExist:
            raise NotFound("Event not found.")
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(seller=self.request.user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            ticket = self.get_queryset().get(pk=pk)
        except Ticket.DoesNotExist:
            raise NotFound("Ticket not found.")
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            event = serializer.validated_data['event']
            if event.organizer != request.user:
                raise PermissionDenied("You can only create tickets for your own events.")
            serializer.save(seller=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            ticket = self.get_queryset().get(pk=pk)
        except Ticket.DoesNotExist:
            raise NotFound("Ticket not found.")

        serializer = self.get_serializer(ticket, data=request.data)
        if serializer.is_valid():
            if not ticket.customer:
                serializer.save(customer=request.user)
            else:
                serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        try:
            ticket = self.get_queryset().get(pk=pk)
        except Ticket.DoesNotExist:
            raise NotFound("Ticket not found.")

        serializer = self.get_serializer(ticket, data=request.data, partial=True)
        if serializer.is_valid():
            if not ticket.customer:
                serializer.save(customer=request.user)
            else:
                serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            ticket = self.get_queryset().get(pk=pk)
        except Ticket.DoesNotExist:
            raise NotFound("Ticket not found.")
        ticket.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
