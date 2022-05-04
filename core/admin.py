from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models
from django.utils.translation import gettext as _
from parler.admin import TranslatableAdmin
# App models
from .models import Activity,ActivityLog,Area,Category,HouseType,HousePriceSource,PriceType
from .models import UnitConv, UnitType,Unit,UnitType,UnitConv

# Register your models here.
class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'username']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('username',)}),
        (_('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': ('email', 'password1', 'password2')}),
    )

class ActivityAdmin(TranslatableAdmin):
    list_display = ['name_en', 'points']
    search_fields = ['name_en',]

class AreaAdmin(TranslatableAdmin):
    list_display = ['name_en', 'points']
    search_fields = ['name_en',]


# The model.User class is displayed using the UserAdmin class
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Activity, ActivityAdmin)
