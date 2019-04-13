import importlib
from django.apps import apps
from django.conf import settings as global_settings
from .products import Product

settings = global_settings.PAYMENT

def get_class(path):
    module_name, class_name = path.rsplit('.', 1)
    m = importlib.import_module(module_name)
    return getattr(m, class_name)

def find_products():
    products = {}
    for path in settings['PRODUCTS']:
        product = get_class(path)
        products[product.model] = product
        assert isinstance(product, Product)
    return products
