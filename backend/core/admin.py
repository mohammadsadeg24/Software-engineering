from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.models import User, Address


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_staff')
    fieldsets = BaseUserAdmin.fieldsets + (('Additional Info', {'fields': ('phone',)}),)

admin.site.register(Address)