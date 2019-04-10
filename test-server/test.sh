#!/bin/bash

cd /mnt/server

pip uninstall django-payment
pip install /mnt/payment

python manage.py test --keepdb