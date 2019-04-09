'''
Created on Jan 13, 2014

@author: pochangl
'''


from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import classonlymethod
from payment.strategies import OffsiteStrategy
from payment.models import PaymentErrorLog
from payment import receive_payment


class PNView(View):
    class Meta:
        http_methods = ['post']

    @classonlymethod
    def as_view(cls, **initkwargs):
        return csrf_exempt(super(PNView, cls).as_view(**initkwargs))

    def post(self, request, *args, **kwargs):
        backend_name = kwargs["backend"]
        strategy = OffsiteStrategy(self.request, backend_name)
        return strategy.process_pn(self.payment_succeed, self.payment_aborted)

    def payment_succeed(self, details):
        receive_payment(details)

    def payment_aborted(self, request, error_message):
        log = PaymentErrorLog()
        log.load_data(request=request, error_message=error_message)
        log.save()
