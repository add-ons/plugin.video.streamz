# -*- coding: utf-8 -*-
""" Tests for Auth API """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

from resources.lib import kodiutils
from resources.lib.streamz.api import Api
from resources.lib.streamz.auth import Auth
from resources.lib.streamz.stream import Stream, ResolvedStream

_LOGGER = logging.getLogger(__name__)


class TestStream(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestStream, self).__init__(*args, **kwargs)

        self._auth = Auth(kodiutils.get_setting('username'),
                          kodiutils.get_setting('password'),
                          kodiutils.get_setting('profile'),
                          kodiutils.get_tokens_path())
        self._api = Api(self._auth)
        self._stream = Stream(self._auth)

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_login(self):
        stream = self._stream.get_stream('movies', '6af62507-229b-41bb-afda-8519c4ccb4fe')
        self.assertIsInstance(stream, ResolvedStream)


if __name__ == '__main__':
    unittest.main()
