#!/bin/bash

cd /mnt/server
python manage.py makemigrations
python manage.py test --keepdb payment.tests.views
