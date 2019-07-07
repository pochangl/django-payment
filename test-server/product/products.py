from payment.products import Product
from .serializers import BookProductSerializer
from .models import Book, BookOwner


__all__ = ['BookProduct']


class BookProduct(Product):
    name = 'book'
    serializer_class = BookProductSerializer
    return_view_name = 'return_page'
    view_name = 'product_info'

    class Meta:
        model = Book

    def apply(self, user, product):
        BookOwner.objects.create(user=user, book=product)

    def is_active(self):
        return super().is_active() and self.item.is_active
