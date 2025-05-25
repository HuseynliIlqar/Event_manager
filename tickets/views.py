import uuid
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.views import APIView
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


class TicketCheckView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Əvvəlcə URL-dən partyamıza diqqət edək:
        # urls.py-də belə qeyd olunub: path('tickets/<str:ticket_id>/check/', ...)
        ticket_id = kwargs.get('ticket_id')  # URL-dən əldə edirik

        if not ticket_id:
            return Response(
                {"error": "URL parametrində ticket_id daxil edilməlidir."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Ticket-in özü mövcuddurmu, yoxlayırıq
        try:
            ticket = Ticket.objects.get(ticket_id=ticket_id)
        except Ticket.DoesNotExist:
            return Response(
                {"error": "Bilet tapılmadı və ya mövcud deyil."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Əgər bilet artıq istifadə olunubsa: is_used=True
        if ticket.is_used:
            return Response(
                {"error": "Bu bilet artıq istifadə olunub."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Ödənişə baxaq: Payment-də həmin event + həmin kullanıcı üçün başarılı bir ödəniş varmı?
        #    Burada ticket.event və ticket.customer əlaqələrinə baxırıq.
        #    İstifadəçi “customer” kimi bileti satın almış olmalıdır.
        customer = ticket.customer
        event = ticket.event

        if not customer:
            # Hələ heç kim bileti almayıbsa, `customer=None` gələ bilər.
            return Response(
                {"error": "Bu bilet hələ satın alınmayıb."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Payment obyektində filter-ləyirik:
        try:
            payment = Payment.objects.filter(
                event=event,
                user=customer,
                is_successful=True
            ).first()
        except Payment.DoesNotExist:
            payment = None

        if not payment:
            return Response(
                {"error": "Bu bilet üçün uğurlu ödəniş tapılmadı."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. Ticket.is_paid yoxsa, indi “ödəmə var” dediyimiz üçün güncəlləyək
        if not ticket.is_paid:
            ticket.is_paid = True
            ticket.save()

        # 5. İndi biletin vəziyyətini geri qaytaraq. Eyni zamanda, is_used=True olaraq qeyd edə bilərik.
        #    Əgər istəyirsinizsə, yoxlama anında bileti “istifadə olundu” kimi işarələmək üçün:
        ticket.is_used = True
        ticket.save()

        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)