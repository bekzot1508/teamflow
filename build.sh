#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); email='admin@gmail.com'; password='12345678'; username='admin'; user, created = User.objects.get_or_create(email=email, defaults={'username': username, 'full_name': 'Admin User', 'is_staff': True, 'is_superuser': True}); user.is_staff=True; user.is_superuser=True; user.set_password(password); user.save(); print('superuser ready:', user.email)"