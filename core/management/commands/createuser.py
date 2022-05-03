import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model

        email = input("email: ")
        password = input("password: ")
        username = input("username: ")
        User = get_user_model()

        user = User.objects.create_user(email, password=password)
        user.username = username
        user.is_active = True    
        user.is_superuser = False
        user.is_staff = False
        user.save()
        print("User created")
        
