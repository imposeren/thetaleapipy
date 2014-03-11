# -*- coding: utf-8 -*-
import requests
import uuid
import sys

from requests.cookies import create_cookie

import logging

logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)

logger.addHandler(console)
logger.setLevel(logging.INFO)


class TheTaleApi(object):

    def __init__(self, **kwargs):
        self.session_id = None
        self.domain = 'the-tale.org'
        self.host = 'http://' + self.domain

        for key in kwargs:
            setattr(self, key, kwargs[key])
        self.session = requests.Session()

        self.default_params = {'api_version': '1.0', 'api_client': 'thetaleapipy-0.1'}

    def make_request(self, path, method='get', params=None, **kwargs):
        params = params or {}
        actual_params = dict(self.default_params)
        actual_params.update(params)

        url = '{0}{1}'.format(self.host, path)
        method_callable = getattr(self.session, method)
        response = method_callable(url, params=actual_params, **kwargs)
        logger.debug('Getting %s', response.request.url)
        logger.debug('response: %s', response.text)

        self.update_csrf()

        return response

    def update_csrf(self):
        csrf_value = self.session.cookies['csrftoken']
        self.session.headers.update({'X-CSRFToken': csrf_value})

    def auth(self, user, password):
        csrf_token = uuid.uuid4().hex
        self.session.headers.update({'X-CSRFToken': csrf_token})
        cookie = create_cookie('csrftoken', csrf_token, domain=self.domain)
        self.session.cookies.set_cookie(cookie)

        response = self.make_request('/accounts/auth/api/login', 'post', data=dict(email=user, password=password))

        return response

    def game_info(self):
        return self.make_request('/game/api/info').json()

    def get_health(self):
        return self.game_info()['data']['account']['hero']['base']['health']

    def use_ability(self, ability_name='help'):
        return self.make_request('/game/abilities/{0}/api/use'.format(ability_name), 'post').json()

    def logout(self):
        return self.make_request('/accounts/auth/api/logout', 'post').json()


if __name__ == '__main__':
    script, email, password = sys.argv
    api = TheTaleApi()
    api.auth(email, password)

    print(api.get_health())

    api.logout()
