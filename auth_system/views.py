from rest_framework.views import APIView
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.core.mail import mail_admins, send_mail
from django.template.loader import render_to_string
from .models import SellerApplication
from .serializers import RegisterSerializer, LoginSerializer, LogoutSerializer, PasswordChangeSerializer, \
    PasswordResetSerializer, SetNewPasswordSerializer,SellerApplicationSerializer

class SellerApplicationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if SellerApplication.objects.filter(user=request.user).exists():
            return Response(
                {'detail': 'Siz artıq müraciət etmisiniz.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SellerApplicationSerializer(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        app = serializer.save()

        subject = f"Yeni seller müraciəti: {request.user.username}"
        message = (
            f"Yeni seller müraciəti alındı:\n\n"
            f"İstifadəçi: {request.user.username} ({request.user.email})\n"
            f"Mağaza adı: {app.store_name}\n"
            f"Telefon: {app.phone}\n"
            f"Açıqlama: {app.description}\n"
            # f"Qısa təsvir: {getattr(app, 'description', '—')}\n"
            f"Müraciət vaxtı: {app.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )


        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False
        )

        return Response(
            {'detail': 'Müraciətiniz alındı və adminə göndərildi.'},
            status=status.HTTP_201_CREATED
        )

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Registration successful'}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']


        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            'access': str(access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Logout failed."}, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data.get('new_password')
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Parol uğurla dəyişdirildi!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActivateAccountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
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
            return Response({'detail': 'Token etibarsızdır və ya vaxtı keçmişdir.'}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Şifrəni sıfırlama linki email ünvanınıza göndərildi."},
                        status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        data = {
            'uidb64': uidb64,
            'token': token,
            **request.data
        }
        serializer = SetNewPasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Şifrə uğurla yeniləndi."},
                        status=status.HTTP_200_OK)