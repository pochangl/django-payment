'''
Created on Jan 16, 2014

@author: pochangl
'''
import importlib
from django.apps import apps
from django.conf import settings as global_settings
from .base import PaymentBackend

settings = global_settings.PAYMENT

def get_class(path):
    module_name, class_name = path.rsplit('.', 1)
    m = importlib.import_module(module_name)
    return getattr(m, class_name)

def get_model(name):
    label, name = name.split('.', 1)
    return apps.get_model(app_label=label, model_name=name)

def find_backends():
    backends = {}
    for backend in settings['PAYMENT_BACKENDS']:
        backend_class = get_class(backend)
        if issubclass(backend_class, PaymentBackend):
            backend_name = backend_class.backend_name
            if backend_name not in backends:
                backends[backend_class.backend_name] = backend_class
    return backends

def backend_choices():
    # this util is for generating form chocies
    backend_choices = ()
    for backend in settings['PAYMENT_BACKENDS']:
        backend_class = get_class(backend)
        if issubclass(backend_class, PaymentBackend):
            backend_name = backend_class.backend_name
            backend_choices = backend_choices + ((backend_name, backend_name),)
    return backend_choices


def find_products():
    products = {}
    for path in settings['PRODUCTS']:
        product = get_model(path)
        products[path] = product
    return products
