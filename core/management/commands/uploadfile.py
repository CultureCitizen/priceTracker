import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

# import models from parent directory
from core.models import Country, State, City, AppLanguage
import csv


class Command(BaseCommand):

    # uploadfile classname filename
    def handle(self, *args, **options):
        if args.count == 0:
            classname = input("classname: ")
            filename = input("filename: ")
            dialect = input(f"dialect {csv.list_dialects()}: ")
        elif args.count == 1:
            classname = args[0]
            filename = input("filename: ")
            dialect = input(f"dialect {csv.list_dialects()}: ")
        elif args.count == 2:
            classname = args[0]
            filename = args[1]
            dialect = input(f"dialect {csv.list_dialects()}: ")
        else:
            classname = args[0]
            filename = args[1]
            dialect = args[2]

        # create a set with the values Country,State,City,Language
        set = {'Country', 'State', 'City', 'Language'}
        if classname not in set:
            print("classname must be one of the following: Country,State,City,Language")
            return

        # read file from operating system
        with open(csv.reader(filename, dialect=dialect)) as reader:
            for row in reader:
                if classname == "Country":
                    obj = Country.objects.create()
                    obj.iso_code = row[0]
                    obj.name_en = row[1]
                    obj.name = row[0]
                    obj.save()
                elif classname == "State":

                    country = Country.objects.get(iso_code=row[0])
                    obj = State.objects.create()
                    obj.iso_code = row[1]
                    obj.name_en = row[2]
                    obj.name = row[1]
                    obj.country_id = country.id
                    obj.save()

                elif classname == "City":
                    state = State.objects.get(iso_code=row[0])
                    obj = City.objects.create()
                    obj.iso_code = row[1]
                    obj.name_en = row[2]
                    obj.name = row[1]
                    obj.state_id = state.id
                    obj.save()

                elif classname == "Language":
                    obj = AppLanguage.objects.create()
                    obj.iso_code = row[0]
                    obj.name_en = row[1]
                    obj.name = row[1]
                    obj.save()
