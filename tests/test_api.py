# -*- coding: utf-8 -*-
""" Tests for Content API """

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from resources.lib import kodiutils
from resources.lib.streamz import STOREFRONT_MAIN, STOREFRONT_MOVIES, STOREFRONT_SERIES
from resources.lib.streamz.api import Api
from resources.lib.streamz.auth import Auth
from resources.lib.streamz.exceptions import UnavailableException


@unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
class TestApi(unittest.TestCase):
    """ Tests for Streamz API """

    @classmethod
    def setUpClass(cls):
        cls.auth = Auth(kodiutils.get_setting('username'),
                        kodiutils.get_setting('password'),
                        kodiutils.get_setting('loginprovider'),
                        kodiutils.get_setting('profile'),
                        kodiutils.get_tokens_path())
        cls.api = Api(cls.auth)

    def test_get_config(self):
        config = self.api.get_config()
        self.assertTrue(config)

    def test_catalog(self):
        items = self.api.get_items()
        self.assertTrue(items)

    def test_recommendations(self):
        main_recommendations = self.api.get_storefront(STOREFRONT_MAIN)
        self.assertIsInstance(main_recommendations, list)

        movie_recommendations = self.api.get_storefront(STOREFRONT_MOVIES)
        self.assertIsInstance(movie_recommendations, list)

        serie_recommendations = self.api.get_storefront(STOREFRONT_SERIES)
        self.assertIsInstance(serie_recommendations, list)

    def test_continuewatching(self):
        mylist = self.api.get_swimlane('continue-watching')
        self.assertIsInstance(mylist, list)

    def test_mylist(self):
        mylist = self.api.get_swimlane('my-list')
        self.assertIsInstance(mylist, list)

    def test_search(self):
        results = self.api.do_search('huis')
        self.assertIsInstance(results, list)

    def test_mylist_ids(self):
        mylist = self.api.get_mylist_ids()
        self.assertIsInstance(mylist, list)

    def test_catalog_ids(self):
        mylist = self.api.get_catalog_ids()
        self.assertIsInstance(mylist, list)

    def test_errors(self):
        with self.assertRaises(UnavailableException):
            self.api.get_movie('0')

        with self.assertRaises(UnavailableException):
            self.api.get_program('0')

        with self.assertRaises(UnavailableException):
            self.api.get_episode('0')

        with self.assertRaises(UnavailableException):
            self.api.get_items('movies')


if __name__ == '__main__':
    unittest.main()
