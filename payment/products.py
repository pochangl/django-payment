import six
from .models import Order
from .serializers import ProductSerializer


class Product:
    product_type = None
    product = None
    backend = None
    serializer_class = None

    def __init__(self, item, backend):
        self.backend = backend
        self.item = item
        assert issubclass(self.serializer_class, ProductSerializer)

    @property
    def data(self):
        return self.serializer_class(instance=self.item).data

    @property
    def price(self):
        return data['price']

    def create_order(self, payment_method, **kwargs):
        data = self.data
        data.update(kwargs)

        order = Order.objects.create(
            backend=self.backend.backend_name,
            content_object=self.item,
            payment_method=payment_method,
            **data
        )
        order.create_order_no()
        order.save()
        return order

    @classmethod
    def get_product_url(cls, order):
        item = order.content_object
        assert isinstance(item, cls.Meta.model)
        return item.get_absolute_url()

    def is_active(self):
        return self.item.is_active
