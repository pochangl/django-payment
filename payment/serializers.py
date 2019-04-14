
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from .strategies import backends
from .utils import find_products, products


class ProductSerializer(ModelSerializer):
    @property
    def data(self):
        # transform to corresponded field
        data = super().data()
        return {
            'title': data['name'],
            'payment_amount': data['price'],
            'description': data['description'],
            'content_object': self.instance
        }


class BackendField(serializers.CharField):
    def __init__(self, **kwargs):
        kwargs['choices'] = tuple(backends.keys())
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        try:
            return backends[data]
        except KeyError:
            raise ValidationError('No such backend %s' % data)


class ProductField(serializers.CharField):
    def __init__(self, **kwargs):
        kwargs['choices'] = tuple(products.keys())
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        try:
            return products[data]
        except KeyError:
            raise ValidationError('No such product %s' % data)


class BuySerializer(serializers.Serializer):
    backend = BackendField()
    payment_method = serializers.CharField()
    product_type = ProductField()
    product_id = serializers.IntegerField(min_value=1)
    price = serializers.IntegerField()

    def clean(self):
        data = self.clean()
        # make sure target product exists and is active
        model = data['product_type'].Meta.model
        pk = data['product_id']

        try:
            item = model.get(pk=pk)
        except model.DoesNotExist:
            raise ValidationError('Product does not exist')

        product_class = products[item]
        product = product_class(product=item, backend=data['backend'])

        if not product.is_active:
            raise ValidationError('Product is not active')
        elif data['price'] != product.price:
            raise ValidationError('Price does not match')

        data['content_object'] = item
        data['product'] = product
        return data

    def create(self, data):
        return data['product'].create_order(payment_method=data['payment_method'])
