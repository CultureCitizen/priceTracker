from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models
from django.utils.translation import gettext as _
from parler.admin import TranslatableAdmin
# App models
from .models import Activity, ActivityLog, Area, Category, HouseType, HousePriceSource, PriceType
from .models import UnitConv, UnitType, Unit, UnitType, UnitConv

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


class CountryAdmin(admin.ModelAdmin):
    model = models.Country
    list_display = ['iso_code', 'name_en', 'name']
    list_filter = ['iso_code', 'name_en']


class LanguageAdmin(admin.ModelAdmin):
    model = models.AppLanguage
    list_display = ['iso_code', 'name_en']
    list_filter = ['iso_code', 'name_en']


class ActivityAdmin(TranslatableAdmin):
    model = Activity
    ordering = ['code']
    list_display = ['code', 'points']
    search_fields = ['code', ]


class AreaAdmin(TranslatableAdmin):
    model = Area
    list_display = ['code']
    search_fields = ['code', ]


class CategoryAdmin(TranslatableAdmin):
    model = Category

    list_display = ['get_area_code', 'code', ]
    search_fields = ['get_area_code', 'code', ]

    def get_area_code(self, obj):
        return obj.area.code


class HousePriceSourceAdmin(TranslatableAdmin):
    model = HousePriceSource
    list_display = ['code', ]
    search_fields = ['code', ]


class HouseTypeAdmin(TranslatableAdmin):
    model = HouseType
    list_display = ['code', ]
    search_fields = ['code', ]


class PriceTypeAdmin(TranslatableAdmin):
    model = PriceType
    list_display = ['code', ]
    search_fields = ['code', ]


class UnitTypeAdmin(TranslatableAdmin):
    model = UnitType
    list_display = ['code', ]
    search_fields = ['code', ]


class ResourceUsageAdmin(TranslatableAdmin):
    model = models.ResourceUsage
    list_display = ['code', ]
    search_fields = ['code', ]


class UnitAdmin(TranslatableAdmin):
    model = Unit
    list_display = ['iso_code', 'name_en', 'get_unit_type', 'is_metric']
    search_fields = ['iso_code', 'name_en']

    def get_unit_type(self, obj):
        return obj.unit_type.name_en


class UnitConvAdmin(admin.ModelAdmin):
    model = UnitConv
    list_display = ['get_unit_name', 'get_to_unit_name', 'conv_factor']
    search_fields = ['get_unit_name', 'get_to_unit_name', ]

    def get_unit_name(self, obj):
        return obj.unit.name_en

    def get_to_unit_name(self, obj):
        return obj.to_unit.name_en


# The model.User class is displayed using the UserAdmin class
admin.site.register(models.User, UserAdmin)
admin.site.register(models.AppLanguage, LanguageAdmin)
admin.site.register(models.Country, CountryAdmin)
admin.site.register(models.Activity, ActivityAdmin)
admin.site.register(models.Area, AreaAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.HousePriceSource, HousePriceSourceAdmin)
admin.site.register(models.HouseType, HouseTypeAdmin)
admin.site.register(models.PriceType, PriceTypeAdmin)
admin.site.register(models.UnitType, UnitTypeAdmin)
admin.site.register(models.ResourceUsage, ResourceUsageAdmin)
admin.site.register(models.Unit, UnitAdmin)
admin.site.register(models.UnitConv, UnitConvAdmin)
