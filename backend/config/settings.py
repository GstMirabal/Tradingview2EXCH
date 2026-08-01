"""==============================================================================

          PROFESSIONAL DJANGO PROJECT SETTINGS TEMPLATE.

This file provides a robust, secure, and production-ready Django configuration.
It is designed as a generic foundation for any professional project, covering:
  - Dynamic path configuration, compatible with Docker and local development.
  - Secure loading of secrets and variables from a `config.toml` file.
  - A comprehensive set of security configurations following industry
    best practices.

This configuration serves as a production-ready template that demonstrates a
deep understanding of Django's operational and security architecture.

For more information on this file, see:
https://docs.djangoproject.com/en/6.0/topics/settings/

For the full list of settings and their values, see:
https://docs.djangoproject.com/en/6.0/ref/settings/

==============================================================================
"""

# --- Required imports at the top of the file ---
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, override

import envtoml
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger('django')

# ------------------------------------------------------------------------------
# SECTION 1: BASE_DIR, CONFIGURATION PATH, AND ENVIRONMENT LOADING
default_base_dir: Path = Path(__file__).resolve().parent.parent.parent
env_base_dir: str | None = os.environ.get('BASE_DIR')
BASE_DIR: Path = Path(env_base_dir) if env_base_dir else default_base_dir

# `.env` is loaded here, not in `manage.py`.
#
# Every entrypoint imports settings; only one imports `manage.py`. Loading it
# there meant `wsgi`, `asgi` and any test runner started without it — and those
# first two are how this project is actually served in production.
#
# `setdefault`, not assignment. The previous loader assigned, so a value
# exported by the shell, the container or the orchestrator was overwritten by
# whatever `.env` happened to hold. `DEBUG=false ./manage.py check --deploy`
# read `DEBUG` back as true and validated nothing. That matters more here than
# in most projects: `DEBUG` also selects between a Binance dry run and a live
# order (`docs/contracts/WEBHOOK_RECEIVER_CONTRACT.md`).
env_file = BASE_DIR / '.env'
if env_file.exists():
    with env_file.open(encoding='utf-8') as env_handle:
        for raw_line in env_handle:
            stripped = raw_line.strip()
            if not stripped or stripped.startswith('#') or '=' not in stripped:
                continue
            env_key, env_value = stripped.split('=', 1)
            os.environ.setdefault(
                env_key.strip(), env_value.strip().strip('"').strip("'")
            )

config_path = BASE_DIR / 'config.toml'

try:
    # Binary mode is required from envtoml 0.4, which parses through the
    # standard library's `tomllib` instead of the third-party `toml` package.
    with config_path.open('rb') as f:
        config: Any = envtoml.load(f)
except FileNotFoundError as e:
    raise ImproperlyConfigured(
        f'FATAL: The configuration file "config.toml" was not found. '
        f'Expected location: {config_path}'
    ) from e


def _config_bool(value: object, *, default: bool = False) -> bool:
    """Parses a config value that must be a boolean but arrives as a string.

    `envtoml` substitutes an unset/text `$VAR` reference into a quoted TOML
    string, so `DEBUG = "$DEBUG"` resolves to the Python string `'False'`,
    not the boolean `False` — and any non-empty string is truthy in Python,
    so a naive `if DEBUG:` would treat `DEBUG="False"` as true. This exists
    specifically to avoid that: a real deployment setting `DEBUG="False"` or
    `EMAIL_USE_TLS="False"` in `.env` must actually resolve to `False`.

    Args:
        value: The raw config value (usually a string like `'True'`/`'False'`).
        default: Returned when `value` is None or an empty string.

    Returns:
        The parsed boolean.
    """
    if isinstance(value, bool):
        return value
    if not value:
        return default
    return str(value).strip().lower() in ('true', '1', 'yes', 'on')


# ==============================================================================
# SECTION 2: CORE SECURITY SETTINGS
# ==============================================================================

# --- 2.1 SECRET KEY (SECRET_KEY) ---
# Ensures the application fails immediately if the SECRET_KEY is not configured.
# Documentation: https://docs.djangoproject.com/en/6.0/ref/settings/#secret-key
# ------------------------------------------------------------------------------
try:
    SECRET_KEY = config['django_settings']['DJANGO_SECRET_KEY']
    if not SECRET_KEY:
        raise ValueError('DJANGO_SECRET_KEY must not be empty.')
except (KeyError, ValueError) as e:
    raise ImproperlyConfigured(
        'CRITICAL: The DJANGO_SECRET_KEY is missing or empty in your '
        f'config.toml / .env file. Error: {e}'
    ) from e


# --- 2.2 DEBUG MODE (DEBUG) ---
# SECURITY WARNING: Never run with debug turned on in production!
# Documentation: https://docs.djangoproject.com/en/6.0/ref/settings/#debug
# ------------------------------------------------------------------------------
DEBUG = _config_bool(config['django_settings'].get('DEBUG'))


# --- 2.3 ALLOWED HOSTS (ALLOWED_HOSTS) ---
# A critical security measure to prevent HTTP Host Header attacks.
# Documentation: https://docs.djangoproject.com/en/6.0/ref/settings/#allowed-hosts
# ------------------------------------------------------------------------------
if DEBUG:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
else:
    try:
        allowed_hosts_str = config['django_settings'].get('ALLOWED_HOSTS')
    except KeyError:
        allowed_hosts_str = None

    ALLOWED_HOSTS = (
        [host.strip() for host in allowed_hosts_str.split(',') if host.strip()]
        if allowed_hosts_str
        else []
    )

if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        'CRITICAL: Running in PRODUCTION mode (DEBUG=False) but '
        '`ALLOWED_HOSTS` is empty. Define it in the '
        '`[django_settings]` section of `config.toml`.'
    ) from None


# --- 2.4 ALLOWED ORIGINS FOR CORS (CORS_ALLOWED_ORIGINS) ---
# Controls which frontend domains can access this API.
# Documentation (django-cors-headers): https://github.com/adamchainz/django-cors-headers
# ------------------------------------------------------------------------------
if DEBUG:
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:5173',
        'http://localhost:4200',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:4200',
    ]
else:
    try:
        cors_origins_str = config['django_settings'].get('CORS_ALLOWED_ORIGINS')
    except KeyError:
        cors_origins_str = None

    CORS_ALLOWED_ORIGINS = (
        [origin.strip() for origin in cors_origins_str.split(',') if origin.strip()]
        if cors_origins_str
        else []
    )

if not DEBUG and not CORS_ALLOWED_ORIGINS:
    raise ImproperlyConfigured(
        'CRITICAL: Running in PRODUCTION mode (DEBUG=False) but '
        '`CORS_ALLOWED_ORIGINS` is empty. Define it in the '
        '`[django_settings]` section of `config.toml`.'
    ) from None


# ==============================================================================
# SECTION 3: PRODUCTION-ONLY SECURITY ENHANCEMENTS
# ==============================================================================
# Hardens the application when `DEBUG` is False by configuring security headers.
# Documentation: https://docs.djangoproject.com/en/6.0/topics/security/#security-middleware
# ------------------------------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    # Without this, SECURE_SSL_REDIRECT can't tell HTTPS was already
    # terminated by a reverse proxy (nginx/Traefik/a cloud load balancer —
    # gunicorn itself never terminates TLS) and redirects every request in
    # an infinite loop. This trusts the de facto standard header; if you
    # deploy gunicorn directly with no TLS-terminating proxy in front, set
    # SECURE_SSL_REDIRECT = False instead, since there's nothing to redirect to.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    # django-csp>=4.0 reads CONTENT_SECURITY_POLICY (a dict), not the old flat
    # CSP_* settings — the old style is a hard system-check Error (csp.E001)
    # on this version, not a warning, and prevents Django from starting.
    CONTENT_SECURITY_POLICY = {'DIRECTIVES': {'default-src': ["'self'"]}}
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_REFERRER_POLICY = 'no-referrer'
    SECURE_PERMISSIONS_POLICY = {
        'geolocation': '()',
        'microphone': '()',
        'camera': '()',
        'fullscreen': '()',
        'payment': '()',
    }


# ==============================================================================
# SECTION 4: APPLICATION DEFINITION
# ==============================================================================
# Informs Django which applications are active. Organized into three tiers.
# Documentation: https://docs.djangoproject.com/en/6.0/ref/settings/#installed-apps
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    # Django Core Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-Party Apps
    'corsheaders',
    'csp',
    'rest_framework',
    'drf_yasg',
    # Local Project Apps
    'apps.core',
    'apps.Webhook_Receiver',
    'apps.Binance_Connector',
]


# ==============================================================================
# SECTION 5: MIDDLEWARE AND CORE CONFIGURATION
# ==============================================================================

# -- 5.1: Middleware --
# The request/response processing pipeline. Order is critical.
# Documentation: https://docs.djangoproject.com/en/6.0/ref/middleware/
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',  # Recommended to be placed high in the stack
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -- 5.2: Root URL Configuration --
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

# -- 5.3: Template Configuration --
# ------------------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }
]

# -- 5.4: Application Server Entry Point --
# ------------------------------------------------------------------------------
WSGI_APPLICATION = 'config.wsgi.application'


# ==============================================================================
# SECTION 6: DATABASE CONFIGURATION
# ==============================================================================
# This project runs exclusively on SQLite — confirmed against the real
# db.sqlite3 in use. There is no Postgres/MySQL support; a prior template
# revision left a Postgres code path here that was never actually adopted.
# Docs: https://docs.djangoproject.com/en/6.0/ref/settings/#databases
# ------------------------------------------------------------------------------
try:
    db_components = config.get('DB', {})
    # `or` (not `.get(key, default)`) because envtoml substitutes an unset
    # $SQLITE_NAME with an empty string rather than omitting the key, so the
    # dict-default form never actually falls back to 'db.sqlite3'.
    sqlite_db_name = db_components.get('SQLITE_NAME') or 'db.sqlite3'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / sqlite_db_name,
        }
    }
    logger.info('Using SQLite database at %s', BASE_DIR / sqlite_db_name)

except (KeyError, ValueError) as e:
    raise ImproperlyConfigured(
        'CRITICAL: Database configuration failed. Check the [DB] section in '
        f'config.toml and .env file. Original error: {e}'
    ) from e


# ==============================================================================
# SECTION 6.1: DJANGO REST FRAMEWORK
# ==============================================================================
# ScopedRateThrottle only throttles views that declare a `throttle_scope`
# (WebhookReceivedView) — every other view is unaffected by default.
# Docs: https://www.django-rest-framework.org/api-guide/throttling/
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.ScopedRateThrottle'],
    'DEFAULT_THROTTLE_RATES': {
        'webhook': '20/min',
    },
}


# ==============================================================================
# SECTION 6.4: EXCHANGE TRADING MODE
# ==============================================================================
# Whether an order reaches the exchange for real.
#
# This was derived from DEBUG until Sprint #003, which coupled a Django
# presentation flag to capital movement and cut both ways: any environment
# running DEBUG=false placed live orders, and a production host left with
# DEBUG=true stopped trading while still answering 201.
#
# Absent, it is False: the connector calls `new_order_test`, which the exchange
# validates and never executes. Trading with real money now requires writing it
# down. `apps.Binance_Connector.checks` reports the omission at startup, so a
# deployment that meant to trade is told why it is not.
# ------------------------------------------------------------------------------
BINANCE_LIVE_TRADING: bool = _config_bool(
    config.get('binance', {}).get('LIVE_TRADING'), default=False
)


# ==============================================================================
# SECTION 6.5: CACHE CONFIGURATION
# ==============================================================================
# Declared explicitly rather than left to Django's implicit per-process
# LocMemCache, because something here depends on it: DRF stores throttle
# counters in the default cache (`rest_framework/throttling.py`,
# `SimpleRateThrottle.cache`).
#
# The `webhook` scope is capped at 20/min, and that cap is the only limit
# between a caller holding the passphrase and an unbounded number of orders.
# On a per-process backend the cap is per worker, so it multiplies by the
# worker count without anything reporting it. `entrypoint.sh` currently runs
# gunicorn with no `--workers` flag, so one worker, so 20/min is 20/min today —
# and adding a worker for throughput would quietly make it 40.
#
# Redis when REDIS_URL is configured, per-process otherwise. See
# Django-Pro-Template ADR-0005 for why the fallback is silent rather than a
# hard failure.
# ------------------------------------------------------------------------------
cache_config = config.get('cache', {})
REDIS_URL: str | None = cache_config.get('REDIS_URL') or os.environ.get('REDIS_URL')

if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'tradingview2exch',
        }
    }


# ==============================================================================
# SECTION 7: PASSWORD VALIDATION AND HASHING
# ==============================================================================

# -- 7.1: Password Validators --
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators
# ------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
        'UserAttributeSimilarityValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'apps.core.validators.PasswordComplexityValidator'},
    {'NAME': 'pwned_passwords_django.validators.PwnedPasswordsValidator'},
]

# -- 7.2: Password Hashers --
# https://docs.djangoproject.com/en/6.0/topics/auth/passwords/#password-storage
# ------------------------------------------------------------------------------
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# ==============================================================================
# SECTION 8: USER MODEL, INTERNATIONALIZATION, AND FILES
# ==============================================================================

# -- 8.1: User Model --
# This project deliberately uses Django's built-in auth.User model, not a
# custom one — there is no `users` app and none is planned.
# https://docs.djangoproject.com/en/6.0/topics/auth/customizing/#substituting-a-custom-user-model
# ------------------------------------------------------------------------------

# -- 8.2: Internationalization (i18n) --
# https://docs.djangoproject.com/en/6.0/topics/i18n/
# ------------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
# `or` (not `.get(key, default)`) — see the SQLITE_NAME comment in Section 6:
# envtoml substitutes an unset $TIME_ZONE with an empty string, not a missing key.
TIME_ZONE = config['django_settings'].get('TIME_ZONE') or 'UTC'
USE_I18N = True
USE_TZ = True  # Saves datetimes in UTC in the DB.

# -- 8.3: Static and Media Files --
# https://docs.djangoproject.com/en/6.0/howto/static-files/
# ------------------------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'


# ==============================================================================
# SECTION 9: EMAIL CONFIGURATION
# ==============================================================================
# Dynamically configures the email backend based on the DEBUG flag.
# Docs: https://docs.djangoproject.com/en/6.0/topics/email/
# ------------------------------------------------------------------------------
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    try:
        email_config = config['email_settings']
        EMAIL_HOST: str = email_config['EMAIL_HOST']
        EMAIL_PORT = email_config['EMAIL_PORT']
        EMAIL_USE_TLS = _config_bool(email_config['EMAIL_USE_TLS'], default=True)
        EMAIL_HOST_USER: str = email_config['EMAIL_HOST_USER']
        EMAIL_HOST_PASSWORD: str = email_config['EMAIL_HOST_PASSWORD']

        if not all([EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD]):
            raise ValueError(
                'EMAIL_HOST, EMAIL_HOST_USER, and EMAIL_HOST_PASSWORD '
                'must not be empty in production.'
            )
    except (KeyError, ValueError) as e:
        raise ImproperlyConfigured(
            'CRITICAL: Production email configuration failed. Check the '
            f'[email_settings] section in config.toml and .env. Original error: {e}'
        ) from e


# ==============================================================================
# SECTION 10: DEFAULT PRIMARY KEY FIELD TYPE
# ==============================================================================
# https://docs.djangoproject.com/en/6.0/ref/settings/#default-auto-field
# ------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==============================================================================
# SECTION 11: PROFESSIONAL LOGGING CONFIGURATION
# ==============================================================================
# Production-ready logging setup, adaptable to different environments.
# https://docs.djangoproject.com/en/6.0/topics/logging/
# ------------------------------------------------------------------------------


class UTCFormatter(logging.Formatter):
    """Custom logging formatter to ensure all timestamps are in UTC.

    Follows the ISO 8601 standard for unambiguous logging across environments.

    Args:
        record (logging.LogRecord): The log record entry.
        datefmt (Optional[str]): Format string for the date. Defaults to ISO-8601.

    Returns:
        str: The ISO-8601 formatted timestamp string in UTC.
    """

    @override
    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        dt = datetime.fromtimestamp(record.created, tz=UTC)
        return dt.strftime(datefmt or '%Y-%m-%dT%H:%M:%SZ')


try:
    logs_dir_str = config['project_logging'].get('PROJECT_LOGS_DIR')
    if logs_dir_str:
        logs_dir = Path(logs_dir_str)
        logs_dir.mkdir(parents=True, exist_ok=True)
    else:
        raise ValueError('PROJECT_LOGS_DIR is not defined in config.toml')
except (KeyError, ValueError) as e:
    raise ImproperlyConfigured(f'Logging directory setup failed. Error: {e}') from e


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {'format': '{levelname} [{name}] {message}', 'style': '{'},
        'verbose': {
            '()': UTCFormatter,
            'format': '{levelname} {asctime} {module} [{funcName}:{lineno}] {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': (
                '%(asctime)s %(name)s %(levelname)s %(module)s %(lineno)d %(message)s'
            ),
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'project_log_file': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': logs_dir / 'project.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'project_json_file': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': logs_dir / 'project.json',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'json',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'project_log_file', 'project_json_file'],
            'level': 'DEBUG' if DEBUG else 'WARNING',
            'propagate': False,
        },
        'project': {
            'handlers': ['console', 'project_log_file', 'project_json_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
# ------------------------------------------------------------------------------
