from .base import *  # noqa

SECRET_KEY = "H/hXAUnb1ZKNGpToim2cg38dxiyHM6b+zB9zozhpTzkP"

DEBUG = False

ALLOWED_HOSTS = ["ateliersoude.hashbang.fr"]

STATIC_ROOT = "/srv/app/ateliersoude/static/"
MEDIA_ROOT = "/srv/app/ateliersoude/media/"

INSTALLED_APPS += ["raven.contrib.django.raven_compat"]  # noqa


RAVEN_CONFIG = {
    "dsn": "http://0e041413044f46ff86cedea29c38048d:"
    "b0a68625ae8b4f85bb4e3891a98475b4@sentry.hashbang.fr/40"
}
