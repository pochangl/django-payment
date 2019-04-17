from django.test import TestCase
from payment.tests.mixins import TestProductMixin, TestPaymentSetupMixin, AccountMixin
from payment.settings import backends
from .products import ProductOne


class TestPayment(TestPaymentSetupMixin, TestCase):
    pass


class TestProduct(AccountMixin, TestProductMixin, TestCase):
    product_class = ProductOne
    backend = backends['ecpay_aio']

    def create_item(self):
        return super().create_item(name='package', is_active=True, price=100, description='desc')

    def create_order(self, owner, payment_method='ALL'):
        return super().create_order(owner=owner, payment_method=payment_method)

    def test_apply(self):
        owner = self.create_user()
        order = self.create_order(owner=owner)
        item = order.content_object
        self.assertFalse(item.buyers.count())

        self.apply(order)

        # flush order
        order = type(order).objects.get(pk=order.pk)
        item = order.content_object

        self.assertEqual(item.buyers.get(), owner)
