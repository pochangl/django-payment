#!/bin/bash
set -e

rm -r /server
rm -r /payment

cp -r /mnt/server /server
cp -r /mnt/payment /payment

cd /server

pip install -e /payment
echo 'running test'
python manage.py makemigrations product
python manage.py test --keepdb
