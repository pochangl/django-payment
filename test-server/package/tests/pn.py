"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse, resolve
from payment.models import PaymentErrorLog, Order

User = get_user_model()

class PNTestBase:
    available_pns = []
    invalid_fields = []
    urlname = "pn"
    backend_name = None
    pn_form = None

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        PaymentErrorLog.objects.all().delete()

    _user_count = 0
    def create_user(self, username=None, **kwargs):
        '''
            create a user account for test
        '''
        self._user_count += 1
        if username is None:
            username = 'user_%d' % self._user_count
        data = {
            'password': kwargs.get('password', 'pasword' + username),
            'username': username,
            'email': kwargs.get('email', '%s@example.com' % username),
            'first_name': username + 'fn',
            'last_name': username + 'ln',
        }
        data.update(kwargs)
        user = User.objects.create_user(**data)
        return user

    def create_order(self, **kwargs):
        if 'owner' not in kwargs:
            kwargs['owner'] = self.create_user()
        kwargs['content_type'] = kwargs.get('content_type', ContentType.objects.get(app_label='product', model='ProductModel'))
        kwargs['object_id'] = kwargs.get('object_id', 1)
        return Order.objects.create(**kwargs)

    def clean_invalid_inputs(self, invalid_input):
        raise NotImplemented

    def clean_valid_inputs(self, invalid_input):
        raise NotImplemented

    def assert_invalid_response(self, response):
        raise NotImplemented

    def assert_valid_response(self, response):
        raise NotImplemented

    def send_invalid_pns(self, view, inputs, *args, **kwargs):
        resolve_match = resolve(reverse('pn',
                                        kwargs={"backend": self.backend_name}))
        for i in range(0, len(inputs)):
            pn_input = self.clean_invalid_inputs(inputs[i])
            request = self.factory.post(
                reverse('pn', kwargs=resolve_match.kwargs), data=pn_input)
            response = view(request,
                            *resolve_match.args,
                            **resolve_match.kwargs)
            self.assert_invalid_response(response)

    def send_valid_pns(self, view, inputs, args=(), kwargs={}, form_check=True):
        resolve_match = \
            resolve(reverse('pn', kwargs={"backend": self.backend_name}))
        for i in range(0, len(inputs)):
            pn_input = self.clean_valid_inputs(inputs[i])
            if form_check:
                form = self.pn_form(pn_input)
                self.assertTrue(form.is_valid(), form.errors)
            request = self.factory.post(
                reverse(
                    'pn',
                    kwargs=resolve_match.kwargs
                ),
                data=pn_input
            )
            response = view(
                request,
                *resolve_match.args,
                **resolve_match.kwargs
            )
            self.assert_valid_response(response)

    def test_pn(self):
        resolve_match = resolve(reverse('pn', kwargs={"backend": self.backend_name}))
        pn_view = resolve_match.func

        self.send_valid_pns(pn_view, self.available_pns)

        pn_input = self.available_pns[0]

        # inject invalid fields
        for field_name, value in self.invalid_fields:
            input = pn_input.copy()
            input[field_name] = value
            input = self.clean_invalid_inputs(input)
            request = self.factory.post(
                reverse(
                    'pn',
                    kwargs=resolve_match.kwargs
                ),
                data=input
            )
            response = pn_view(
                request,
                *resolve_match.args,
                **resolve_match.kwargs
            )
            self.assert_invalid_response(response)

        # for log in PaymentErrorLog.objects.all():
        #   print log.__dict__

        total_errors = PaymentErrorLog.objects.all().count()
        expected_errors = len(self.invalid_fields)

        self.assertEqual(total_errors,
                         expected_errors,
                         "total_errors: %d, expected: %d" %
                         (total_errors, expected_errors))

    def test_csrf_example(self):
        pass
