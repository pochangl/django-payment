'''
Created on Jan 16, 2014

@author: pochangl
'''
from django.conf import settings
from payment.backends.base import PaymentBackend
import importlib


def find_backends():
    backends = {}
    for backend in settings.PAYMENT_BACKENDS:
        module_name, class_name = backend.rsplit('.', 1)
        m = importlib.import_module(module_name)
        backend_class = getattr(m, class_name)
        if issubclass(backend_class, PaymentBackend):
            backend_name = backend_class.backend_name
            if backend_name not in backends:
                backends[backend_class.backend_name] = backend_class
    return backends


def backend_choices():
    # this util is for generating form chocies
    backend_choices = ()
    for backend in settings.PAYMENT_BACKENDS:
        module_name, class_name = backend.rsplit('.', 1)
        m = importlib.import_module(module_name)
        backend_class = getattr(m, class_name)
        if issubclass(backend_class, PaymentBackend):
            backend_name = backend_class.backend_name
            backend_choices = backend_choices + ((backend_name, backend_name),)
    return backend_choices
