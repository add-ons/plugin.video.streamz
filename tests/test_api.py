# -*- coding: utf-8 -*-
""" Tests for Content API """

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import unittest

from resources.lib import kodiutils
from resources.lib.streamz import STOREFRONT_MAIN, STOREFRONT_MOVIES, STOREFRONT_PAGE_CONTINUE_WATCHING, STOREFRONT_SERIES, Episode, Movie, Program
from resources.lib.streamz.api import Api
from resources.lib.streamz.auth import Auth
from resources.lib.streamz.exceptions import UnavailableException

EXAMPLE_MOVIE = 'f384c9f1-e2dc-4f82-9954-a3f91589385a'  # Niet schieten
EXAMPLE_PROGRAM = '6382e070-c284-4538-b60a-44f337ba6157'  # FC De Kampioenen
EXAMPLE_EPISODE = '7c1c2b5c-de72-45d6-ab88-8dd63edddf43'  # FC De Kampioenen S01E01


@unittest.skipUnless(os.environ.get('ADDON_TOKEN') and os.environ.get('ADDON_PROFILE'), 'Skipping since we have no credentials.')
class TestApi(unittest.TestCase):
    """ Tests for Streamz API """

    @classmethod
    def setUpClass(cls):
        auth = Auth(kodiutils.get_tokens_path())
        cls.api = Api(auth.get_tokens())

    def test_get_config(self):
        config = self.api.get_config()
        self.assertTrue(config)

    def test_recommendations(self):
        main_recommendations = self.api.get_storefront(STOREFRONT_MAIN)
        self.assertIsInstance(main_recommendations, list)

        movie_recommendations = self.api.get_storefront(STOREFRONT_MOVIES)
        self.assertIsInstance(movie_recommendations, list)

        serie_recommendations = self.api.get_storefront(STOREFRONT_SERIES)
        self.assertIsInstance(serie_recommendations, list)

    def test_continuewatching(self):
        result = self.api.get_storefront_category(STOREFRONT_MAIN, STOREFRONT_PAGE_CONTINUE_WATCHING)
        self.assertIsInstance(result.content, list)

    def test_mylist(self):
        mylist = self.api.get_mylist()
        self.assertIsInstance(mylist, list)

    def test_search(self):
        results = self.api.do_search('huis')
        self.assertIsInstance(results, list)

    def test_get_program(self):
        results = self.api.get_program(EXAMPLE_PROGRAM)
        self.assertIsInstance(results, Program)

    def test_get_movie(self):
        results = self.api.get_movie(EXAMPLE_MOVIE)
        self.assertIsInstance(results, Movie)

    def test_get_episode(self):
        results = self.api.get_episode(EXAMPLE_EPISODE)
        self.assertIsInstance(results, Episode)

    def test_errors(self):
        with self.assertRaises(UnavailableException):
            self.api.get_movie('0')

        with self.assertRaises(UnavailableException):
            self.api.get_program('0')

        with self.assertRaises(UnavailableException):
            self.api.get_episode('0')


if __name__ == '__main__':
    unittest.main()
