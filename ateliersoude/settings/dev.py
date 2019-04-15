from .base import * # noqa


INSTALLED_APPS += [  # noqa
    'debug_toolbar',
]

MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa

INTERNAL_IPS = ["127.0.0.1"]
