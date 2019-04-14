#!/usr/bin/python
# -*- coding: UTF-8 -*-


"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase
from payment.tests import PNTestBase
from payment.backends.ecpay.settings import settings
from payment.backends.ecpay.utils import get_CheckMacValue
from payment.backends.ecpay import forms
from payment.models import Order


available_ecpay_pns = [
    {
        "MerchantID": settings.MerchantID,
        "MerchantTradeNo": u"15550464430000024",
        "RtnCode": u"1",
        "RtnMsg": u"",
        "TradeNo": u"1904121320432293",
        "TradeAmt": u"700",
        "PaymentDate": u"2019/04/12 13:21:22",
        "PaymentType": u"Credit_CreditCard",
        "PaymentTypeChargeFee": u"1.00",
        "TradeDate": u"2019/04/12 13:21:03",
        "SimulatePaid": u"0",
    }
]

invalid_ecpay_fields = [
    ("MerchantID", "%s%s" % (settings.MerchantID, "0")),
    ("MerchantID", settings.MerchantID[0:len(settings.MerchantID)-1]),
    ("MerchantID", "%s%s" %
     (settings.MerchantID[0:len(settings.MerchantID)-1], '0')),
    ("MerchantTradeNo", "meowmeowmeo"),
    ("RtnCode", "0"),
    ("RtnCode", "2"),
    # ("RtnMsg", "喵1"),
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


class ECPayTestBase(PNTestBase, TestCase):
    available_pns = available_ecpay_pns
    invalid_fields = invalid_ecpay_fields
    backend_name = "ecpay_aio"
    pn_form = forms.ECPayAIOPNForm

    def create_order(self, **kwargs):
        return super().create_order(
            backend=self.backend_name,
            product_class='product_one',
            **kwargs
        )

    def setUp(self):
        super().setUp()
        for pns in self.available_pns:
            order = self.create_order(
                order_no=pns['MerchantTradeNo'],
                payment_amount=pns['TradeAmt'],
            )
            model_class = order.content_type.model_class()
            pk = order.object_id
            model_class.objects.create(pk=pk, name=pk, description=pk, price=pk)

    def clean_invalid_inputs(self, invalid_input):
        invalid_input["CheckMacValue"] = get_CheckMacValue(invalid_input)
        return invalid_input

    def clean_valid_inputs(self, valid_input):
        valid_input["CheckMacValue"] = get_CheckMacValue(valid_input)
        return valid_input

    def assert_invalid_response(self, response):
        self.assertEqual(response.content[0:2], b'0|', response.content)

    def assert_valid_response(self, response):
        self.assertEqual(response.content, b'1|OK', response.content)

    def test_pn(self):
        order = Order.objects.get()
        self.assertEqual(order.additional_fee, 0)
        self.assertIsNone(order.payment_received)
        super().test_pn()

        order = Order.objects.get()
        self.assertEqual(order.additional_fee, 1.00)
        self.assertIsNotNone(order.payment_received)
