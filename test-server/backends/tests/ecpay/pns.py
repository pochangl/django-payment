#!/usr/bin/python
# -*- coding: UTF-8 -*-


"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase
from package.tests import PNTestBase
from payment.backends.ecpay.settings import settings
from payment.backends.ecpay.utils import get_CheckMacValue
from payment.backends.ecpay import forms
from payment.models import Order, PaymentErrorLog
from product.models import Book
from django.urls import resolve, reverse

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
    # ("RtnMsg", "喵1"),
    # ("TradeNo", "140110030454740700000"),
    # ("TradeNo", "14011003045474070000"),
    # ("TradeNo", "1401100304547407"),
    # ("TradeNo", "140110030454740a"),
    ("TradeAmt", "194"),
    # ("PaymentDate","2014/01/10 03:06:42"),
    ("PaymentDate", "2014/01/10 03:06:042"),
    ("PaymentDate", "2014/01010 03:06:4a"),
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
            product_class='book',
            **kwargs
        )

    def create_order_from_pn(self, pn):
        order = self.create_order(
            order_no=pn['MerchantTradeNo'],
            payment_amount=pn['TradeAmt'],
        )
        model_class = order.content_type.model_class()
        pk = order.object_id
        model_class.objects.create(pk=pk, book_title=pk, book_description=pk, book_price=order.payment_amount)
        return order

    def create_item(self):
        return Book.objects.create(pk=1, )

    def setUp(self):
        super().setUp()
        for pn in self.available_pns:
            self.create_order_from_pn(pn)

    def clean_invalid_inputs(self, invalid_input):
        invalid_input["CheckMacValue"] = get_CheckMacValue(invalid_input)
        return invalid_input

    def clean_valid_inputs(self, valid_input):
        valid_input["CheckMacValue"] = get_CheckMacValue(valid_input)
        return valid_input

    def assert_invalid_response(self, response):
        self.assertEqual(response.content, b'0|error', response.content)

    def assert_valid_response(self, response):
        self.assertEqual(response.content, b'1|OK', response.content)

    @property
    def pn_view(self):
        resolve_match = resolve(reverse('pn', kwargs={"backend": self.backend_name}))
        return resolve_match.func

    def test_pn(self):
        order = Order.objects.get()
        self.assertEqual(order.additional_fee, 0)
        self.assertIsNone(order.payment_received)
        super().test_pn()

        order = Order.objects.get()
        self.assertEqual(order.additional_fee, 1.00)
        self.assertIsNotNone(order.payment_received)

    def test_product_apply(self):
        order = Order.objects.get()
        product = Book.objects.get()

        self.assertEqual(product.buyers.count(), 0)
        self.assertEqual(product.count, 0)
        self.send_valid_pns(self.pn_view, self.available_pns)

        product = Book.objects.get()
        self.assertEqual(product.buyers.get(), order.owner)
        self.assertEqual(product.count, 1)

    def test_repeat_pn(self):
        order = Order.objects.get()
        product = Book.objects.get()
        self.send_valid_pns(self.pn_view, self.available_pns)
        self.send_valid_pns(self.pn_view, self.available_pns)

        product = Book.objects.get()
        self.assertEqual(product.buyers.get(), order.owner)
        self.assertEqual(product.count, 1)

    def test_pipe_apply(self):
        order = Order.objects.get()
        field_names = ['payment_received', 'additional_fee', 'handled']
        # Falsy
        for field_name in field_names:
            self.assertFalse(getattr(order, field_name))
        self.send_valid_pns(self.pn_view, self.available_pns)

        order = Order.objects.get()
        for field_name in field_names:
            self.assertTrue(getattr(order, field_name))

    def test_transaction_cancel(self):
        '''
            must return 0|OK
        '''
        self.assertEqual(PaymentErrorLog.objects.count(), 0)

        pn = {
            'CustomField1':'',
            'CustomField2':'',
            'CustomField3':'',
            'CustomField4':'',
            'MerchantID':'2000132',
            'MerchantTradeNo':'1555489476T2',
            'PaymentDate':'0001/01/01 00:00:00',
            'PaymentType':'Credit_CreditCard',
            'PaymentTypeChargeFee':'1',
            'RtnCode':'10100058',
            'RtnMsg':'付款失敗',
            'SimulatePaid':'0',
            'StoreID':'',
            'TradeAmt':'1688',
            'TradeDate':'2019/04/17 16:24:36',
            'TradeNo':'1904171624367334',
            'CheckMacValue':'C469E19ED4B9BC2DAE82A95275A9F464228A44277D9F08806519A410CB16F5CF'
        }

        self.send_valid_pns(self.pn_view, [pn], form_check=False)

        self.assertEqual(PaymentErrorLog.objects.count(), 1)

    def test_simulated_success(self):
        # simulation should not apply and should not return fail disregard it's actual state
        pn = {
            "PaymentType":"BARCODE_BARCODE",
            "RtnMsg":"付款成功",
            "SimulatePaid":"1",
            "CustomField2":"",
            "PaymentDate":"2019/04/17 20:12:21",
            "TradeNo":"1904171757027487",
            "TradeAmt":"999",
            "MerchantID":"2000132",
            "StoreID":"",
            "CustomField3":"",
            "MerchantTradeNo":"1555495021T6",
            "CustomField4":"",
            "CheckMacValue":"E1797F7FF339A78BC9B1076CF158B95083B0C7205828F4F57D5BF88765FC4AFB",
            "TradeDate":"2019/04/17 17:57:02",
            "CustomField1":"",
            "RtnCode":"1",
            "PaymentTypeChargeFee":"15"
        }

        Order.objects.all().delete()
        Book.objects.all().delete()
        self.assertEqual(PaymentErrorLog.objects.count(), 0)
        order = self.create_order_from_pn(pn)
        self.assertEqual(order.content_object.buyers.count(), 0)
        self.send_valid_pns(self.pn_view, [pn], form_check=False)

        self.assertEqual(PaymentErrorLog.objects.count(), 0)
        self.assertEqual(order.content_object.buyers.count(), 0)
