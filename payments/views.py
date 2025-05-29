from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer
from tickets.models import Ticket
import uuid
import requests
import hmac
import hashlib
from django.conf import settings

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            transaction_id=str(uuid.uuid4())
        )

def verify_callback_signature(request):
    """Xarici sistemdən gələn callback-in etibarlılığını yoxlayırıq"""
    signature = request.headers.get('X-Payment-System-Signature')
    if not signature:
        return False
    
    # Gələn məlumatları təhlükəsiz şəkildə yoxlayırıq
    payload = request.body
    expected_signature = hmac.new(
        settings.PAYMENT_SYSTEM_API_KEY.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    ticket_id = request.data.get('ticket_id')
    payment_method = request.data.get('payment_method', 'credit_card')
    ticket_count = int(request.data.get('ticket_count', 1))  # Default olaraq 1 ticket

    try:
        ticket = Ticket.objects.get(ticket_id=ticket_id)
    except Ticket.DoesNotExist:
        return Response({"error": "Ticket not found"}, status=404)

    # Təkrar ödənişin qarşısını alırıq
    if Payment.objects.filter(user=request.user, ticket=ticket).exists():
        return Response({"error": "Payment already exists for this ticket"}, status=400)

    # Ödəniş yaradırıq
    transaction_id = str(uuid.uuid4())
    payment = Payment.objects.create(
        user=request.user,
        ticket=ticket,
        ticket_count=ticket_count,
        payment_method=payment_method,
        transaction_id=transaction_id
    )

    # Ticket sayına görə ümumi qiyməti hesablayırıq
    total_price = float(ticket.price) * ticket_count
    
    # Prepare callback URL
    callback_url = f"{settings.BASE_URL}/api/payments/callback/"

    # Xarici ödəniş sisteminə yalnız lazımi məlumatları göndəririk
    payment_data = {
        "amount": total_price,
        "callback_url": callback_url
    }

    try:
        response = requests.post(
            f"{settings.PAYMENT_SYSTEM_URL}/api/payments/",
            json=payment_data,
            headers={
                "Authorization": f"Bearer {settings.PAYMENT_SYSTEM_API_KEY}",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        
        payment_data = response.json()
        payment.payment_system_id = payment_data.get('payment_reference')
        payment.payment_url = f"{settings.PAYMENT_SYSTEM_URL}/payment/{payment_data.get('payment_reference')}"
        payment.save()

        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except requests.RequestException as e:
        payment.status = 'failed'
        payment.save()
        return Response({"error": "Payment provider error", "details": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([])  # Callback public olur
def payment_callback(request):
    # Callback-in etibarlılığını yoxlayırıq
    if not verify_callback_signature(request):
        return Response({"error": "Invalid signature"}, status=400)

    data = request.data

    transaction_id = data.get('payment_reference')
    status_from_payment = data.get('is_successful')

    if not transaction_id:
        return Response({"error": "Missing payment reference"}, status=400)

    try:
        payment = Payment.objects.get(transaction_id=transaction_id)
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=404)

    # Status dəyişikliyini yoxlayırıq
    if payment.status == 'completed':
        return Response({"error": "Payment already completed"}, status=400)

    if status_from_payment:
        payment.status = "completed"
        payment.ticket.status = "confirmed"
        payment.ticket.save()
    else:
        payment.status = "failed"
        payment.ticket.status = "cancelled"
        payment.ticket.save()

    payment.save()

    return Response({"status": "updated"}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_detail(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
    except Payment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_list(request):
    payments = Payment.objects.filter(user=request.user)
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_status(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
    except Payment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
