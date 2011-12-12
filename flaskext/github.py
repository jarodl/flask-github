# -*- coding: utf-8 -*-
"""
    flaskext.github
    ---------------

    Authenticate users in your Flask app with Github.
"""
import json
import oauth2
from httplib2 import Http
from functools import wraps
from urllib import urlencode
from urlparse import parse_qs
from flask import redirect, request

class GithubAuth(object):
    """
    Provides decorators for authenticating users with Github within a Flask
    application. Helper methods are also provided for checking organization
    access and getting user data from the Github API.
    """

    def __init__(self, client_id, client_secret, session_key):
        """
        client_id:          Created by Github when a new application is made.

        client_secret:      Created by Github when a new application is made.

        session_key:        The key for the value stored in the session
                            used to determine if the user has been
                            authenticated or not.
        """
        self.user = None
        self.client_id = client_id
        self.session_key = session_key
        self.client_secret = client_secret
        self.get_access_token = lambda: None
        self.base_url = 'https://api.github.com/'
        self.base_auth_url = 'https://github.com/login/oauth/'

    def access_token_getter(self, f):
        """
        Registers a function as the access_token getter. Must return the
        access_token used to make requests to Github on the user's behalf.
        """
        self.get_access_token = f
        return f

    def authorize(self, callback_url=None):
        """
        Redirect to Github and request access to a user's data. If a callback
        URL is not provided the URL configured in the Github settings for the
        app is used.
        """
        params = {
            'client_id': self.client_id,
        }
        if callback_url is not None:
            params.update({'redirect_uri': callback_url})
        auth_url = self.base_auth_url + 'authorize?' + urlencode(params)
        return redirect(auth_url)

    def raw_request(self, base_url, resource, params, method, accept='json'):
        """
        Makes a raw HTTP request and returns the response and content.
        """
        http = Http(disable_ssl_certificate_validation=True)
        params.update({'access_token': self.get_access_token()})
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": accept
        }
        url = base_url + resource + '?' + urlencode(params)
        resp, content = http.request(url, method)
        return resp, content

    def get_resource(self, resource, params={}):
        """
        Makes a raw HTTP GET request and returns the response and content.
        """
        return self.raw_request(self.base_url, resource, params, "GET")

    def handle_response(self):
        """
        Handles response after the redirect to Github. This response
        determines if the user has allowed the this application access. If we
        were then we send a POST request for the access_key used to
        authenticate requests to Github.
        """
        params = {
            'code': request.args.get('code'),
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        resp, content = self.raw_request(self.base_auth_url, 'access_token',
            params, "POST")
        data = parse_qs(content)
        for k, v in data.items():
            if len(v) == 1:
                data[k] = v[0]
        return data

    def handle_invalid_response(self):
        """
        """
        return None

    def authorized_handler(self, f):
        """
        Decorator for the route that is used as the callback for authorizing
        with Github. This callback URL can be set in the settings for the app
        or passed in during authorization.
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'code' in request.args:
                data = self.handle_response()
            else:
                data = self.handle_invalid_response()
            return f(*((data,) + args), **kwargs)
        return decorated

    def github_user(self):
        """
        Sets the user to the currently authorized user if it is not already and
        returns it. The user object is the dictionary response from the API.
        """
        if self.user is None:
            self.user = self.get_github_user()
        return self.user

    def get_github_user(self):
        """
        Requests the authenticated user's data from Github.
        """
        path = 'user'
        resp, content = self.get_resource(path)
        user = json.loads(content)
        return user

    def has_org_access(self, organization):
        """
        Checks to see if the authenticated user is a member of the given
        organization.
        """
        path = 'orgs/' + organization + '/members'
        resp, content = self.get_resource(path)
        org_members = json.loads(content)
        user = self.github_user()
        for member in org_members:
            if member['login'] == user['login']:
                return True
        return False
