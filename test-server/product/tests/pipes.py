import datetime
from django.test import TestCase
from payment.tests.mixins import AccountMixin
from payment.pipes import receive_payment
from payment.settings import backends
from payment.models import Order
from .products import OrderMixin
from ..products import ProductOne


class TestPipe(AccountMixin, OrderMixin, TestCase):
    product_class = ProductOne
    backend = backends['ecpay_aio']

    def setUp(self):
        order = self.create_order()
        self.detail = {
            'order_no': order.order_no,
            'payment_amount': order.payment_amount,
            'additional_fee': order.additional_fee,
        }

    def create_order(self):
        return super().create_order(owner=self.create_user(), payment_method='ALL')

    def get_order(self):
        return Order.objects.get(order_no=self.detail['order_no'])

    def test_update(self):
        order = self.get_order()
        self.assertIsNone(order.payment_received)

        receive_payment(self.detail)

        order = self.get_order()
        self.assertIsInstance(order.payment_received, datetime.datetime)


    def test_apply(self):
        order = self.get_order()
        item = order.content_object
        self.assertEqual(item.buyers.count(), 0)

        receive_payment(self.detail)

        item = self.get_order().content_object
        self.assertEqual(item.buyers.get(), order.owner)

    def test_extra(self):
        item = self.get_order().content_object

        self.assertEqual(item.count, 0)

        receive_payment(self.detail)

        item = self.get_order().content_object
        self.assertEqual(item.count, 1)
