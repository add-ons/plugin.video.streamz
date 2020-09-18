# -*- coding: utf-8 -*-
""" Tests for Content API """

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from resources.lib import kodiutils
from resources.lib.streamz import STOREFRONT_MAIN, STOREFRONT_MOVIES, STOREFRONT_SERIES
from resources.lib.streamz.api import Api
from resources.lib.streamz.auth import Auth


class TestApi(unittest.TestCase):
    """ Tests for Streamz API """

    def __init__(self, *args, **kwargs):
        super(TestApi, self).__init__(*args, **kwargs)

        self._auth = Auth(kodiutils.get_setting('username'),
                          kodiutils.get_setting('password'),
                          kodiutils.get_setting('profile'),
                          kodiutils.get_tokens_path())
        self._api = Api(self._auth)

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_catalog(self):
        categories = self._api.get_categories()
        self.assertTrue(categories)

        items = self._api.get_items()
        self.assertTrue(items)

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_recommendations(self):
        main_recommendations = self._api.get_recommendations(STOREFRONT_MAIN)
        self.assertIsInstance(main_recommendations, list)

        movie_recommendations = self._api.get_recommendations(STOREFRONT_MOVIES)
        self.assertIsInstance(movie_recommendations, list)

        serie_recommendations = self._api.get_recommendations(STOREFRONT_SERIES)
        self.assertIsInstance(serie_recommendations, list)

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_continuewatching(self):
        mylist = self._api.get_swimlane('continue-watching')
        self.assertIsInstance(mylist, list)

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_mylist(self):
        mylist = self._api.get_swimlane('my-list')
        self.assertIsInstance(mylist, list)

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_search(self):
        results = self._api.do_search('huis')
        self.assertIsInstance(results, list)


if __name__ == '__main__':
    unittest.main()
