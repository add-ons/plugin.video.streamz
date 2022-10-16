# -*- coding: utf-8 -*-
""" Tests for Auth API """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

import xbmc

from resources.lib import kodiutils
from resources.lib.streamz import STOREFRONT_MOVIES, Movie
from resources.lib.streamz.api import Api
from resources.lib.streamz.auth import Auth
from resources.lib.streamz.stream import ResolvedStream, Stream

_LOGGER = logging.getLogger(__name__)


@unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
class TestStream(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        auth = Auth(kodiutils.get_tokens_path())
        cls.api = Api(auth.get_tokens())
        cls.stream = Stream(auth.get_tokens())

    def tearDown(self):
        xbmc.Player().stop()

    def test_stream(self):
        # Find the first movie from the catalog
        items = self.api.get_storefront(STOREFRONT_MOVIES)
        movie = next(item for item in items if isinstance(item, Movie) if item.available)
        _LOGGER.info('Playing %s', movie)

        stream = self.stream.get_stream('movies', movie.movie_id)
        self.assertIsInstance(stream, ResolvedStream)


if __name__ == '__main__':
    unittest.main()
