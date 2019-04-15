#!/usr/bin/python
# -*- coding: UTF-8 -*-
import datetime
import string
import calendar
import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from .models import ECPayReceive
from .settings import settings
from .utils import get_CheckMacValue, format_time


class CMVGenMixin:
    class Meta:
        abstract = True

    def clean(self):
        cleaned_data = super(CMVGenMixin, self).clean()
        cleaned_data["CheckMacValue"] = self.data["CheckMacValue"] = get_CheckMacValue(cleaned_data)
        return cleaned_data


class CMVCheckMixin(object):
    def clean(self):
        cleaned_data = super(CMVCheckMixin, self).clean()
        CheckMacValue = get_CheckMacValue(self.data)
        if CheckMacValue != self.data["CheckMacValue"].upper():
            raise ValidationError("MacValue Doesn't match")
        else:
            return cleaned_data


class ECPayAIOPNForm(CMVCheckMixin, forms.ModelForm):
    # form for receive ec pay payment notiifcation

    PaymentDate = forms.DateTimeField(input_formats=[settings.DateTimeFormat])
    TradeDate = forms.DateTimeField(input_formats=[settings.DateTimeFormat])

    def clean_RtnCode(self):
        if self.cleaned_data["RtnCode"] != 1:
            raise ValidationError("Return Code Error, payment aborted")
        else:
            return self.cleaned_data["RtnCode"]

    def clean_MerchantID(self):
        if self.cleaned_data["MerchantID"] != settings.MerchantID:
            raise ValidationError("Wrong Vendor ID")
        else:
            return self.cleaned_data["MerchantID"]

    class Meta:
        model = ECPayReceive
        fields = '__all__'


class ECPayPayForm(CMVGenMixin, forms.Form):
    submit_url = settings.AioCheckOut_URL
    MerchantID = forms.CharField(initial=settings.MerchantID, max_length=10,
                                 required=False)
    MerchantTradeNo = forms.CharField(max_length=20)
    MerchantTradeDate = forms.CharField(max_length=20)
    PaymentType = forms.CharField(initial=settings.PaymentType)
    TotalAmount = forms.IntegerField()
    TradeDesc = forms.CharField(max_length=200)
    ItemName = forms.CharField(max_length=200)
    ReturnURL = forms.URLField()
    ChoosePayment = forms.ChoiceField(choices=settings.PaymentChoices)
    ClientBackURL = forms.URLField(max_length=200)
    EncryptType = forms.IntegerField()
    ExpireDate = forms.IntegerField()
    ItemURL = forms.URLField(max_length=200)

    def clean_EncryptType(self):
        return 1

    def __init__(self, data, *args, **kwargs):
        data["MerchantTradeDate"] = format_time(data["MerchantTradeDate"])
        data['ExpireDate'] = settings.ExpireDate
        data['EncryptType'] = '1'
        data["MerchantID"] = settings.MerchantID
        super().__init__(data=data, *args, **kwargs)

    class Meta:
        abstract = True


class ECPayAIOLookUpForm(CMVGenMixin, forms.Form):
    MerchantID = forms.CharField(max_length=10)
    MerchantTradeNo = forms.CharField(max_length=20)
    TimeStamp = forms.IntegerField(min_value=0)

    def __init__(self, *args, **kwargs):
        super(ECPayAIOLookUpForm, self).__init__(*args, **kwargs)
        self.data["MerchantID"] = settings.MerchantID
        self.data["TimeStamp"] = calendar.timegm(datetime.datetime.now().utctimetuple())
