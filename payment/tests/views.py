from django.test import TestCase
from rest_framework import status
from product.models import ProductModel
from ..models import Order
from .mixins import APIMixin


class BuyViewTest(APIMixin, TestCase):
    view_name = 'buy'

    _item_count = 0
    def create_item(self):
        self._item_count += 1
        cnt = self._item_count

        return ProductModel.objects.create(
            price = cnt * 100,
            name = 'product %d' % cnt,
            description = 'product desc %d' % cnt,
        )

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

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get()

        # Truthy
        self.assertTrue(order.order_no)

        # Falsy
        fields = ('payment_received', 'handled', 'additional_fee')
        for field in fields:
            self.assertFalse(getattr[field])

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
