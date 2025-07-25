from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'username', 'phone_number', 'is_verified', 'is_active')
    search_fields = ('username', 'phone_number')

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'is_verified')}),
    )
