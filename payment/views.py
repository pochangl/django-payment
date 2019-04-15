'''
Created on Jan 13, 2014

@author: pochangl
'''
import json
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import classonlymethod
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import PaymentErrorLog
from .strategies import OffsiteStrategy
from .pipes import receive_payment
from .serializers import BuySerializer


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


class BuyView(CreateAPIView):
    serializer_class = BuySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        data = serializer._validated_data
        product = data['product']
        pform = data['backend'](request=self.request).get_payment_form(order=order, product=product)
        if pform.is_valid():
            headers = self.get_success_headers(serializer.data)
            return Response({
                'data': pform.cleaned_data,
                'url': data['product_type'].get_product_url(order=order),
                'method': 'POST',
            }, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(data=pform.errors, status=status.HTTP_400_BAD_REQUEST, headers=headers)
