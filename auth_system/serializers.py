from django_filters.conf import settings
from jwt.utils import force_bytes
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import BadHeaderError
from smtplib import SMTPException
from auth_system.models import Profile
from .models import SellerApplication



class SellerApplicationSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(max_length=100, required=True)
    phone = serializers.CharField(max_length=20, required=True)
    description = serializers.CharField(max_length=150, required=True)

    class Meta:
        model  = SellerApplication
        fields = ['store_name', 'phone', 'description']

    def create(self, validated_data):
        user = self.context['request'].user
        return SellerApplication.objects.create(user=user, **validated_data)

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password_2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_2']:
            raise serializers.ValidationError({
                'password_2': 'Parollar eyni olmalıdır.'
            })
        return attrs

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Bu istifadəçi adı artıq mövcuddur.")
        return value

    def create(self, validated_data):
        validated_data.pop('password_2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.is_active = False
        user.save()

        Profile.objects.create(user=user)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = f"http://127.0.0.1:8000/api/auth/activate/{uid}/{token}/"

        try:
            send_mail(
                subject="Hesab aktivləşdirmə linki",
                message=f"Aktivləşdirmə üçün bu linkə daxil olun: {activation_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except (BadHeaderError, SMTPException, Exception):
            user.delete()
            raise serializers.ValidationError("Email göndərilə bilmədi. Zəhmət olmasa düzgün email yazın.")

        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # authenticate çağıranda bizim EmailBackend də işləyəcək
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            raise serializers.ValidationError("Email və ya şifrə yalnışdır")
        attrs['user'] = user
        return attrs

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs.get('refresh_token')

        if not refresh_token:
            raise serializers.ValidationError("Refresh token is required.")

        return attrs

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context.get('request').user
        old_password = data.get('old_password')

        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Köhnə parol düzgün deyil."})

        new_password = data.get('new_password')
        new_password_confirm = data.get('new_password_confirm')
        if new_password != new_password_confirm:
            raise serializers.ValidationError({"new_password_confirm": "Yeni parol və təkrar eyni olmalıdır."})

        if len(new_password) < 8:
            raise serializers.ValidationError({"new_password": "Yeni parol ən azı 8 simvoldan ibarət olmalıdır."})

        return data

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Belə email ilə istifadəçi tapılmadı.")
        return value

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"http://127.0.0.1:8000/api/auth/password-reset-confirm/{uid}/{token}/"

        try:
            send_mail(
                subject="Şifrəni sıfırlama linki",
                message=f"Şifrənizi sıfırlamaq üçün aşağıdakı linkə daxil olun:\n\n{reset_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception:
            raise serializers.ValidationError("Email göndərilmədi. Zəhmət olmasa düzgün email yazın.")
        return user

class SetNewPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            uid = urlsafe_base64_decode(attrs['uidb64']).decode()
            user = User.objects.get(pk=uid)
        except Exception:
            raise serializers.ValidationError("Link etibarsızdır.")

        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError("Token etibarsızdır və ya vaxtı keçib.")

        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Şifrələr uyğun gəlmir."})

        if len(attrs['new_password']) < 8:
            raise serializers.ValidationError({"new_password": "Yeni şifrə ən azı 8 simvoldan ibarət olmalıdır."})

        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

