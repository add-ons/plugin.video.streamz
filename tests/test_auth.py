# -*- coding: utf-8 -*-
""" Tests for Auth API """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

from resources.lib import kodiutils
from resources.lib.streamz import Profile
from resources.lib.streamz.api import Api
from resources.lib.streamz.auth import AccountStorage, Auth, LOGIN_STREAMZ, LOGIN_TELENET
from resources.lib.streamz.exceptions import NoLoginException, InvalidLoginException

_LOGGER = logging.getLogger(__name__)


@unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
class TestAuth(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.auth = Auth(kodiutils.get_setting('username'),
                        kodiutils.get_setting('password'),
                        kodiutils.get_setting('loginprovider'),
                        kodiutils.get_setting('profile'),
                        kodiutils.get_tokens_path())
        cls.api = Api(cls.auth)

    def test_login(self):
        account = self.auth.get_tokens()
        self.assertIsInstance(account, AccountStorage)

        profiles = self.auth.get_profiles()
        self.assertIsInstance(profiles[0], Profile)

        api = Api(self.auth)
        config = api.get_config()
        self.assertIsInstance(config, dict)

    def test_errors(self):
        with self.assertRaises(NoLoginException):
            Auth(None, None, None, None, token_path=kodiutils.get_tokens_path())

        with self.assertRaises(InvalidLoginException):
            Auth('test@gmail.com', 'test', LOGIN_STREAMZ, None, token_path=kodiutils.get_tokens_path())

        with self.assertRaises(InvalidLoginException):
            Auth('test@gmail.com', 'test', LOGIN_TELENET, None, token_path=kodiutils.get_tokens_path())


if __name__ == '__main__':
    unittest.main()
