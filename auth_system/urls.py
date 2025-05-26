from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SellerApplicationViewSet, UserViewSet

router = DefaultRouter()
router.register(r'seller-applications', SellerApplicationViewSet, basename='seller-application')
router.register(r'auth', UserViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
]

# Aşağıdakı endpointlər avtomatik yaradılır:

# -------------------------------------------------------------------
# /seller-applications/             # SellerApplicationViewSet
#   GET    → istifadəçinin bütün müraciətlərini siyahılayır
#   POST   → yeni seller müraciəti yaradır
#
# /seller-applications/{pk}/        # SellerApplicationViewSet
#   GET    → seçilmiş müraciətin detalları
#   PUT    → bütün sahələri yeniləyir
#   PATCH  → seçilmiş sahələri qismən yeniləyir
#   DELETE → müraciəti silir
# -------------------------------------------------------------------
# /auth/register/                   # UserViewSet.register
#   POST   → yeni istifadəçi qeydiyyatı
#
# /auth/login/                      # UserViewSet.login
#   POST   → istifadəçi daxil olur, access və refresh token qaytarır
#
# /auth/logout/                     # UserViewSet.logout
#   POST   → refresh token-i blacklist edir (çıxış)
#
# /auth/change-password/            # UserViewSet.change_password
#   PUT    → giriş etmiş istifadəçinin parolunu dəyişir
#
# /auth/activate/{uidb64}/{token}/  # UserViewSet.activate
#   GET    → email-də gələn link vasitəsilə hesabı aktivləşdirir
#
# /auth/password-reset/             # UserViewSet.password_reset
#   POST   → şifrə sıfırlama linkini email-ə göndərir
#
# /auth/password-reset-confirm/{uidb64}/{token}/  # UserViewSet.password_reset_confirm
#   POST   → linkdəki token və uid əsasında yeni şifrə təyin edir
# -------------------------------------------------------------------
