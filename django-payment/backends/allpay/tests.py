#!/usr/bin/python
# -*- coding: UTF-8 -*-


"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from payment.tests import PNTestBase
from payment.backends.allpay.settings import settings
from payment.backends.allpay.utils import get_CheckMacValue
from payment.backends.allpay import forms


available_allpay_pns = [
    {
        "MerchantID": settings.MerchantID,
        "MerchantTradeNo": u"meowmeowmeow",
        "RtnCode": u"1",
        "RtnMsg": u"喵1",
        "TradeNo": u"1401100304547408",
        "TradeAmt": u"193",
        "PaymentDate": u"2014/01/10 03:06:41",
        "PaymentType": u"Credit_CreditCard",
        "PaymentTypeChargeFee": u"0",
        "TradeDate": u"2014/01/10 03:04:54",
        "SimulatePaid": u"0",
    },
    {
        "MerchantID": settings.MerchantID,
        "MerchantTradeNo": u"meowmeowmeow2",
        "RtnCode": u"1",
        "RtnMsg": u"喵二",
        "TradeNo": u"1401131630470735",
        "TradeAmt": u"199",
        "PaymentDate": u"2014/01/13 16:30:47",
        "PaymentType": u"Credit_CreditCard",
        "PaymentTypeChargeFee": u"0",
        "TradeDate": u"2014/01/13 16:30:47",
        "SimulatePaid": u"0",
    },
    {
        "MerchantID": settings.MerchantID,
        "MerchantTradeNo": u"kjhn2398kd",
        "RtnCode": u"1",
        "RtnMsg": u"第三",
        "TradeNo": u"1401100147537403",
        "TradeAmt": u"123",
        "PaymentDate": u"2014/01/10 01:51:25",
        "PaymentType": u"Credit_CreditCard",
        "PaymentTypeChargeFee": u"0",
        "TradeDate": u"2014/01/10 01:47:53",
        "SimulatePaid": u"0",
    },
    {
        "MerchantID": settings.MerchantID,
        "MerchantTradeNo": u"kjhn2398kc",
        "RtnCode": u"1",
        "RtnMsg": u"第四",
        "TradeNo": u"1401100204396998",
        "TradeAmt": u"123",
        "PaymentDate": u"2014/01/10 02:06:20",
        "PaymentType": u"Credit_CreditCard",
        "PaymentTypeChargeFee": u"0",
        "TradeDate": u"2014/01/10 02:04:39",
        "SimulatePaid": u"0",
    }
    ]

invalid_allpay_fields = [
    ("MerchantID", "%s%s" % (settings.MerchantID, "0")),
    ("MerchantID", settings.MerchantID[0:len(settings.MerchantID)-1]),
    ("MerchantID", "%s%s" %
     (settings.MerchantID[0:len(settings.MerchantID)-1], '0')),
    ("MerchantTradeNo", "meowmeowmeo"),
    ("RtnCode", "0"),
    ("RtnCode", "2"),
    ("RtnMsg", ""),
    # ("TradeNo", "140110030454740700000"),
    # ("TradeNo", "14011003045474070000"),
    # ("TradeNo", "1401100304547407"),
    # ("TradeNo", "140110030454740a"),
    ("TradeAmt", "194"),
    # ("PaymentDate","2014/01/10 03:06:42"),
    ("PaymentDate", "2014/01/10 03:06:042"),
    ("PaymentDate", "2014/01010 03:06:4a"),
    ("PaymentType", "Credi"),
    ("PaymentType", "aCVS_"),
    # ("PaymentTypeChargeFee","1"),
    ("PaymentTypeChargeFee", "a"),
    # ("TradeDate","2014/01/10 03:04:53"),
    ("TradeDate", "2014/01/10 03:04:054"),
    ("TradeDate", "2014/01/10 03:04:5a"),
    # ("TradeDate","2014/01;10 03:04:54"),
    # ("SimulatePaid", "0")
    ]


class AllPayTestBase(PNTestBase):
    available_pns = available_allpay_pns
    invalid_fields = invalid_allpay_fields
    backend_name = "allpay_aio"
    pn_form = forms.AllPayAIOPNForm

    def clean_invalid_inputs(self, invalid_input):
        invalid_input["CheckMacValue"] = get_CheckMacValue(invalid_input)
        return invalid_input

    def clean_valid_inputs(self, valid_input):
        valid_input["CheckMacValue"] = get_CheckMacValue(valid_input)
        return valid_input

    def assert_invalid_response(self, response):
        self.assertEqual(response.content[0:2], "0|", response.content)

    def assert_valid_response(self, response):
        self.assertEqual(response.content, "1|OK", response.content)
