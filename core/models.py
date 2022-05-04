from random import triangular
import re
from django.db import models
from datetime import date
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from parler.models import TranslatableModel, TranslatedFields
from django.utils.translation import gettext_lazy as _
# User manager


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError("User must have an email address")
        else:
            # raises ValidationError
            validate_email(email)

        if not "username" in extra_fields :
            extra_fields['username'] = email
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Creates and saves a new super user"""
        if not "username" in extra_fields :
            extra_fields['username'] = email
        user = self.create_user(email, password, **extra_fields)
        user.username = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.username = email
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=250, unique=True)
    username = models.CharField(max_length=30, unique=True, default='')
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    #profile data
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    points = models.IntegerField(default=0)
    sex = models.CharField(max_length=1,null=True)
    birth_year = models.IntegerField(null=True)
    created_at = models.DateTimeField(
        auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        return f'{self.user.email} Profile'


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.CharField(max_length=30)
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} Activity Log'


class Activity(TranslatableModel):
    name_en = models.CharField(max_length=30)
    translations = TranslatedFields(
        name=models.CharField(max_length=30)
    )
    points = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.name_en}:{self.points}'

    def save_model(self, request, obj, form, change):    
        lang = self.get_current_language()

        if obj.id == None:
            obj.created_by = request.user
            if lang == 'en':
                obj.name_en = obj.translations.name
            super().save_model(request, obj, form, change)
        else:
            obj.updated_by = request.user
            if lang == 'en':
                obj.name_en = obj.translations.name

            super().save_model(request, obj, form, change)


# ===============================================================================
# Configuration
# ===============================================================================

class Language(models.Model):
    iso_code = models.CharField(max_length=2)
    name_en = models.CharField(max_length=30)
    translations = TranslatedFields(
        name=models.CharField(max_length=30),
    )

    def __str__(self):
        return f'{self.iso_code}:{self.name_en}'


class Area(TranslatableModel):
    """Price Area
    E.g Food , transport , services , etc"""
    code = models.CharField(max_length=10, unique=True)
    name_en = models.CharField(max_length=30)
    translations = TranslatedFields(
        name=models.CharField(max_length=30),
    )

    def __str__(self):
        return self.name


class Category(TranslatableModel):
    """Category"""
    area = models.ForeignKey(
        Area, on_delete=models.RESTRICT, related_name='categories')

    name_en = models.CharField(max_length=30)
    translations = TranslatedFields(
        name=models.CharField(max_length=30),
    )

    def __str__(self):
        return self.name


class PriceItem(models.Model):
    name_en = models.CharField(max_length=30)


class CountryCategory(TranslatableModel):
    """Item classifications specific for a country
        I am not sure if this class will work as a model or not
    """
    country = models.ForeignKey('Country', on_delete=models.RESTRICT)
    price_item = models.ForeignKey('PriceItem', on_delete=models.RESTRICT)
    translations = TranslatedFields(
        name=models.CharField(max_length=30),
    )


class HouseType(TranslatableModel):
    """Home type
    E.g low-rise appartment, high-rise appartment, duplex , house , etc"""
    codee = models.CharField(max_length=10, unique=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=30),
    )

    def __str__(self):
        return self.name


class HousePriceSource(TranslatableModel):
    """House price source:
    E.g. actual / exptected """
    translations = TranslatedFields(
        name=models.CharField(max_length=20),
    )

    def __str__(self):
        return self.name


class PriceType(TranslatableModel):
    """Price type
    producer sale, wholesale buy, wholesale sale, retail buy , retail sale"""
    code = models.CharField(max_length=10, unique=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=10),
    )

    def __str__(self):
        return self.name


class UnitType(TranslatableModel):
    """Unit type:
    length, area, energy , volume, weight, etc"""
    name_en = models.CharField(max_length=20)
    translations = TranslatedFields(
        name=models.CharField(max_length=20),
    )

    def __str__(self):
        return self.name


class ResourceUsage(TranslatableModel):
    """Resource usage
        E.g Government, Residential, Commercial, Industrial
    """
    name_en = models.CharField(max_length=20)
    translations = TranslatedFields(
        name=models.CharField(max_length=20),
    )

    def __str__(self):
        return self.name

    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.created_by = request.user
        else:
            obj.updated_by = request.user

# ===============================================================================
# Catalogs
# ===============================================================================


class ActiveSubstance(TranslatableModel):
    """Active substance"""
    iso_name = models.CharField(max_length=40),
    translations = TranslatedFields(
        name=models.CharField(max_length=40),
    )
    unit = models.ForeignKey(
        'Unit', on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name='active_substance_created_by')
    updated_by = models.ForeignKey(
        User, related_name='active_substance_changed_by', on_delete=models.RESTRICT)

    def __str__(self):
        return self.name


class Currency(TranslatableModel):
    iso_code = models.CharField(max_length=3, unique=True)
    name_en = models.CharField(max_length=20)
    translations = TranslatedFields(
        name=models.CharField(max_length=20),
    )


class Country(TranslatableModel):
    """Country"""
    iso_code = models.CharField(max_length=2, unique=True)
    name_en = models.CharField(max_length=30)
    language = models.ForeignKey(Language, on_delete=models.RESTRICT, related_name='countries')
    
    translations = TranslatedFields(
        name=models.CharField(max_length=30),
    )

    def __str__(self):
        return self.name


class FoodStorage(TranslatableModel):
    """Food storage category: 
    - 1: Fresh,
    - 2: Frozen,
    - 3: Refrigerated,
    - 4: Dry,
    - 5: Canned"""
    translations = TranslatedFields(
        name=models.CharField(max_length=20),
    )

    def __str__(self):
        return self.name


class Food(TranslatableModel):
    translatiions = TranslatedFields(
        name=models.CharField(max_length=40),
    )
    picture = models.ImageField(upload_to='images/food', blank=True, null=True)
    generic_food = models.ForeignKey(
        'self', on_delete=models.RESTRICT, blank=True, null=True)
    is_generic = models.BooleanField(default=False)
    food_storage = models.ForeignKey('FoodStorage', on_delete=models.RESTRICT)
    is_cooked = models.BooleanField(default=False)
    category = models.ForeignKey('Category', on_delete=models.RESTRICT)
    weight_unit = models.ForeignKey('Unit', on_delete=models.RESTRICT)
    weight = models.FloatField(default=0)
    weight_kg = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='food_created_by', null=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='food_changed_by', null=True)

    def __str__(self):
        return f'{self.name} ({self.food_storage.name})'
    
    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.created_by = request.user
        else:
            obj.updated_by = request.user
    

class Medicine(TranslatableModel):
    """Medicine"""
    name_en = models.CharField(max_length=40)
    translations = TranslatedFields(
        name=models.CharField(max_length=40),
    )
    active_s1 = models.ForeignKey(
        'ActiveSubstance', on_delete=models.RESTRICT, related_name='active_s1')
    active_s2 = models.ForeignKey(
        'ActiveSubstance', on_delete=models.RESTRICT, related_name='active_s2')
    active_s3 = models.ForeignKey(
        'ActiveSubstance', on_delete=models.RESTRICT, related_name='active_s3')
    s1_amount = models.FloatField(default=0)
    s2_amount = models.FloatField(default=0)
    s3_amount = models.FloatField(default=0)
    s1_unit = models.ForeignKey(
        'Unit', related_name='medicine_unit1', on_delete=models.RESTRICT)
    s2_unit = models.ForeignKey(
        'Unit', related_name='medicine_unit2', on_delete=models.RESTRICT)
    s3_unit = models.ForeignKey(
        'Unit', related_name='medicine_unit3', on_delete=models.RESTRICT)

    def __str__(self):
        return self.name

    def save_model(self, request, obj, form, change):
        lang = self.get_current_language()

        if obj.id == None:
            obj.created_by = request.user
            if lang == 'en':
                obj.name = obj.translations.name
            super().save_model(request, obj, form, change)
        else:
            obj.updated_by = request.user
            if lang == 'en':
                obj.name = obj.translations.name

            super().save_model(request, obj, form, change)


class State(TranslatableModel):
    """State"""
    country = models.ForeignKey(Country, on_delete=models.RESTRICT)
    iso_code = models.CharField(max_length=5, unique=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=30),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='state_created_by',
                                   on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name='state_changed_by',
                                   on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    def __str__(self):
        return self.name

    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
        else:
            obj.updated_by = request.user
            super().save_model(request, obj, form, change)


class City(TranslatableModel):
    country = models.ForeignKey(Country, on_delete=models.RESTRICT)
    state = models.ForeignKey(State, on_delete=models.RESTRICT)
    translations = TranslatedFields(
        name=models.CharField(max_length=30),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='city_created_by')
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='city_changed_by')

    def __str__(self):
        return self.name

    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
        else:
            obj.updated_by = request.user
            super().save_model(request, obj, form, change)


class Unit(TranslatableModel):
    iso_code = models.CharField(max_length=5, unique=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=30),
    )
    is_metric = models.BooleanField(default=True)
    unit_type = models.ForeignKey(UnitType, on_delete=models.RESTRICT)

    def __str__(self):
        return self.name


class UnitConv(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.RESTRICT)
    conv_unit = models.ForeignKey(
        Unit, on_delete=models.RESTRICT, related_name='conv_unit')
    conv_factor = models.FloatField()

    def __str__(self):
        return f'{self.unit.name}:{self.conv_unit.name}:{self.conv_factor}'


class Vendor(models.Model):
    country = models.ForeignKey(Country, on_delete=models.RESTRICT)
    name = models.CharField(max_length=30)
    informal = models.BooleanField(default=False)
    address = models.CharField(max_length=100)
    is_wholesale = models.BooleanField(default=False)
    className = models.CharField(max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='vendor_created_by')
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='vendor_changed_by')

    def __str__(self):
        return f'{self.name}'

    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
        else:
            obj.updated_by = request.user
            super().save_model(request, obj, form, change)

# ===============================================================================
# Transactions
# ===============================================================================


class CurrencyConv(models.Model):
    date_from = models.DateField()
    date_to = models.DateField()
    currency_from = models.ForeignKey(
        Currency, on_delete=models.RESTRICT, related_name='currency_from')
    currency_to = models.ForeignKey(
        Currency, on_delete=models.RESTRICT, related_name='currency_to')
    rate = models.FloatField()

    def category(self):
        return ''

    def __str__(self):
        return f'{self.date_from}:{self.currency_from.name}:{self.currency_to.name}:{self.rate}'

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, null=True, blank=True,
        related_name='conv_created_by')
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, null=True, blank=True,
        related_name='conv_changed_by')

    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
        else:
            obj.updated_by = request.user
            super().save_model(request, obj, form, change)


class ElectricityPrice(models.Model):
    date = models.DateField()
    country = models.ForeignKey(Country, on_delete=models.RESTRICT)
    state = models.ForeignKey(State, on_delete=models.RESTRICT)
    city = models.ForeignKey(City, on_delete=models.RESTRICT)
    consumption = models.FloatField()
    price = models.FloatField()
    unit_price = models.FloatField()
    period_days = models.IntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, related_name='electricity_price_created_by', on_delete=models.RESTRICT, null=True, blank=True)
    updated_by = models.ForeignKey(
        User, related_name='electricity_price_changed_by', on_delete=models.RESTRICT, null=True, blank=True)

    def category(self):
        return 'services'

    def subcategory(self):
        return 'electricity'

    def __str__(self):
        return f'{self.date}:{self.country.name}:{self.state.name}:{self.city.name}:{self.consumption}:{self.price}:{self.unit_price}:{self.period_days}'

    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
        else:
            obj.updated_by = request.user
            super().save_model(request, obj, form, change)


class gasPrice(models.Model):
    date = models.DateField()
    country = models.ForeignKey(Country, on_delete=models.RESTRICT)
    state = models.ForeignKey(State, on_delete=models.RESTRICT)
    city = models.ForeignKey(City, on_delete=models.RESTRICT)
    consumption = models.FloatField()
    unit = models.ForeignKey(Unit, on_delete=models.RESTRICT)
    price = models.FloatField()
    period_days = models.IntegerField()

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, null=True, blank=True, related_name='gas_price_created_by')
    updated_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, null=True, blank=True, related_name='gas_price_changed_by')

    def category(self):
        return 'services'

    def subcategory(self):
        return 'gas'

    def __str__(self):
        return f'{self.date}:{self.country.name}:{self.state.name}:{self.city.name}:{self.consumption}:{self.price}:{self.period_days}'

    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
        else:
            obj.updated_by = request.user
            super().save_model(request, obj, form, change)


class InternetPrice(models.Model):
    date = models.DateField()
    country = models.ForeignKey(Country, on_delete=models.RESTRICT)
    state = models.ForeignKey(State, on_delete=models.RESTRICT)
    city = models.ForeignKey(City, on_delete=models.RESTRICT)
    price = models.FloatField()
    period_days = models.IntegerField()
    max_speed_gbyte = models.FloatField()
    actual_speed_gbyte = models.FloatField()
    data_limit_mb = models.FloatField()

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, related_name='inet_price_created_by', on_delete=models.RESTRICT, null=True, blank=True)
    updated_by = models.ForeignKey(
        User, related_name='inet_price_changed_by', on_delete=models.RESTRICT, null=True, blank=True)

    def category(self):
        return 'services'

    def subcategory(self):
        return 'internet'

    def __str__(self):
        return f'{self.date}:{self.country.name}:{self.state.name}:{self.city.name}:{self.price}:{self.period_days}:{self.max_speed_gbyte}:{self.actual_speed_gbyte}:{self.data_limit_mb}'

    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
        else:
            obj.updated_by = request.user
            super().save_model(request, obj, form, change)


class FoodPrice(models.Model):
    date = models.DateField()
    country = models.ForeignKey(Country, on_delete=models.RESTRICT)
    state = models.ForeignKey(State, on_delete=models.RESTRICT)
    city = models.ForeignKey(City, on_delete=models.RESTRICT)
    vendor = models.ForeignKey(Vendor, on_delete=models.RESTRICT)
    food = models.ForeignKey(Food, on_delete=models.RESTRICT)
    price = models.FloatField()
    weight_unit = models.ForeignKey(Unit, on_delete=models.RESTRICT)
    weight = models.FloatField()
    weight_kg = models.FloatField()
    created_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, null=True, blank=True,
        related_name='food_price_created_by')
    updated_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, null=True, blank=True,
        related_name='food_price_changed_by')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def category(self):
        return "food"

    def subcategory(self):
        return "food"

    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
        else:
            obj.updated_by = request.user
            super().save_model(request, obj, form, change)


class housePrice(models.Model):
    date = models.DateField()
    country = models.ForeignKey(Country, on_delete=models.RESTRICT)
    state = models.ForeignKey(State, on_delete=models.RESTRICT)
    city = models.ForeignKey(City, on_delete=models.RESTRICT)
    rent_sale = models.CharField(max_length=1)
    house_type = models.ForeignKey(HouseType, on_delete=models.RESTRICT)
    price_type = models.ForeignKey(PriceType, on_delete=models.RESTRICT)
    price = models.FloatField()
    materials = models.CharField(max_length=50)
    land_m2 = models.FloatField()
    construction_m2 = models.FloatField()
    electricity_pct = models.FloatField()
    water_pct = models.FloatField()
    internet_pct = models.FloatField()
    parking_spaces = models.IntegerField()
    floors = models.IntegerField()
    floor = models.IntegerField()
    garden_type = models.CharField(max_length=2)
    garden_m2 = models.FloatField()
    gym_type = models.CharField(max_length=2)
    pool_type = models.CharField(max_length=2)
    # admin fields
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='house_price_created_by')
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='house_price_changed_by')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def category(self):
        return "housing"

    def subcategory(self):
        return "housing"

    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
        else:
            obj.updated_by = request.user
            super().save_model(request, obj, form, change)


class gasolinePrice(models.Model):
    date = models.DateField()
    country = models.ForeignKey(Country, on_delete=models.RESTRICT)
    state = models.ForeignKey(State, on_delete=models.RESTRICT)
    city = models.ForeignKey(City, on_delete=models.RESTRICT)
    price = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.RESTRICT)
    volume = models.FloatField()
    vol_unit = models.ForeignKey(Unit, on_delete=models.RESTRICT)
    price_per_liter = models.FloatField()
    # admin fields
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='gasoline_price_created_by')
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='gasoline_price_changed_by')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def category(self):
        return "transport"

    def subcategory(self):
        return "gasoline"

    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
        else:
            obj.updated_by = request.user
            super().save_model(request, obj, form, change)


class PublicTransportType(models.TextChoices):
    URBAN_BUS = 'UB', _('Urban Bus')
    URBAN_BUS_SMALL = 'UBS', _('Urban Bus Small')
    BUS = 'JR', _('Bus')
    TAXI = 'TX', _('Taxi')
    TROLLEY_CAR = 'TC', _('Trolley Car')
    FERRY = 'FR', _('Ferry')
    METRO = 'MT', _('Metro')
    TRAIN_LS = 'TLS', _('Train LOW SPEED')
    TRAIN_HS = 'THS', _('Train HIGH SPEED')
    AIRPLANE = 'AP', _('Airplane')


class TransportClass(TranslatableModel):
    transport_type = models.CharField(
        max_length=4, choices=PublicTransportType.choices)
    translations = TranslatedFields(
        name=models.CharField(max_length=50),
    )

    def __str__(self):
        return self.name


class TransportVendor(models.Model):
    transport_type = models.CharField(
        max_length=4, choices=PublicTransportType.choices)
    vendor_name = models.CharField(max_length=50)

    def __str__(self):
        return self.vendor_name


class TransportPrice(models.Model):
    date = models.DateField()
    country = models.ForeignKey(Country, on_delete=models.RESTRICT)
    state = models.ForeignKey(State, on_delete=models.RESTRICT)
    city = models.ForeignKey(City, on_delete=models.RESTRICT)
    city_dest = models.ForeignKey(
        City, on_delete=models.RESTRICT, related_name='city_dest')
    price = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.RESTRICT)
    distance = models.FloatField()
    distance_unit = models.ForeignKey(Unit, on_delete=models.RESTRICT)
    price_per_km = models.FloatField()
    is_public = models.BooleanField()
    transport_type = models.CharField(
        max_length=4, choices=PublicTransportType.choices)
    transport_vendor = models.ForeignKey(
        TransportVendor, on_delete=models.RESTRICT)
    # admin fields
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transport_price_created_by')
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transport_price_changed_by')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def category(self):
        return "transport"

    def subcategory(self):
        return "transport"

    def __str__(self):
        return f'{self.date}:{self.country}:{self.state}:{self.city}:{self.transport_type}:{self.transport_vendor}'

    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
        else:
            obj.updated_by = request.user
            super().save_model(request, obj, form, change)


class MedicinePrice(models.Model):
    date = models.DateField()
    country = models.ForeignKey(Country, on_delete=models.RESTRICT)
    state = models.ForeignKey(State, on_delete=models.RESTRICT)
    city = models.ForeignKey(City, on_delete=models.RESTRICT)
    vendor = models.ForeignKey(Vendor, on_delete=models.RESTRICT)
    Medicine = models.ForeignKey(Medicine, on_delete=models.RESTRICT)
    price = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.RESTRICT)
    # admin fields
    created_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, null=True, blank=True, related_name='medicine_price_created_by')
    updated_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, null=True, blank=True, related_name='medicine_price_changed_by')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def category(self):
        return "health"

    def subcategory(self):
        return "medicine"

    def __str__(self):
        return f'{self.date}:{self.country}:{self.state}:{self.city}:{self.vendor}:{self.Medicine}'

    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
        else:
            obj.updated_by = request.user
            super().save_model(request, obj, form, change)


class waterPrice(models.Model):
    date = models.DateField()
    country = models.ForeignKey(Country, on_delete=models.RESTRICT)
    state = models.ForeignKey(State, on_delete=models.RESTRICT)
    city = models.ForeignKey(City, on_delete=models.RESTRICT)
    consumption = models.FloatField()
    volume_unit = models.ForeignKey(Unit, on_delete=models.RESTRICT)
    price_m3 = models.FloatField()
    volume_m3 = models.FloatField()
    price = models.FloatField()
    is_public = models.BooleanField()
    period_days = models.IntegerField()

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, null=True, blank=True, related_name='water_price_created_by')
    updated_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, null=True, blank=True, related_name='water_price_changed_by')

    def category(self):
        return "services"

    def subcategory(self):
        return "water"

    def __str__(self):
        return f'{self.date}:{self.country}:{self.state}:{self.city}:{self.is_public}:{self.price}'

    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
        else:
            obj.updated_by = request.user
            super().save_model(request, obj, form, change)
