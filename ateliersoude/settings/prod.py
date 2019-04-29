from .base import *  # noqa

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "H/hXAUnb1ZKNGpToim2cg38dxiyHM6b+zB9zozhpTzkP"

DEBUG = False

EMAIL_ADRESSE = environ.get("EMAIL_ADRESSE")

EMAIL_USE_TLS = True
EMAIL_HOST = environ.get("SMTP_HOST")
EMAIL_HOST_USER = EMAIL_ADRESSE
EMAIL_HOST_PASSWORD = environ.get("EMAIL_PASSWORD")
EMAIL_PORT = 587
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
DEFAULT_FROM_EMAIL = EMAIL_ADRESSE
SERVER_EMAIL = EMAIL_ADRESSE
