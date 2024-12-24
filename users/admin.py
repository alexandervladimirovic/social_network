from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class AdminUser(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    raw_id_fields = ('groups', 'user_permissions')
