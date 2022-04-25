# import postgresql package
from unicodedata import name
import psycopg2 as pg
import os

# connect to postgresql database
DJANGO_LOCAL = os.getenv("DJANGO_LOCAL", "False")

try:
    #   Testing in my local machine
    if DJANGO_LOCAL == "True":
        db = {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': '127.0.0.1',
            'NAME': 'priceTracker',
            'USER': 'priceTracker',
            'PASSWORD': '2022Tracker!',
            'PORT': 5432,
        }
    else:
        print("eneter password")
        pwd = input()
        db = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "HOST": "app-b0c0cbba-d5df-4ffb-88b5-5a3a2df1f91a-do-user-7594820-0.b.db.ondigitalocean.com",
                "NAME": "pt",
                "USER": "pt",
                "PASSWORD": pwd,
                "PORT": 25060,
            }
        }
    conn = pg.connect(host=db["HOST"], dbname=db["NAME"], user=db["USER"],
                      password=db["PASSWORD"], port=db["PORT"])

    print(conn)
    # Create a cursor to perform database operations
    cursor = conn.cursor()
    # Print PostgreSQL details
    print("PostgreSQL server information")
    print(conn.get_dsn_parameters(), "\n")
    # Executing a SQL query
    cursor.execute("SELECT version();")
    # Fetch result
    record = cursor.fetchone()
    print("You are connected to - ", record, "\n")

except (Exception, pg.DatabaseError) as error:
    print("Error while connecting to PostgreSQL", error)
else:
    if conn:
        conn.close()
        print("Database connection closed.")