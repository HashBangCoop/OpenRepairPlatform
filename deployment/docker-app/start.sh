#!/usr/bin/env bash

service cron start
service postgresql start
su postgres -c "psql -c \"CREATE USER ateliersoude WITH PASSWORD ''\""
su postgres -c "createdb -O ateliersoude ateliersoude"
su ateliersoude -c "python manage.py migrate"
su ateliersoude -c "python manage.py shell -c \"from ateliersoude.user.models import CustomUser; CustomUser.objects.create_superuser('admin@example.com', 'adminpass')\""
su ateliersoude -c "python manage.py runserver 0.0.0.0:8000"
