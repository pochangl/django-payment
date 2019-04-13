from payment.products import BaseProduct
from .serializers import ProductModelSerializer


class Product(BaseProduct):
    serializer_class = ProductModelSerializer
