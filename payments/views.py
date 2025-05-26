from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Payment
import uuid

class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            transaction_id=str(uuid.uuid4())
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    amount = request.data.get('amount')
    payment_method = request.data.get('payment_method')
    description = request.data.get('description', '')

    payment = Payment.objects.create(
        user=request.user,
        amount=amount,
        payment_method=payment_method,
        description=description,
        transaction_id=str(uuid.uuid4())
    )


    payment.status = 'completed'
    payment.save()

    return Response({
        'status': 'success',
        'payment_id': payment.id,
        'transaction_id': payment.transaction_id,
        'amount': str(payment.amount),
        'currency': payment.currency,
        'status': payment.status
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_detail(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)
        return Response({
            'id': payment.id,
            'transaction_id': payment.transaction_id,
            'amount': str(payment.amount),
            'currency': payment.currency,
            'payment_method': payment.payment_method,
            'status': payment.status,
            'created_at': payment.created_at,
            'description': payment.description
        })
    except Payment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_list(request):
    payments = Payment.objects.filter(user=request.user)
    return Response([{
        'id': payment.id,
        'transaction_id': payment.transaction_id,
        'amount': str(payment.amount),
        'currency': payment.currency,
        'payment_method': payment.payment_method,
        'status': payment.status,
        'created_at': payment.created_at
    } for payment in payments])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_status(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)
        return Response({
            'status': payment.status,
            'amount': str(payment.amount),
            'currency': payment.currency,
            'created_at': payment.created_at.isoformat()
        })
    except Payment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
