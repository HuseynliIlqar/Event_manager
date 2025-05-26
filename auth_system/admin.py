from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, SellerApplication

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profil'

class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(SellerApplication)
class SellerApplicationAdmin(admin.ModelAdmin):
    list_display  = ('user', 'store_name','created_at','description')
    search_fields = ('user__username', 'store_name')