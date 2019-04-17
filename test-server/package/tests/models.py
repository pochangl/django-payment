import re
from django.test import TestCase
from payment.models import Order

class TestOrder(TestCase):
    def test_order(self):
        order = Order()
        order.id = 1
        order.create_order_no()
        self.assertTrue(re.match(r'^\d+T\d+$', order.order_no))
