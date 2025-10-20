from pathlib import Path
import os
from decouple import config
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================
# 🔐 Security Keys
# ==========================
SECRET_KEY = config(
    "DJANGO_SECRET_KEY",
    default="unsafe-secret-key-change-in-production"
)

# ==========================
# 📧 Email Settings
# ==========================
EMAIL_BACKEND = config(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = config("DJANGO_EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("DJANGO_EMAIL_PORT", cast=int, default=587)
EMAIL_USE_TLS = config("DJANGO_EMAIL_USE_TLS", cast=bool, default=True)
EMAIL_HOST_USER = config("DJANGO_EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("DJANGO_EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default=f"Auralis Health <{EMAIL_HOST_USER}>"
)


# ==========================
# 🍪 Session Settings
# ==========================
SESSION_ENGINE = config(
    "SESSION_ENGINE",
    default="django.contrib.sessions.backends.db"
)
SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_AGE = config("SESSION_COOKIE_AGE", cast=int, default=3600)  # 1hr in seconds
SESSION_SAVE_EVERY_REQUEST = config("SESSION_SAVE_EVERY_REQUEST", cast=bool, default=True)
SESSION_EXPIRE_AT_BROWSER_CLOSE = config("SESSION_EXPIRE_AT_BROWSER_CLOSE", cast=bool, default=True)

# ==========================
# ⏳ Token Expiry Times
# ==========================
OTP_EXPIRY_MINUTES = config("OTP_EXPIRY_MINUTES", cast=int, default=10)
PASSWORD_RESET_TOKEN_EXPIRY_HOURS = config("PASSWORD_RESET_TOKEN_EXPIRY_HOURS", cast=int, default=1)

# Helper variables for use in views/services
OTP_EXPIRY_DELTA = timedelta(minutes=OTP_EXPIRY_MINUTES)
PASSWORD_RESET_TOKEN_EXPIRY_DELTA = timedelta(hours=PASSWORD_RESET_TOKEN_EXPIRY_HOURS)


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third-party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'channels',

    # Local apps
    'accounts',
    'monitoring',
    'sync',
    'analytics',
    'notifications',
]

AUTH_USER_MODEL = "accounts.CustomUser"

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',  # fallback
]


# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '1000/day',
        'anon': '50/day',
    }
}

# Simple JWT settings (basic example)
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS (for frontend/mobile)
CORS_ALLOW_ALL_ORIGINS = True  # tighten for production

# Redis Cache (for local dev point to Redis)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
    }
}


ROOT_URLCONF = 'health_monitoring.urls'

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
    },
]

WSGI_APPLICATION = 'health_monitoring.wsgi.application'

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'info',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',  
}

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]  # if you have a global project-level static folder
STATIC_ROOT = BASE_DIR / "staticfiles"    # used when running collectstatic

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"
# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# After login → send user to role-based dashboard redirect
# LOGIN_REDIRECT_URL = "dashboard_redirect"

# If an unauthenticated user hits a @login_required view → send to login page
# LOGIN_URL = "login"

# After logout → send user back to login page
# LOGOUT_REDIRECT_URL = "login"