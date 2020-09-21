# -*- coding: utf-8 -*-
""" Streamz Authentication API """

from __future__ import absolute_import, division, unicode_literals

import json
import logging
import os
import re
from hashlib import md5

from resources.lib.streamz import util, API_ENDPOINT, Profile
from resources.lib.streamz.exceptions import LoginErrorException, NoLoginException

try:  # Python 3
    import jwt
except ImportError:  # Python 2
    # The package is named pyjwt in Kodi 18: https://github.com/lottaboost/script.module.pyjwt/pull/1
    import pyjwt as jwt

_LOGGER = logging.getLogger(__name__)


class AccountStorage:
    """ Data storage for account info """
    jwt_token = ''
    profile = ''
    product = ''

    # Credentials hash
    hash = ''

    def is_valid_token(self):
        """ Validate the JWT to see if it's still valid.

        :rtype: boolean
        """
        if not self.jwt_token:
            # We have no token
            return False

        try:
            # Verify our token to see if it's still valid.
            jwt.decode(self.jwt_token,
                       algorithms=['HS256'],
                       options={'verify_signature': False, 'verify_aud': False})
        except Exception as exc:  # pylint: disable=broad-except
            _LOGGER.debug('JWT is NOT valid: %s', exc)
            return False

        _LOGGER.debug('JWT is valid')
        return True


class Auth:
    """ Streamz Authentication API """

    TOKEN_FILE = 'auth-tokens.json'
    CLIENT_ID = 'WWl9F97L9m56SrPcTmC2hYkCCKcmxevS'  # Website

    # CLIENT_ID = '6sMlUPtp8BsujHOvtkvtC9DJv0gZjP3p'  # Android APP

    def __init__(self, username, password, profile, token_path):
        """ Initialise object """
        self._username = username
        self._password = password
        self._profile = profile

        if not self._username or not self._password:
            raise NoLoginException()

        self._token_path = token_path

        # Load existing account data
        self._account = AccountStorage()
        self._load_cache()

        # Do login so we have valid tokens
        self.login()

        # Apply profile and product
        if profile:
            parts = profile.split(':')
            try:
                self._account.profile = parts[0]
            except (IndexError, AttributeError):
                self._account.profile = None
            try:
                self._account.product = parts[1]
            except (IndexError, AttributeError):
                self._account.product = None

    def _check_credentials_change(self):
        """ Check if credentials have changed """
        old_hash = self._account.hash
        new_hash = md5((self._username + ':' + self._password).encode('utf-8')).hexdigest()
        if new_hash != old_hash:
            _LOGGER.debug('Credentials have changed, clearing tokens.')
            self._account.hash = new_hash
            self.logout()

    def get_profiles(self, products='STREAMZ,STREAMZ_KIDS'):
        """ Returns the available profiles """
        response = util.http_get(API_ENDPOINT + '/profiles', {'products': products}, token=self._account.jwt_token)
        result = json.loads(response.text)

        profiles = [
            Profile(
                key=profile.get('id'),
                product=profile.get('product'),
                name=profile.get('name'),
                gender=profile.get('gender'),
                birthdate=profile.get('birthDate'),
                color=profile.get('color', {}).get('start'),
                color2=profile.get('color', {}).get('end'),
            )
            for profile in result
        ]

        return profiles

    def login(self, force=False):
        """ Make a login request.

        :param bool force:              Force authenticating from scratch without cached tokens.

        :return:
        :rtype: AccountStorage
        """
        # Check if credentials have changed
        self._check_credentials_change()

        # Use cached token if it is still valid
        if force or not self._account.is_valid_token():
            # Do actual login
            self._web_login()

        return self._account

    def logout(self):
        """ Clear the session tokens. """
        self._account.jwt_token = None
        self._save_cache()

    # def _app_login(self):
    #     """ Executes a login and returns the JSON Web Token.
    #     :rtype str
    #     """
    #     # TODO: randomize
    #     nonce = 'CDvv9_Zer256fnt4KaD0ngfekutOSeSPZGg5VBQywyg'
    #
    #     # Start login flow, this will do a redirect to the login form
    #     response = util.http_get('https://login.streamz.be/authorize', params={
    #         'scope': 'openid',
    #         'auth0Client': 'eyJuYW1lIjoiQXV0aDAuQW5kcm9pZCIsImVudiI6eyJhbmRyb2lkIjoiMjMifSwidmVyc2lvbiI6IjEuMjMuMCJ9',
    #         'client_id': self.CLIENT_ID,
    #         'code_challenge_method': 'S256',
    #         'state': 'HWlWHpwwGkzIgFDwBk8VANFZq8b3ANIFY-SBg2FdmTY',  # TODO: random
    #         'response_type': 'code',
    #         'redirect_uri': 'streamz://login.streamz.be/android/be.dpgmedia.streamz/callback',
    #         'code_challenge': 'rI9r3h5EWRT72Vkcyj2z9aumBKFZkoePkg01JIEw2Kw',  # TODO: random
    #         'nonce': nonce,
    #     })
    #     response.raise_for_status()
    #
    #     # Extract configuration of login page
    #     matches_config = re.search(r"var config = JSON\.parse\(decodeURIComponent\(escape\(window\.atob\('([^']+)'", response.text)
    #     if not matches_config:
    #         raise LoginErrorException(code=101)  # Could not extract authentication configuration
    #
    #     config_json = base64.decodebytes(matches_config.group(1).encode())
    #     config = json.loads(config_json)
    #
    #     # Send credentials
    #     response = util.http_post('https://login.streamz.be/usernamepassword/login', data={
    #         "_csrf": config.get('extraParams', {}).get('_csrf'),
    #         "_intstate": config.get('extraParams', {}).get('_intstate'),
    #         "client_id": self.CLIENT_ID,
    #         "connection": "Username-Password-Authentication",
    #         "nonce": nonce,
    #         "password": self._password,
    #         "redirect_uri": "streamz://login.streamz.be/android/be.dpgmedia.streamz/callback",
    #         "response_type": "code",
    #         "scope": "openid",
    #         "state": config.get('extraParams', {}).get('state'),
    #         "tenant": "streamz",
    #         "username": self._username,
    #     }, headers={
    #         'Referrer': response.url,
    #         'Origin': 'https://login.streamz.be',
    #     })
    #
    #     # Extract fields
    #     matches_action = re.search(r'action="([^"]+)', response.text)
    #     if not matches_action:
    #         raise LoginErrorException(code=102)  # Could not extract parameter
    #
    #     matches_wa = re.search(r'name="wa"\s+value="([^"]+)', response.text)
    #     if not matches_wa:
    #         raise LoginErrorException(code=103)  # Could not extract parameter
    #
    #     matches_wresult = re.search(r'name="wresult"\s+value="([^"]+)', response.text)
    #     if not matches_wresult:
    #         raise LoginErrorException(code=104)  # Could not extract parameter
    #
    #     matches_wctx = re.search(r'name="wctx"\s+value="([^"]+)', response.text)
    #     if not matches_wctx:
    #         raise LoginErrorException(code=105)  # Could not extract parameter
    #
    #     # We now need to POST this form to get a code and state.
    #     try:
    #         response = util.http_post(matches_action.group(1), form={
    #             'wa': unescape(matches_wa.group(1)),
    #             'wresult': unescape(matches_wresult.group(1)),
    #             'wctx': unescape(matches_wctx.group(1)),
    #         }, headers={
    #             'Referrer': response.url,
    #             'Origin': 'https://login.streamz.be',
    #         })
    #         response.raise_for_status()
    #     except requests.exceptions.InvalidSchema as exc:
    #
    #         # I found no other way to get this url then by parsing the Exception message. :(
    #         matches_code = re.search(r"code=([^&]+)", str(exc))
    #         if not matches_code:
    #             raise LoginErrorException(code=106)  # Could not extract authentication code
    #         code = matches_code.group(1)
    #
    #         if not code:
    #             raise LoginErrorException(code=107)  # Could not extract authentication code
    #
    #         # matches_state = re.search(r"state=([^&]+)", str(exc))
    #         # if not matches_state:
    #         #     raise LoginErrorException(code=107)  # Could not extract authentication code
    #         # state = matches_state.group(1)
    #
    #         _LOGGER.debug(code)
    #
    #     # To get a JWT, we need to use our code and state
    #     response = util.http_post(matches_action.group(1), data={
    #         "client_id": self.CLIENT_ID,
    #         "redirect_uri": "streamz://login.streamz.be/android/be.dpgmedia.streamz/callback",
    #         "code_verifier": "FuAw_qyJMrLr-Mb8eHOo4EIu_dxmavR1xpLZn7KWZ1Y",  # TODO: how do we get this?
    #         "code": code,
    #         "grant_type": "authorization_code"
    #     }, headers={
    #         'Referrer': response.url,
    #         'Origin': 'https://login.streamz.be',
    #     })
    #     response.raise_for_status()
    #
    #     _LOGGER.debug(response.text)
    #     _LOGGER.debug(response.url)

    def _web_login(self):
        """ Executes a login and returns the JSON Web Token.
        :rtype str
        """
        # Start login flow
        util.http_get('https://account.streamz.be/login')

        # Send login credentials
        util.http_post('https://login.streamz.be/co/authenticate',
                       data={
                           "client_id": self.CLIENT_ID,
                           "username": self._username,
                           "password": self._password,
                           "realm": "Username-Password-Authentication",
                           "credential_type": "http://auth0.com/oauth/grant-type/password-realm"
                       },
                       headers={
                           'Origin': 'https://account.streamz.be',
                           'Referer': 'https://account.streamz.be',
                       })

        response = util.http_get('https://www.streamz.be/streamz/aanmelden')

        # Extract state and code
        matches_state = re.search(r'name="state" value="([^"]+)', response.text)
        if matches_state:
            state = matches_state.group(1)
        else:
            raise LoginErrorException(code=101)  # Could not extract authentication state

        matches_code = re.search(r'name="code" value="([^"]+)', response.text)
        if matches_code:
            code = matches_code.group(1)
        else:
            raise LoginErrorException(code=102)  # Could not extract authentication code

        # Okay, final stage. We now need to POST our state and code to get a valid JWT.
        util.http_post('https://www.streamz.be/streamz/login-callback', form={
            'state': state,
            'code': code,
        })

        # Get JWT from cookies
        self._account.jwt_token = util.SESSION.cookies.get('lfvp_auth')
        self._save_cache()

        return self._account

    def _load_cache(self):
        """ Load tokens from cache """
        try:
            with open(os.path.join(self._token_path, self.TOKEN_FILE), 'r') as fdesc:
                self._account.__dict__ = json.loads(fdesc.read())  # pylint: disable=attribute-defined-outside-init
        except (IOError, TypeError, ValueError):
            _LOGGER.warning('We could not use the cache since it is invalid or non-existent.')

    def _save_cache(self):
        """ Store tokens in cache """
        if not os.path.exists(self._token_path):
            os.makedirs(self._token_path)

        with open(os.path.join(self._token_path, self.TOKEN_FILE), 'w') as fdesc:
            json.dump(self._account.__dict__, fdesc, indent=2)
