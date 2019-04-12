'''
Created on Jan 7, 2014

@author: pochangl
'''
from .backends.base import NoBackEndFound
from .backends.utils import find_backends
from django.conf import settings
import traceback
import sys

backends = find_backends()

class OffsiteStrategy(object):
    '''
        offsite strategy is a strategy for handling payment notification from third party payment service providers
    '''
    payment_backend = None
    merchant = None
    request = None

    def __init__(self, request, backend_name):
        setattr(self, "request", request)
        self._load_backend(backend_name)
        # self.merchant = merchant

    def _load_backend(self, backend_name):
        try:
            setattr(self,
                    "payment_backend",
                    backends[backend_name](self.request))
        except KeyError:
            raise NoBackEndFound(backend_name)
        return self.payment_backend

    def process_pn(self, success_callback, fail_callback):

        backend = self.payment_backend
        form = backend.get_pn_form(self.request)

        try:
            backend.transaction_is_valid(form)
        except Exception:
            return self.payment_aborted(backend,
                                        fail_callback,
                                        self.request,
                                        traceback.format_exc())

        details = backend.pn_details(form)

        if details["is_simulation"] and (not self.payment_backend.is_test):
            return backend.invalid_response()
            # pass

        try:
            return self.payment_succeed(backend, success_callback, details)
        except:
            return self.payment_aborted(backend,
                                        fail_callback,
                                        self.request,
                                        traceback.format_exc())

    def payment_succeed(self, backend, success_callback, details):
        success_callback(details)
        return backend.valid_response()

    def payment_aborted(self, backend, error_callback, request, error_message):
        error_callback(request, error_message)
        if settings.DEBUG or 'test' in sys.argv:
            return backend.invalid_response(error_message)
        else:
            return backend.invalid_response("")

    def get_payment_form(self, order, title, payment_amount, description,
                         time_created, user_return_url, payment_type):
        return self.payment_backend.get_payment_form(
            order, title, payment_amount, description, time_created,
            user_return_url, payment_type)
