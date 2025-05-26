from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_seller = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} — {'Seller' if self.is_seller else 'Customer'}"


class SellerApplication(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=100,blank=False,null=False)
    phone = models.CharField(max_length=20,blank=False,null=False)
    description = models.TextField(max_length=150,blank=False,null=False,default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — Application for {self.store_name}"