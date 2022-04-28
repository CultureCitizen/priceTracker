"""
Django settings for priceTracker project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

# Added by adelatorre
import os
import sys
import dj_database_url
import socket

from pathlib import Path
from django.core.management.utils import get_random_secret_key

# Added by adelatorre
#socket.getaddrinfo('localhost', 8080)

DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "True"

# local development environment?
DJANGO_LOCAL = os.getenv("DJANGO_LOCAL", "False")
print("DJANGO_LOCAL=", DJANGO_LOCAL)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Added by adelatorre
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())


# SECURITY WARNING: don't run with debug turned on in production!

# ------------------------------------------------------------------------------
# DEVELOPMENT ENVIRONMENT
# Added by adelatorre
DEBUG = os.getenv("DEBUG", "False") == "True"
DEBUG = True
DEVELOPMENT_MODE = True
# ------------------------------------------------------------------------------


# Added by adelatorre
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS",
                          "127.0.0.1,localhost").split(",")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_extensions',
    'parler',
    # my apps
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'priceTracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'priceTracker.wsgi.application'

# --------------------------------------------------------------------------
# The user is provided by the class User in the module core
AUTH_USER_MODEL = 'core.User'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

pghost = os.getenv("PGHOST", "")
pgport = os.getenv("PGPORT", "")
dburl = os.getenv("DATABASE_URL", "")
pgdatabase = os.getenv("PGDATABASE", "")
pwd = os.getenv("DB_PT", "")

if DEVELOPMENT_MODE is True:
    #   Testing in my local machine
    if DJANGO_LOCAL is True:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'HOST': '127.0.0.1',
                'NAME': 'priceTracker',
                'USER': 'priceTracker',
                'PASSWORD': pwd,
                'PORT': 5432,
            }
        }
#   Testing in digital ocean server
    else:
        print("DATABASE_URL=", dburl)
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "HOST": "app-b0c0cbba-d5df-4ffb-88b5-5a3a2df1f91a-do-user-7594820-0.b.db.ondigitalocean.com",
                "NAME": "pt",
                "USER": "pt",
                "PASSWORD": pwd,
                "PORT": 25060,
                "OPTIONS": {'sslmode': 'require'},
            }
        }
elif len(sys.argv) > 0 and sys.argv[1] == "collectstatic":
    if os.getenv("DATABASE_URL", None) is None:
        raise Exception("DATABASE_URL is not defined")
    DATABASES = {
        "default": dj_database_url.parse(os.environ.get("DATABSE_URL")),
    }

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True

PARLER_LANGUAGES = {
    None: (
        {'code', 'en'},
        {'code', 'es'},
    ),
    'default': {
        'fallback': 'en',
        'hide_untranslated': False,
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
print("static root:", STATIC_ROOT)

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# Email confirmation
# ==============================================================================

DJOSER = {
    "USER_ID_FIELD": "username",
    "LOGIN_FIELD": "email",
    "SEND_ACTIVATION_EMAIL": True,
    "ACTIVATION_URL": "activate/{uid}/{token}",
    'SERIALIZERS': {
        'token_create': 'core.serializers.CustomTokenCreateSerializer',
    },
}

# Dummy email backend : it only displays the mails in the console.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
SITE_NAME = "pricetracker"


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
}
