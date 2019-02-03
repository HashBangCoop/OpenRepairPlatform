from __future__ import absolute_import # optional, but I like it

from .common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'H/hXAUnb1ZKNGpToim2cg38dxiyHM6b+zB9zozhpTzkP'

# TODO for the address module; change it!
GOOGLE_API_KEY = "AIzaSyAYCYw3z7WEG8ttiZ53WyEvrOd0fDDlHeU"

# STATICFILES_STORAGE disabled in test environement
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

