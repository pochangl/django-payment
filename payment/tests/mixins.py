
class ClientMixin:

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
        return user

    def get_logged_in_client(self, user=None):
        '''
            return a logged in client
            user model can be found in client.user
        '''
        user = user if (user is not None) and (not user.is_anonymous()) else self.create_user()

        client = self.client_class()
        client.user = user
        client.credentials(HTTP_AUTHORIZATION='Token ' + user.auth_token.key)
        return client

    def api_create(self, user, data):
        data = self.clean_data(data)
        client = self.get_logged_in_client(user=user)
        return client.post(self.get_url(), data=data, format='json')
