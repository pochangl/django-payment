import copy
import json
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db.models import Model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from ..settings import products, backends
from ..pipes import apply_order, payment_pipes

User = get_user_model()
HOST = 'example.com'

class AccountMixin:
    def get_password(self, username):
        '''
            rebuild password from username
        '''
        return '%s_psw' % username

    _user_count = 0
    def create_user(self, username=None, **old_kwargs):
        '''
            create a user account for test
        '''
        if username is None:
            username = 'user_%d' % self._user_count
        self._user_count += 1
        kwargs = copy.deepcopy(old_kwargs)
        kwargs.update({
            'password': kwargs.get('password', self.get_password(username)),
            'username': username,
            'email': kwargs.get('email', '%s@example.com' % username),
            'first_name': username + 'fn',
            'last_name': username + 'ln',
        })
        user = User.objects.create_user(**kwargs)
        Token.objects.create(user=user)
        return user

    def get_anonymous(self):
        return AnonymousUser()

class ClientMixin(AccountMixin):
    def reverse(self, *args, **kwargs):
        return reverse(*args, **kwargs)

    def clean_data(self, d):
        if isinstance(d, list):
            data = []
            for value in d:
                if isinstance(value, Model):
                    data.append(value.pk)
                else:
                    data.append(value)
        elif isinstance(d, dict):
            data = {}
            for key, value in d.items():
                if isinstance(value, Model):
                    data[key] = value.id
                else:
                    data[key] = value
        return data

    def get_logged_in_client(self, user=None):
        '''
            return a logged in client
            user model can be found in client.user
        '''
        client = self.client_class(HTTP_HOST=HOST)
        if user is None:
            user = self.create_user()

        if not user.is_anonymous():
            client.user = user
            client.credentials(HTTP_AUTHORIZATION='Token ' + user.auth_token.key)

        return client


class APIMixin(ClientMixin):
    client_class = APIClient
    is_viewset = False

    def load_json(self, content):
        if not isinstance(content, str):
            return json.loads(str(content, encoding='utf8'))
        else:
            return json.loads(content)

    def get_url(self, **kwargs):
        if self.is_viewset:
            if 'pk' in kwargs:
                return self.reverse(self.view_name + '-detail', kwargs=kwargs)
            if 'pks' in kwargs:
                return self.reverse(self.view_name + '-set', kwargs=kwargs)
            else:
                return self.reverse(self.view_name + '-list', kwargs=kwargs)
        else:
            return self.reverse(self.view_name, kwargs=kwargs)

    def api_create(self, user, data):
        data = self.clean_data(data)
        client = self.get_logged_in_client(user=user)
        return client.post(self.get_url(), data=data, format='json')


class TestPaymentSetupMixin:
    def test_url(self):
        reverse('pn', kwargs={'backend': 'bak'})
        reverse('buy')

    def test_products(self):
        self.assertGreater(len(products.keys()), 0)
        self.assertGreater(len(backends.keys()), 0)

    def test_pipes(self):
        self.assertGreater(len(payment_pipes), 0)


class TestProductMixin:
    def create_item(self, **kwargs):
        return self.product_class.Meta.model.objects.create(**kwargs)

    def create_product(self):
        return self.product_class(item=self.create_item(), backend=self.backend)

    def create_order(self, owner, payment_method):
        product = self.create_product()
        return product.create_order(owner=owner, payment_method=payment_method)

    def test_backend(self):
        self.assertTrue(self.backend.backend_name in backends)

    def test_product(self):
        self.assertTrue(self.product_class.name in products)

    def apply(self, order):
        self.assertFalse(order.handled)
        apply_order(order=order)
        self.assertTrue(order.handled)
