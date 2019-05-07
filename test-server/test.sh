#!/bin/bash

cd /mnt/server
# python manage.py makemigrations payment
python manage.py test --keepdb package
