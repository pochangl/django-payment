import copy
import json
from django.contrib.auth import get_user_model
from django.db.models import Model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

User = get_user_model()

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
        user = user if (user is not None) and (not user.is_anonymous()) else self.create_user()

        client = self.client_class(HTTP_HOST='example.com')
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
