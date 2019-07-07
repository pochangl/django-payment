from django.test import TestCase
from payment.tests.mixins import TestProductMixin, ProductMixin, TestPaymentSetupMixin, AccountMixin
from payment.settings import backends
from ..products import BookProduct


class TestPayment(TestPaymentSetupMixin, TestCase):
    pass


class OrderMixin(ProductMixin):
    def create_item(self):
        return super().create_item(book_title='package', is_active=True, book_price=100, book_description='desc')

    def create_order(self, owner, payment_method='ALL'):
        return super().create_order(owner=owner, payment_method=payment_method)


class TestProduct(OrderMixin, TestProductMixin, AccountMixin, TestCase):
    product_class = BookProduct
    backend = backends['ecpay_aio']

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
