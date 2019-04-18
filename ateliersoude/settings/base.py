from os import environ
from os.path import dirname, abspath, join


PROJECT_DIR = dirname(dirname(abspath(__file__)))
BASE_DIR = dirname(PROJECT_DIR)

SECRET_KEY = "H/hXAUnb1ZKNGpToim2cg38dxiyHM6b+zB9zozhpTzkP"

DEBUG = True

ALLOWED_HOSTS = []

SITE_ID = 1

INSTALLED_APPS = [
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.messages",

    "ateliersoude.api",
    "ateliersoude.event",
    "ateliersoude.user",
    "ateliersoude.location",

    "simple_history",
    "rest_framework",
    'bootstrap',
    'fontawesome',
    'django_assets',
]


MIDDLEWARE = [
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "ateliersoude.urls"

AS_CONTEXT = "ateliersoude.context_processors"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            (join(BASE_DIR, "ateliersoude", "templates"))
        ],  # handle the /templates base directory
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                f"{AS_CONTEXT}.user_data",
                f"{AS_CONTEXT}.last_events",
                f"{AS_CONTEXT}.user_in_organization",
                f"{AS_CONTEXT}.admin_of_organizations",
            ]
        },
    }
]

WSGI_APPLICATION = "ateliersoude.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ateliersoude",
    }
}

# custom User model
AUTH_USER_MODEL = "user.CustomUser"

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATION = "django.contrib.auth.password_validation."
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": (AUTH_PASSWORD_VALIDATION + "UserAttributeSimilarityValidator")},
    {"NAME": (AUTH_PASSWORD_VALIDATION + "MinimumLengthValidator")},
    {"NAME": (AUTH_PASSWORD_VALIDATION + "CommonPasswordValidator")},
    {"NAME": (AUTH_PASSWORD_VALIDATION + "NumericPasswordValidator")},
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "Europe/Paris"

USE_I18N = True
USE_L10N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True


STATICFILES_DIRS = [join(PROJECT_DIR, "static")]

STATIC_ROOT = join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = join(BASE_DIR, "media")


# Email Settings
EMAIL_ADRESSE = environ.get("EMAIL_ADRESSE")

EMAIL_USE_TLS = True
EMAIL_HOST = environ.get("SMTP_HOST")
EMAIL_HOST_USER = EMAIL_ADRESSE
EMAIL_HOST_PASSWORD = environ.get("EMAIL_PASSWORD")
EMAIL_PORT = 587
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
DEFAULT_FROM_EMAIL = EMAIL_ADRESSE
SERVER_EMAIL = EMAIL_ADRESSE

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
)

# Config django-assets
ASSETS_MODULES = [
    'ateliersoude.assets'
]
ASSETS_ROOT = STATICFILES_DIRS[0]
