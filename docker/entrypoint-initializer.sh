#!/bin/sh

python manage.py makemigrations dojo
python manage.py makemigrations --merge --noinput
python manage.py migrate
cat <<EOD | python manage.py shell
import os
from django.contrib.auth.models import User
User.objects.create_superuser(
    os.getenv('DD_ADMIN_USER'),
    os.getenv('DD_ADMIN_MAIL'),
    os.getenv('DD_ADMIN_PASSWORD'),
    first_name=os.getenv('DD_ADMIN_FIRST_NAME'),
    last_name=os.getenv('DD_ADMIN_LAST_NAME')
)
EOD

python manage.py loaddata product_type
python manage.py loaddata test_type
python manage.py loaddata development_environment
python manage.py loaddata system_settings
python manage.py loaddata benchmark_type
python manage.py loaddata benchmark_category
python manage.py loaddata benchmark_requirement
python manage.py loaddata language_type
python manage.py loaddata objects_review
python manage.py loaddata regulation
python manage.py installwatson
python manage.py buildwatson
