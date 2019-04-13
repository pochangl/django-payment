'''
Created on Jan 16, 2014

@author: pochangl
'''
from django.conf import settings as global_settings
from .base import PaymentBackend
from ..utils import get_class

settings = global_settings.PAYMENT

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
