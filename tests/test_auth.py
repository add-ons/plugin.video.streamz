# -*- coding: utf-8 -*-
""" Tests for Auth API """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

from resources.lib import kodiutils
from resources.lib.streamz.auth import Auth

_LOGGER = logging.getLogger(__name__)


@unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
class TestAuth(unittest.TestCase):

    def test_authorization(self):
        auth = Auth(kodiutils.get_tokens_path())
        auth_info = auth.authorize()
        self.assertIsInstance(auth_info, dict)
        self.assertIsNotNone(auth_info.get('user_code'))
        self.assertIsNotNone(auth_info.get('device_code'))
        self.assertIsNotNone(auth_info.get('interval'))
        self.assertIsNotNone(auth_info.get('verification_uri'))
        self.assertIsNotNone(auth_info.get('expires_in'))

    def test_login(self):
        auth = Auth(kodiutils.get_tokens_path())
        tokens = auth.get_tokens()
        self.assertTrue(tokens.is_valid_token())


if __name__ == '__main__':
    unittest.main()
