from django.db import models
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

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Creates and saves a new super user"""
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=250, unique=True)
    username = models.CharField(max_length=30, unique=True, default='')
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    translations = TranslatedFields(
        activity=models.CharField(max_length=30)
    )
    points = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.activity}:{self.points}'

# ===============================================================================
# Configuration
# ===============================================================================


class Area(TranslatableModel):
    """Price Area"""
    translations = TranslatedFields(
        name=models.CharField(max_length=30),
    )

    def __str__(self):
        return self.name


class Category(TranslatableModel):
    """Category"""
    area = models.ForeignKey(
        Area, on_delete=models.RESTRICT, related_name='categories')

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


class HomeType(TranslatableModel):
    """Home type"""
    translations = TranslatedFields(
        name=models.CharField(max_length=30),
    )

    def __str__(self):
        return self.name


class HousePriceSource(TranslatableModel):
    """House price source"""
    translations = TranslatedFields(
        name=models.CharField(max_length=20),
    )

    def __str__(self):
        return self.name


class PriceType(TranslatableModel):
    """Price type"""
    translations = TranslatedFields(
        name=models.CharField(max_length=10),
    )

    def __str__(self):
        return self.name


class UnitType(TranslatableModel):
    """Unit type"""
    translations = TranslatedFields(
        name=models.CharField(max_length=20),
    )

    def __str__(self):
        return self.name


class ResourceUsage(TranslatableModel):
    """Resource usage"""
    translations = TranslatedFields(
        name=models.CharField(max_length=20),
    )

    def __str__(self):
        return self.name

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
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL)

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
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.name} ({self.food_storage.name})'


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
    s1_unit = models.ForeignKey('Unit', on_delete=models.RESTRICT)
    s2_unit = models.ForeignKey('Unit', on_delete=models.RESTRICT)
    s3_unit = models.ForeignKey('Unit', on_delete=models.RESTRICT)

    def __str__(self):
        return self.name


class State(TranslatableModel):
    """State"""
    country = models.ForeignKey(Country, on_delete=models.RESTRICT)
    iso_code = models.CharField(max_length=5, unique=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=30),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

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
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

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


class PointOfSale(models.Model):
    country = models.ForeignKey(Country, on_delete=models.RESTRICT)
    name = models.CharField(max_length=30)
    informal = models.BooleanField(default=False)
    address = models.CharField(max_length=100)
    is_wholesale = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

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
    currency_from = models.ForeignKey(Currency, on_delete=models.RESTRICT)
    currency_to = models.ForeignKey(Currency, on_delete=models.RESTRICT)
    rate = models.FloatField()

    def __str__(self):
        return f'{self.date_from}:{self.currency_from.name}:{self.currency_to.name}:{self.rate}'

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
        else:
            obj.updated_by = request.user
            super().save_model(request, obj, form, change)
