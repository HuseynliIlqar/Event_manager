from django.conf import settings
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from .models import SellerApplication
from .serializers import (
    SellerApplicationSerializer,
    RegisterSerializer, LoginSerializer, LogoutSerializer,
    PasswordChangeSerializer, PasswordResetSerializer, SetNewPasswordSerializer
)

class SellerApplicationViewSet(viewsets.ModelViewSet):
    queryset = SellerApplication.objects.all()
    serializer_class = SellerApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        if SellerApplication.objects.filter(user=self.request.user).exists():
            raise serializers.ValidationError("Siz artıq müraciət etmisiniz.")

        app = serializer.save()

        subject = f"Yeni seller müraciəti: {self.request.user.username}"
        message = (
            f"Yeni seller müraciəti alındı:\n\n"
            f"İstifadəçi: {self.request.user.username} ({self.request.user.email})\n"
            f"Mağaza adı: {app.store_name}\n"
            f"Telefon: {app.phone}\n"
            f"Açıqlama: {app.description}\n"
            f"Müraciət vaxtı: {app.created_at:%Y-%m-%d %H:%M:%S}\n"
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False
        )

class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Qeydiyyat uğurla tamamlandı.'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        RefreshToken(serializer.validated_data['refresh_token']).blacklist()
        return Response({'detail': 'Çıxış uğurla edildi.'}, status=status.HTTP_205_RESET_CONTENT)

    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated], url_path='change-password')
    def change_password(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': 'Parol uğurla dəyişdirildi!'}, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=['get'], permission_classes=[AllowAny],
        url_path=r'activate/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)'
    )
    def activate(self, request, uidb64=None, token=None):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'detail': 'Link düzgün deyil və ya istifadəçi mövcud deyil.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if user.is_active:
            return Response({'detail': 'Hesab artıq aktivdir.'}, status=status.HTTP_200_OK)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'detail': 'Hesab uğurla aktivləşdirildi.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Token etibarsızdır və ya vaxtı keçmişdir.'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='password-reset')
    def password_reset(self, request):
        serializer = PasswordResetSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Şifrə sıfırlama linki göndərildi.'}, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=['post'], permission_classes=[AllowAny],
        url_path=r'password-reset-confirm/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)'
    )
    def password_reset_confirm(self, request, uidb64=None, token=None):
        data = {'uidb64': uidb64, 'token': token, **request.data}
        serializer = SetNewPasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Şifrə uğurla yeniləndi.'}, status=status.HTTP_200_OK)
