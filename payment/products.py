import six
from django.utils.functional import cached_property
from rest_framework import serializers
from .models import Order


class ProductSerializer(serializers.ModelSerializer):
    @property
    def data(self):
        # transform to corresponded field
        data = super().data
        return {
            'title': data['name'],
            'payment_amount': data['price'],
            'description': data['description'],
            'content_object': self.instance
        }


class Product:
    product_type = None
    product = None
    backend = None
    serializer_class = None

    def __init__(self, item, backend):
        self.backend = backend
        self.item = item
        assert issubclass(self.serializer_class, ProductSerializer)

    @cached_property
    def data(self):
        return self.serializer_class(instance=self.item).data

    @property
    def price(self):
        return self.data['payment_amount']

    def create_order(self, owner, payment_method, **kwargs):
        data = self.data
        data.update(kwargs)

        order = Order.objects.create(
            owner=owner,
            backend=self.backend.backend_name,
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
