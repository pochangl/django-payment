'''
Created on Jan 13, 2014

@author: pochangl
'''
import json
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import classonlymethod
from django.views.generic import View, FormView
from django.views.decorators.csrf import csrf_exempt
from .models import PaymentErrorLog
from .strategies import OffsiteStrategy
from .pipes import receive_payment
from .forms import BuyForm

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


class BuyView(FormView):
    form_class = BuyForm

    def get_form_kwargs(self):
        return self.kwargs

    def form_valid(self, form):
        instance = data['content_object']
        backend = data['backend']
        data = form.cleaned_data
        order = Order.objects.create(
            backend=backend,
            content_object=instance,
        )
        order.clean()
        order.save()
        pform = backend.get_payment_form(order=order, payment_type=data['payment_type'])
        if not pform.is_valid():
            return self.form_invalid(form)


        return HttpResponse(json.dumps({
            'url': pform.submit_url,
            'method': 'post',
            'data': pform.cleaned_data
        }), status=200, content_type='application/json')

    def form_invalid(self, form):
        return HttpResponse(status=404)
