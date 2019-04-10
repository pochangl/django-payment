#!/usr/bin/python
# -*- coding: UTF-8 -*-
import datetime
import string
import calendar
import re

from django import forms
from django.core.exceptions import ValidationError
from .models import ECPayReceive
from .settings import settings
from .utils import get_CheckMacValue


class CMVGenMixin(object):
    class Meta:
        abstract = True

    def clean(self):
        cleaned_data = super(CMVGenMixin, self).clean()
        cleaned_data["CheckMacValue"] = self.data["CheckMacValue"] = \
            get_CheckMacValue(cleaned_data)
        return cleaned_data


class CMVCheckMixin(object):
    def clean(self):
        cleaned_data = super(CMVCheckMixin, self).clean()
        CheckMacValue = get_CheckMacValue(self.data)
        if CheckMacValue != string.upper(self.data["CheckMacValue"]):
            raise ValidationError("MacValue Doesn't match")
        else:
            return cleaned_data


class ECPayAIOPNForm(CMVCheckMixin, forms.ModelForm):
    # form for receive all pay payment notiifcation

    PaymentDate = forms.DateTimeField(input_formats=settings.DateTimeFormats,)
    TradeDate = forms.DateTimeField(input_formats=settings.DateTimeFormats,)

    def clean_PaymentType(self):
        data = self.cleaned_data["PaymentType"]
        if any([re.search(prefix, data) for prefix in settings.ResponsePaymentTypePrefixes]):
            return data
        else:
            raise ValidationError("Wrong Choice")

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
        datetime_format = settings.DateTimeFormats
        fields = '__all__'


class ECPayPayForm(CMVGenMixin, forms.Form):
    CheckMacValue = forms.CharField(required=False)
    submit_url = settings.AioCheckOut_URL
    MerchantID = forms.CharField(initial=settings.MerchantID, max_length=10,
                                 required=False)
    MerchantTradeNo = forms.CharField(max_length=20)
    MerchantTradeDate = forms.CharField(max_length=20, required=False)
    PaymentType = forms.CharField(initial=settings.PaymentType)
    TotalAmount = forms.IntegerField()
    TradeDesc = forms.CharField(max_length=200)
    ItemName = forms.CharField(max_length=200)
    ReturnURL = forms.URLField()
    ChoosePayment = forms.ChoiceField(choices=settings.PaymentChoices)
    ClientBackURL = forms.URLField(max_length=200)
    # ItemURL = forms.URLField(max_length=200)
    # ChooseSubPayment = forms.CharField(max_length=20, initial="")

    def clean_MerchantTradeDate(self):
        if self.cleaned_data["MerchantTradeDate"] is None:
            date = self.data["MerchantTradeDate"] = \
                datetime.datetime.utcnow()\
                .strftime(settings.DateTimeFormats[0])
            return date
        else:
            return self.cleaned_data["MerchantTradeDate"]

    def __init__(self, data, *args, **kwargs):
        if "MerchantTradeDate" in data:
            data["MerchantTradeDate"] = \
                data["MerchantTradeDate"].strftime(settings.DateTimeFormats[0])
        data["MerchantID"] = settings.MerchantID
        super(ECPayPayForm, self).__init__(data=data, *args, **kwargs)

    class Meta:
        abstract = True


class ECPayAIOLookUpForm(CMVGenMixin, forms.Form):
    MerchantID = forms.CharField(max_length=10)
    MerchantTradeNo = forms.CharField(max_length=20)
    TimeStamp = forms.IntegerField(min_value=0)

    def __init__(self, *args, **kwargs):
        super(ECPayAIOLookUpForm, self).__init__(*args, **kwargs)
        self.data["MerchantID"] = settings.MerchantID
        self.data["TimeStamp"] = \
            calendar.timegm(datetime.datetime.now().utctimetuple())
