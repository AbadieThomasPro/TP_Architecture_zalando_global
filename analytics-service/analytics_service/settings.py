import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-me')
DEBUG = os.getenv('DJANGO_DEBUG', '1') == '1'

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,analytics-service').split(',')
    if host.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'analytics',
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

ROOT_URLCONF = 'analytics_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'analytics_service.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'analytics_db'),
        'USER': os.getenv('DB_USER', 'analytics_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'analytics_password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5435'),
    },
    'customer_source': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'customer_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'customer-db',
        'PORT': '5432',
    },
    'catalog_source': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'catalog_db',
        'USER': 'catalog_user',
        'PASSWORD': 'catalog_password',
        'HOST': 'catalog-db',
        'PORT': '5432',
    },
    'order_source': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'order_service_db',
        'USER': 'order_service_user',
        'PASSWORD': 'order_service_password',
        'HOST': 'order-db',
        'PORT': '5432',
    },
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'