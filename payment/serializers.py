
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .fields import BackendField, ProductField


class BuySerializer(serializers.Serializer):
    backend = BackendField()
    product_type = ProductField()
    product_id = serializers.IntegerField(min_value=1)
    price = serializers.IntegerField()
    payment_method = serializers.CharField()

    def validate(self, data):
        # make sure target product exists and is active
        model = data['product_type'].Meta.model
        pk = data['product_id']

        try:
            item = model.objects.get(pk=pk)
        except model.DoesNotExist:
            raise ValidationError('Product does not exist')

        product_class = data['product_type']
        product = product_class(item=item, backend=data['backend'])

        if not product.is_active:
            raise ValidationError('Product is not active')
        elif data['price'] != product.price:
            raise ValidationError('Price does not match')

        data['content_object'] = item
        data['product'] = product
        return data

    def create(self, data):
        owner = self._context['request'].user
        return data['product'].create_order(owner=owner, payment_method=data['payment_method'])
