# -*- coding: utf-8 -*-
""" Tests for Auth API """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

import xbmc

from resources.lib import kodiutils
from resources.lib.streamz.api import Api
from resources.lib.streamz.auth import Auth
from resources.lib.streamz.stream import Stream, ResolvedStream

_LOGGER = logging.getLogger(__name__)


@unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
class TestStream(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.auth = Auth(kodiutils.get_setting('username'),
                        kodiutils.get_setting('password'),
                        kodiutils.get_setting('profile'),
                        kodiutils.get_tokens_path())
        cls.api = Api(cls.auth)
        cls.stream = Stream(cls.auth)

    def tearDown(self):
        xbmc.Player().stop()

    def test_stream(self):
        stream = self.stream.get_stream('movies', 'dc980ef6-b9f6-4d99-bbf2-5dfa2f9b7867')
        self.assertIsInstance(stream, ResolvedStream)


if __name__ == '__main__':
    unittest.main()
