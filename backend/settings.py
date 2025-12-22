from pathlib import Path
from environ import environ
from environ.environ import Env
from django.apps import config
from whitenoise.middleware import WhiteNoiseMiddleware
from django.template.backends.django import DjangoTemplates
from django.template.backends import base
from django import shortcuts
from django.conf.urls import static
from django.conf import global_settings
from whitenoise import base
from whitenoise import compress
from whitenoise import responders
from whitenoise import storage
from django.core.mail.backends.smtp import EmailBackend
import os
import environ
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
BASE_URL = "https://advice-project.onrender.com"
# BASE_URL = "http://localhost:8000"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

#settings environment
load_dotenv()
env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY', default='django-insecure-default-key')
DATABASES = {
    'default': env.db(),
    'extra': env.db_url(
        'SQLITE_URL',
        default='sqlite:////tmp/my-tmp-sqlite.db'
    )
}
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['127.0.0.1', 'localhost', 'advice-project.onrender.com', 'wicked-seals-fail.loca.lt', '192.168.0.182', '94.25.185.171'])
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
HF_API_KEY = os.getenv('HF_API_KEY')
HF_API_KEY_FIN = os.getenv('HF_API_KEY_FIN')
HF_API_KEY_UR = os.getenv('HF_API_KEY_UR')
#security for production 
#SECURE_HSTS_SECONDS = 1209600
#SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
#SECURE_HSTS_INCLUDE_SUBDOMAINS = False
#SECURE_HSTS_PRELOAD = False

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = 'django-insecure-eatdin_z3-eb$g*e(%=a+c)$8or4=q$z6xsk=c8!%b))gzu4*p'

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = True

#ALLOWED_HOSTS = []
#ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'aqwe8dea.pythonanywhere.com']

DJSTRIPE_FOREIGN_KEY_TO_FIELD ='id' 

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'aqwe_app.apps.AqweAppConfig',    
    'rest_framework',
    'corsheaders',
    'djstripe',
    'stripe',
    'sslserver',
]
X_FRAME_OPTIONS = 'ALLOW'
CORS_ALLOW_METHODS = ['GET', 'POST', 'OPTIONS']
CORS_ALLOW_HEADERS = ['content-type', 'autorization']
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "https://advice-project.onrender.com",
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "https://advice-project.onrender.com",
]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'aqwe_app.middleware.SessionMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permission.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'frontend/build'],
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

WSGI_APPLICATION = 'backend.wsgi.application'
# settings mail server
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_PORT = 587
#EMAIL_USE_TLS =True
#EMAIL_HOST_USER = env('EMAIL_HOST_USER')
#EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
#DEFAULT_FROM_EMAIL = env('EMAIL_HOST_USER')

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
#DATABASES = {
    #'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
#}
# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
# }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_DIRS = [
    BASE_DIR / 'frontend/build/static',
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#Django settings for backend project.

#Generated by 'django-admin startproject' using Django 5.1.6.

#For more information on this file, see
#https://docs.djangoproject.com/en/5.1/topics/settings/

#For the full list of settings and their values, see
#https://docs.djangoproject.com/en/5.1/ref/settings/
