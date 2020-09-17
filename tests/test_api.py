# -*- coding: utf-8 -*-
""" Tests for Content API """

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

import xbmc

from resources.lib import kodiutils
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

    def setUp(self):
        # Don't warn that we don't close our HTTPS connections, this is on purpose.
        # warnings.simplefilter("ignore", ResourceWarning)
        pass

    def tearDown(self):
        xbmc.Player().stop()

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_catalog(self):
        categories = self._api.get_categories()
        self.assertTrue(categories)

        items = self._api.get_items()
        self.assertTrue(items)

        # # Movies
        # movie = next(a for a in items if isinstance(a, Movie) and not a.geoblocked)
        # info = self._vtmgo.get_movie(movie.movie_id)
        # self.assertTrue(info)
        # try:
        #     self._player.play('movies', info.movie_id)
        # except StreamGeoblockedException:
        #     pass
        #
        # # Programs
        # program = next(a for a in items if isinstance(a, Program) and not a.geoblocked)
        # info = self._vtmgo.get_program(program.program_id)
        # self.assertTrue(info)
        #
        # season = list(info.seasons.values())[0]
        # episode = list(season.episodes.values())[0]
        # info = self._vtmgo.get_episode(episode.episode_id)
        # self.assertTrue(info)
        # try:
        #     self._player.play('episodes', info.episode_id)
        # except StreamGeoblockedException:
        #     pass

    # def test_recommendations(self):
    #     recommendations = self._vtmgo.get_recommendations()
    #     self.assertTrue(recommendations)
    #
    # def test_mylist(self):
    #     mylist = self._vtmgo.get_swimlane('my-list')
    #     self.assertIsInstance(mylist, list)
    #
    # def test_continuewatching(self):
    #     mylist = self._vtmgo.get_swimlane('continue-watching')
    #     self.assertIsInstance(mylist, list)

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_search(self):
        results = self._api.do_search('huis')
        self.assertIsInstance(results, list)


if __name__ == '__main__':
    unittest.main()
