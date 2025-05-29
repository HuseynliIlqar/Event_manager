from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.PaymentViewSet, basename='payment')

app_name = 'payments'

urlpatterns = [
    path('', include(router.urls)),
    path('initiate/', views.initiate_payment, name='initiate_payment'),
    path('list/', views.payment_list, name='payment_list'),
    path('detail/<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('status/<int:payment_id>/', views.payment_status, name='payment_status'),
    path('callback/', views.payment_callback, name='payment_callback'),
] 