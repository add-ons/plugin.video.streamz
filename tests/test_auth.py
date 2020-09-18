# -*- coding: utf-8 -*-
""" Tests for Auth API """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

from resources.lib import kodiutils
from resources.lib.streamz import Profile
from resources.lib.streamz.api import Api
from resources.lib.streamz.auth import AccountStorage, Auth

_LOGGER = logging.getLogger(__name__)


@unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
class TestAuth(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAuth, self).__init__(*args, **kwargs)

        self._auth = Auth(kodiutils.get_setting('username'),
                          kodiutils.get_setting('password'),
                          kodiutils.get_setting('profile'),
                          kodiutils.get_tokens_path())
        self._api = Api(self._auth)

    def test_login(self):
        account = self._auth.login()
        self.assertIsInstance(account, AccountStorage)

        profiles = self._auth.get_profiles()
        self.assertIsInstance(profiles[0], Profile)

        api = Api(self._auth)
        config = api.get_config()
        self.assertIsInstance(config, dict)


if __name__ == '__main__':
    unittest.main()
