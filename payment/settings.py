from django.apps import apps
from django.conf import settings as global_settings
from .backends.utils import find_backends
from .utils import get_class
from .products import Product

__all__ = ['products', 'backends']

settings = global_settings.PAYMENT
backends = find_backends()

def find_products():
    products = {}
    for path in settings['PRODUCTS']:
        product = get_class(path)
        assert product.name not in products
        products[product.name] = product
        assert issubclass(product, Product), '%s is not Product' % path
    return products

products = find_products()
