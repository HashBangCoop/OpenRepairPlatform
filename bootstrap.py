#!/usr/bin/env python3
import logging

from django.db.utils import IntegrityError

from users.models import CustomUser

# don't choke if
try:
    CustomUser.objects.create_superuser("admin@example.com", "foobar")
except IntegrityError:
    logging.info("admin user was already created, moving on")
