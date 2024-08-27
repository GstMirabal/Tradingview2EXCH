"""
Django settings for the APIRest_Connector project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from django.core.management import call_command
from pathlib import Path
import os
import envtoml

# Read the config.toml file
config_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'config.toml')

config = envtoml.load(open(config_path))

# Define BASE_DIR as the base directory from the config file, or use the default if not configured
default_base_dir = Path(__file__).resolve().parent.parent
BASE_DIR = config['project'].get('BASE_DIR', default_base_dir)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'm0#ym%s+1@&je(94%s1z3zry*%2cw_i6df92qsd@eyd9uez(06'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config['security'].get('DEBUG')

ALLOWED_HOSTS = [config['security'].get(
    'ALLOWED_HOSTS'), config['security'].get('LOCAL_HOST')]

# Security settings for development
SECURE_BROWSER_XSS_FILTER = config['security'].get(
    'SECURE_BROWSER_XSS_FILTER', False)
X_FRAME_OPTIONS = config['security'].get('X_FRAME_OPTIONS')
SECURE_CONTENT_TYPE_NOSNIFF = config['security'].get(
    'SECURE_CONTENT_TYPE_NOSNIFF', False)
CSRF_COOKIE_SECURE = config['security'].get('CSRF_COOKIE_SECURE', False)
SESSION_COOKIE_SECURE = config['security'].get('SESSION_COOKIE_SECURE', False)
SECURE_SSL_REDIRECT = config['security'].get('SECURE_SSL_REDIRECT', False)
SECURE_HSTS_SECONDS = config['security'].get('SECURE_HSTS_SECONDS', 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config['security'].get(
    'SECURE_HSTS_INCLUDE_SUBDOMAINS', False)
SECURE_HSTS_PRELOAD = config['security'].get('SECURE_HSTS_PRELOAD', False)

# Additional settings to ensure HTTPS is not enforced in development
if DEBUG:
    SECURE_SSL_REDIRECT = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False

# Email configuration
EMAIL_BACKEND = config['email'].get('EMAIL_BACKEND')
EMAIL_HOST = config['email'].get('EMAIL_HOST')
EMAIL_PORT = config['email'].get('EMAIL_PORT')
EMAIL_USE_TLS = config['email'].get('EMAIL_USE_TLS')
EMAIL_USE_SSL = config['email'].get('EMAIL_USE_SSL')
EMAIL_HOST_USER = config['email'].get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config['email'].get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config['email'].get('DEFAULT_FROM_EMAIL')

# Warning if EMAIL_HOST_PASSWORD is not set
if not EMAIL_HOST_PASSWORD:
    import warnings
    warnings.warn(
        "EMAIL_HOST_PASSWORD is not set in the environment variables.")

# Logging configuration
LOG_LEVEL = config['logging'].get('LOG_LEVEL')
LOG_FILE = config['logging'].get('LOG_FILE')

# Create the log file if it does not exist
log_file_path = os.path.join(BASE_DIR, LOG_FILE)
if not os.path.exists(log_file_path):
    open(log_file_path, 'a').close()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': log_file_path,
        },
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',
    'Webhook_Receiver',
    'Binance_Connector'
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

ROOT_URLCONF = 'tradingview2exch.urls'

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

WSGI_APPLICATION = 'tradingview2exch.wsgi.application'

# Database configuration
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': config['db'].get('ENGINE', 'django.db.backends.sqlite3'),
        'NAME': BASE_DIR / config['db'].get('NAME', 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

# Internationalization settings
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'