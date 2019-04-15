from rest_framework import serializers
from payment.products import ProductSerializer
from .models import ProductModel


class ProductModelSerializer(ProductSerializer):
    name = serializers.CharField()
    price = serializers.IntegerField()
    description = serializers.CharField()

    class Meta:
        model = ProductModel
        fields = ('name', 'price', 'description')
