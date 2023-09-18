#!/bin/bash
set -e

rm -r /server
rm -r /payment

cp -r /mnt/server /server
cp -r /mnt/payment /payment

cd /server

pip install -e /mnt/payment
echo 'running test'
python manage.py makemigrations
python manage.py test --keepdb