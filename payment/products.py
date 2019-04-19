import six
from django.utils.functional import cached_property
from django.urls import reverse
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
    item = None
    backend = None
    serializer_class = None
    return_view_name = None
    view_name = None

    def __init__(self, item, backend, request=None):
        self.backend = backend
        self.item = item
        self.request = request
        assert issubclass(self.serializer_class, ProductSerializer)

    @cached_property
    def data(self):
        return self.serializer_class(instance=self.item).data

    def is_active(self):
        return self.price > 0

    @property
    def price(self):
        return self.data['payment_amount']

    @property
    def url(self):
        # product info url
        return self.request.build_absolute_uri(reverse(self.view_name, kwargs=self.get_url_kwargs()))

    def get_return_url(self, order):
        # where user should return after done with purchasing
        return self.request.build_absolute_uri(reverse(self.return_view_name, kwargs=self.get_return_url_kwargs(order)))

    def get_url_kwargs(self):
        return {
            'pk': self.item.pk
        }

    def get_return_url_kwargs(self, order):
        return {
            'pk': order.pk
        }

    def create_order(self, owner, payment_method, **kwargs):
        data = self.data
        data.update(kwargs)

        order = Order.objects.create(
            owner=owner,
            backend=self.backend.backend_name,
            payment_method=payment_method,
            product_class=self.name,
            **data
        )
        order.create_order_no()
        order.save()
        return order
