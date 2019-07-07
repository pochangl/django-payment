from rest_framework import serializers
from payment.products import ProductSerializer
from .models import Book


class BookProductSerializer(ProductSerializer):
    name = serializers.CharField(source='book_title')
    price = serializers.IntegerField(source='book_price')
    description = serializers.CharField(source='book_description')

    class Meta:
        model = Book
        fields = ('name', 'price', 'description')
