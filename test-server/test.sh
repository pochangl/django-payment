#!/bin/bash

cd /mnt/server
python manage.py test --keepdb payment.backends.ecpay.tests.forms
