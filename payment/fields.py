from rest_framework import serializers
from .settings import backends
from .settings import products


class BackendField(serializers.ChoiceField):
    def __init__(self, **kwargs):
        kwargs['choices'] = tuple(backends.keys())
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        try:
            return backends[data]
        except KeyError:
            raise ValidationError('No such backend %s' % data)


class ProductField(serializers.ChoiceField):
    def __init__(self, **kwargs):
        kwargs['choices'] = tuple(products.keys())
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        try:
            return products[data]
        except KeyError:
            raise ValidationError('No such product %s' % data)
