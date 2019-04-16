from payment.products import Product
from .serializers import ProductModelSerializer
from .models import ProductModel


class ProductOne(Product):
    name = 'product_one'
    serializer_class = ProductModelSerializer
    return_view_name = 'return_page'
    view_name = 'product_info'

    class Meta:
        model = ProductModel

    def apply(self, user):
        self.item.buyers.add(user)

    @property
    def is_active(self):
        return super().is_active() and self.item.is_active
