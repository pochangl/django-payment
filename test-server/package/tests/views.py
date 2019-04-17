from django.test import TestCase
from django.utils.timezone import now
from rest_framework import status
from product.models import ProductModel
from payment.backends.ecpay.settings import settings
from payment.backends.ecpay.utils import format_time
from payment.tests.mixins import APIMixin
from payment.models import Order


class BuyViewTest(APIMixin, TestCase):
    view_name = 'buy'

    _item_count = 0
    maxDiff = 2000

    def create_item(self, **kwargs):
        self._item_count += 1
        cnt = self._item_count
        data = {
            'price': cnt * 100,
            'name': 'product %d' % cnt,
            'description': 'product desc %d' % cnt,
            'is_active': True
        }
        data.update(kwargs)

        return ProductModel.objects.create(**data)

    def setUp(self):
        item = self.item = self.create_item()
        self.data = {
            'backend': 'ecpay_aio',
            'product_type': 'product_one',
            'product_id': item.pk,
            'price': item.price,
            'payment_method': 'ALL'
        }

    def test_buy(self):
        self.assertEqual(Order.objects.count(), 0)
        item = self.item
        data = self.data

        user = self.create_user()
        response = self.api_create(user=user, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        # check order object
        order = Order.objects.get()

        # Truthy
        self.assertTrue(order.order_no)

        # Falsy
        fields = ('payment_received', 'handled', 'additional_fee')
        for field in fields:
            self.assertFalse(getattr(order, field))

        # compare order and data
        pairs = (
            ('backend', 'backend'),
            ('product_class', 'product_type'),
            ('object_id', 'product_id'),
            ('payment_amount', 'price'),
            ('payment_method', 'payment_method'),
        )
        for attr, name in pairs:
            self.assertEqual(getattr(order, attr), data[name])

        # compares order and item
        pairs = (
            ('title', 'name'),
            ('payment_amount', 'price'),
            ('description', 'description'),
        )
        for oattr, iattr in pairs:
            self.assertEqual(getattr(order, oattr), getattr(item, iattr))

        self.assertEqual(order.content_object, item)

        # check return value
        content = self.load_json(response.content)
        self.assertTrue(content['data']['CheckMacValue'])
        content['data'].pop('CheckMacValue')
        self.assertEqual(content, {
            'method': 'POST',
            'url': settings.AioCheckOut_URL,
            'data': {
                'ChoosePayment': 'ALL',
                'MerchantID': settings.MerchantID,
                'PaymentType': 'aio',
                'ExpireDate': 7,
                'MerchantTradeNo': order.order_no,
                'ItemName': item.name,
                'TradeDesc': item.description,
                'TotalAmount': item.price,
                'MerchantTradeDate': format_time(order.time_created),
                'ClientBackURL': 'http://example.com/return/%d' % order.pk,
                'ItemURL': 'http://example.com/info/%d' % item.pk,
                'ReturnURL': 'http://example.com/pn/pn/ecpay_aio',
                'EncryptType': 1,
            }
        })

    def test_price_zero(self):
        item = self.item
        price = item.price
        item.price = 0
        item.save()
        data = self.data.copy()
        data['price'] = 0
        user = self.create_user()

        # should reject
        response = self.api_create(user=user, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)
        self.assertTrue(b'Product is not active' in response.content)

        data['price'] = item.price = price
        item.save()


        # should accept
        response = self.api_create(user=user, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

    def test_inactive(self):
        item = self.item
        item.is_active = False
        item.save()
        data = self.data

        user = self.create_user()

        # should reject
        response = self.api_create(user=user, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)
        self.assertTrue(b'Product is not active' in response.content)

        item.is_active = True
        item.save()

        # should accept
        response = self.api_create(user=user, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

    def test_price_mismatch(self):
        user = self.create_user()
        data = self.data
        item = self.item
        item.price += 1
        item.save()

        # should reject
        response = self.api_create(user=user, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)
        self.assertTrue(b'Price mismatch' in response.content, response.content)
