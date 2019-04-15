from payment.products import Product
from .serializers import ProductModelSerializer
from .models import ProductModel


class ProductOne(Product):
    name = 'product_one'
    serializer_class = ProductModelSerializer

    class Meta:
        model = ProductModel

    def apply(self, user):
        self.item.buyers.add(user)
