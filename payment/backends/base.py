'''
Created on Jan 7, 2014

@author: pochangl
'''
import datetime
import inspect
from django.core.urlresolvers import reverse


class BackEndError(Exception):
    pass


class NoBackEndFound(BackEndError):
    pass


class InvalidInput(BackEndError):
    pass


class InvalidPayment(BackEndError):
    pass


class UnknownBackEndError(BackEndError):
    pass


class InvalidForm(BackEndError):
    pass


class ServerError(BackEndError):
    pass


class PaymentBackend(object):
    # receive payment notification form
    pn_form_class = None
    payment_form_class = None
    backend_name = None

    def __init__(self, request):
        setattr(self, "request", request)

    def get_pn_form(self, request):
        if self.pn_form_class is None:
            raise InvalidForm("pn_form undefined")
        return self.pn_form_class(request.POST, request.FILES)

    def pn_url(self):
        return self.request.build_absolute_uri(
            reverse('pn', kwargs={"backend": self.backend_name}))

    def pn_details(self, form):
        return {
            "backend": self.backend_name,
            "payment_received": datetime.datetime.utcnow(), }

    def transaction_is_valid(self, form):
        # look up transaction from the 3rd party payment server
        raise NotImplemented

    def input_is_valid(self, form):
        if form.is_valid():
            return True
        else:
            raise InvalidInput(
                "input is invalid, module%s: line:%s reason:%s" %
                (__name__,
                 inspect.currentframe().f_back.f_lineno,
                 str(form.errors)))

    def get_payment_form(self, order, product):
        func = getattr(self, "get_%s_payment_form" % order.payment_method)
        return func(order=order, product=product)

    def invalid_response(self, error_message):
        raise NotImplemented

    def valid_response(self):
        raise NotImplemented
