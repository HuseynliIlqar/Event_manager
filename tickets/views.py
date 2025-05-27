import uuid
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Ticket, Event, EventCategory
from .serializers import TicketSerializer, EventSerializer
from datetime import datetime

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['start_time', 'price', 'created_at']

    def get_queryset(self):
        queryset = Event.objects.filter(is_active=True)
        
        # Axtarış parametrləri
        query = self.request.query_params.get('q', '')
        category = self.request.query_params.get('category', '')
        min_price = self.request.query_params.get('min_price', '')
        max_price = self.request.query_params.get('max_price', '')
        date_from = self.request.query_params.get('date_from', '')
        date_to = self.request.query_params.get('date_to', '')
        location = self.request.query_params.get('location', '')

        # Mətn axtarışı
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )

        # Kateqoriyaya görə filtirləmə
        if category:
            queryset = queryset.filter(category__name__iexact=category)

        # Qiymət aralığına görə filtirləmə
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Tarix aralığına görə filtirləmə
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d')
                queryset = queryset.filter(start_time__gte=date_from)
            except ValueError:
                pass

        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d')
                queryset = queryset.filter(end_time__lte=date_to)
            except ValueError:
                pass

        # Yerə görə filtirləmə
        if location:
            queryset = queryset.filter(location__icontains=location)

        return queryset

    @action(detail=False, methods=['get'])
    def search(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def categories(self, request):
        categories = EventCategory.objects.all()
        return Response([{
            'id': category.id,
            'name': category.name,
            'description': category.description
        } for category in categories])

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
            print(serializer.data)
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

class TicketCheckViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def check(self, request, pk=None):
        ticket_id = pk

        if not ticket_id:
            return Response(
                {"error": "URL parametrində ticket_id daxil edilməlidir."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ticket = Ticket.objects.get(ticket_id=ticket_id)
        except Ticket.DoesNotExist:
            return Response(
                {"error": "Bilet tapılmadı və ya mövcud deyil."},
                status=status.HTTP_404_NOT_FOUND
            )

        if ticket.is_used:
            return Response(
                {"error": "Bu bilet artıq istifadə olunub."},
                status=status.HTTP_400_BAD_REQUEST
            )

        customer = ticket.customer
        event = ticket.event

        if not customer:
            return Response(
                {"error": "Bu bilet hələ satın alınmayıb."},
                status=status.HTTP_400_BAD_REQUEST
            )

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

        if not ticket.is_paid:
            ticket.is_paid = True
            ticket.save()

        ticket.is_used = True
        ticket.save()

        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TicketPurchaseAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, ticket_id):
        # 1. Mövcud bileti tap
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id)

        # 2. Əgər artıq alınıbsa
        if ticket.customer:
            return Response({"error": "Bu bilet artıq alınıb."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Payment sisteminə məlumat göndər
        payment_api_url = "http://payment-system/api/payments/"  # <- bunu real payment URL ilə əvəz et
        payload = {
            "user_id": request.user.id,
            "event_id": ticket.event.id,
            "ticket_id": ticket.ticket_id,
            "amount": float(ticket.price)
        }

        try:
            payment_response = requests.post(payment_api_url, json=payload)
            payment_data = payment_response.json()
        except Exception as e:
            return Response({"error": "Ödəniş sistemi ilə əlaqə qurulmadı.", "details": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 4. Ödəniş nəticəsinə bax
        if payment_response.status_code == 200 and payment_data.get("status") == "success":
            ticket.customer = request.user
            ticket.is_paid = True
            ticket.is_confirmed = True  # əgər belə bir sahə varsa
            ticket.save()
            serializer = TicketSerializer(ticket)
            return Response({
                "message": "Biletiniz təsdiqləndi.",
                "ticket": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "error": "Ödəniş uğursuz oldu.",
            "payment_status": payment_data.get("status"),
            "details": payment_data.get("message", "")
        }, status=status.HTTP_400_BAD_REQUEST)
