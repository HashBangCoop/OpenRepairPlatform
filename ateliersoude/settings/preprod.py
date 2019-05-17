from .base import *  # noqa

SECRET_KEY = "H/hXAUnb1ZKNGpToim2cg38dxiyHM6b+zB9zozhpTzkP"

DEBUG = False

ALLOWED_HOSTS = ["ateliersoude.hashbang.fr"]

INSTALLED_APPS += ["raven.contrib.django.raven_compat"]  # noqa

STATIC_ROOT = "/srv/app/ateliersoude/static/"
MEDIA_ROOT = "/srv/app/ateliersoude/media/"
ASSETS_ROOT = STATIC_ROOT


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ateliersoude",
        "USER": "ateliersoude",
    }
}

RAVEN_CONFIG = {
    "dsn": "http://0e041413044f46ff86cedea29c38048d:"
    "b0a68625ae8b4f85bb4e3891a98475b4@sentry.hashbang.fr/40"
}


# Email Settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "mail.atelier-soude.fr"
EMAIL_PORT = 25
EMAIL_HOST_USER = "no-reply@atelier-soude.fr"
EMAIL_HOST_PASSWORD = "noreplyeconomieparticipative"
