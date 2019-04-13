import six
from .models import Order
from .serializers import ProductSerializer


class Product:
    product_type = None
    product = None
    backend = None
    serializer_class = None

    def __init__(self, product, backend):
        self.backend = backend
        self.product = product
        assert isinstance(self.serializer_class, ProductSerializer)

    def create_order(self):
        data = self.serializer_class(instance=self.product)

        order = Order.objects.create(
            backend=self.backend.backend_name,
            **data
        )
        order.create_order_no()
        order.save()
        return order

    def get_product_url(self, order):
        product = order.content_object
        assert product == self.product
        return product.get_absolute_url()

    def is_active(self):
        return self.product.is_active
