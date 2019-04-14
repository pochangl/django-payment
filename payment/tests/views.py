from django.test import TestCase
from product.models import ProductModel


class BuyViewTest(TestCase):
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

    def test_buy(self):
        user = self.create_user()
        item = self.create_product()
        data = {
            'backend': 'ecpay_aio',
            'product': 'product_one',
            'id': item.pk
        }
        product = Product.objects.create(pk=1)
        self.api_create(user=user, data=data)
