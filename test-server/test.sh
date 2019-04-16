#!/bin/bash

cd /mnt/server
# python manage.py makemigrations product
python manage.py test --keepdb
