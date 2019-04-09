"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import RequestFactory
from django.test import Client

from payment.models import PaymentErrorLog
from django.core.urlresolvers import reverse, resolve


class PNTestBase:
    available_pns = []
    invalid_fields = []
    urlname = "pn_view"
    backend_name = None
    pn_form = None

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        PaymentErrorLog.objects.all().delete()

    def clean_invalid_inputs(self, invalid_input):
        raise NotImplemented

    def clean_valid_inputs(self, invalid_input):
        raise NotImplemented

    def assert_invalid_response(self, response):
        raise NotImplemented

    def assert_valid_response(self, response):
        raise NotImplemented

    def send_invalid_pns(self, view, inputs, *args, **kwargs):
        resolve_match = resolve(reverse('pn_view',
                                        kwargs={"backend": self.backend_name}))
        for i in range(0, len(inputs)):
            pn_input = self.clean_invalid_inputs(inputs[i])
            request = self.factory.post(
                reverse('pn_view', kwargs=resolve_match.kwargs), data=pn_input)
            response = view(request,
                            *resolve_match.args,
                            **resolve_match.kwargs)
            self.assert_invalid_response(response)

    def send_valid_pns(self, view, inputs, *args, **kwargs):
        resolve_match = \
            resolve(reverse('pn_view', kwargs={"backend": self.backend_name}))
        for i in range(0, len(inputs)):
            pn_input = self.clean_valid_inputs(inputs[i])
            form = self.pn_form(pn_input)
            self.assertTrue(form.is_valid(), form.errors)
            request = self.factory.post(reverse('pn_view',
                                                kwargs=resolve_match.kwargs),
                                        data=pn_input)
            response = view(request,
                            *resolve_match.args,
                            **resolve_match.kwargs)
            self.assert_valid_response(response)

    def test_pn(self):
        resolve_match = resolve(reverse('pn_view',
                                        kwargs={"backend": self.backend_name}))
        pn_view = resolve_match.func

        self.send_valid_pns(pn_view, self.available_pns)

        pn_input = self.available_pns[0]

        # inject invalid fields
        for field_name, value in self.invalid_fields:
            input = pn_input.copy()
            input[field_name] = value
            input = self.clean_invalid_inputs(input)
            request = self.factory.post(reverse('pn_view',
                                                kwargs=resolve_match.kwargs),
                                        data=input)
            response = pn_view(request,
                               *resolve_match.args,
                               **resolve_match.kwargs)
            self.assert_invalid_response(response)

        # for log in PaymentErrorLog.objects.all():
        #   print log.__dict__

        total_errors = PaymentErrorLog.objects.all().count()
        expected_errors = len(self.invalid_fields)

        self.assertEqual(total_errors,
                         expected_errors,
                         "total_errors: %d, expected: %d" %
                         (total_errors, expected_errors))
