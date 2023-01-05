# -*- coding: utf-8 -*-
""" Tests for Routing """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os
import unittest

import xbmc

from resources.lib import addon
from resources.lib.streamz import STOREFRONT_MAIN

routing = addon.routing  # pylint: disable=invalid-name

_LOGGER = logging.getLogger(__name__)

EXAMPLE_MOVIE = 'f384c9f1-e2dc-4f82-9954-a3f91589385a'  # Niet schieten
EXAMPLE_PROGRAM = '6382e070-c284-4538-b60a-44f337ba6157'  # FC De Kampioenen
EXAMPLE_EPISODE = '7c1c2b5c-de72-45d6-ab88-8dd63edddf43'  # FC De Kampioenen S01E01


@unittest.skipUnless(os.environ.get('ADDON_TOKEN') and os.environ.get('ADDON_PROFILE'), 'Skipping since we have no credentials.')
class TestRouting(unittest.TestCase):
    """ Tests for Routing """

    def __init__(self, *args, **kwargs):
        super(TestRouting, self).__init__(*args, **kwargs)

    def tearDown(self):
        xbmc.Player().stop()

    def test_index(self):
        routing.run([routing.url_for(addon.index), '0', ''])

    def test_clear_cache(self):
        routing.run([routing.url_for(addon.auth_clear_cache), '0', ''])

    def test_main_menu(self):
        routing.run([routing.url_for(addon.show_main_menu), '0', ''])

    def test_catalog_program_menu(self):
        routing.run([routing.url_for(addon.show_catalog_program, program=EXAMPLE_PROGRAM), '0', ''])

    def test_catalog_program_season_menu(self):
        routing.run([routing.url_for(addon.show_catalog_program_season, program=EXAMPLE_PROGRAM, season=-1), '0', ''])

    def test_catalog_recommendations_menu(self):
        routing.run([routing.url_for(addon.show_recommendations, storefront=STOREFRONT_MAIN), '0', ''])
        routing.run([routing.url_for(addon.show_recommendations_category,
                                     storefront=STOREFRONT_MAIN,
                                     category='cae1712c-e4ad-40fb-965f-757179a47365'), '0', ''])  # Toptitels van het moment

    def test_catalog_mylist_menu(self):
        routing.run([routing.url_for(addon.show_mylist), '0', ''])

    def test_catalog_continuewatching_menu(self):
        routing.run([routing.url_for(addon.show_continuewatching), '0', ''])

    def test_search_menu(self):
        routing.run([routing.url_for(addon.show_search), '0', ''])
        routing.run([routing.url_for(addon.show_search, query='kampioenen'), '0', ''])
        routing.run([routing.url_for(addon.show_search, query='hbo'), '0', ''])

    def test_play_movie(self):
        routing.run([routing.url_for(addon.play, category='movies', item=EXAMPLE_MOVIE), '0', ''])

    def test_play_episode(self):
        routing.run([routing.url_for(addon.play, category='episodes', item=EXAMPLE_EPISODE), '0', ''])


if __name__ == '__main__':
    unittest.main()
