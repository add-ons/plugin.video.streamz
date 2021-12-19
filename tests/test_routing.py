# -*- coding: utf-8 -*-
""" Tests for Routing """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

import xbmc

from resources.lib import addon, kodiutils
from resources.lib.streamz import STOREFRONT_MAIN

routing = addon.routing  # pylint: disable=invalid-name

_LOGGER = logging.getLogger(__name__)

EXAMPLE_MOVIE = '9f33cbca-0321-4a2f-9ac4-374ff69e2c4e'  # Gooische Vrouwen 2
EXAMPLE_PROGRAM = '6382e070-c284-4538-b60a-44f337ba6157'  # FC De Kampioenen
EXAMPLE_EPISODE = '7c1c2b5c-de72-45d6-ab88-8dd63edddf43'  # FC De Kampioenen S01E01


@unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
class TestRouting(unittest.TestCase):
    """ Tests for Routing """

    def __init__(self, *args, **kwargs):
        super(TestRouting, self).__init__(*args, **kwargs)

    def tearDown(self):
        xbmc.Player().stop()

    def test_index(self):
        routing.run([routing.url_for(addon.index), '0', ''])

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
                                     category='5d07c416-dc08-4e5b-a3d2-8134121b6bd4'), '0', ''])  # Aanbevolen voor jou

    def test_catalog_mylist_menu(self):
        routing.run([routing.url_for(addon.show_mylist), '0', ''])

    def test_catalog_continuewatching_menu(self):
        routing.run([routing.url_for(addon.show_continuewatching), '0', ''])

    def test_search_menu(self):
        routing.run([routing.url_for(addon.show_search), '0', ''])
        routing.run([routing.url_for(addon.show_search, query='kampioenen'), '0', ''])
        routing.run([routing.url_for(addon.show_search, query='hbo'), '0', ''])

    def test_play_movie(self):
        old_setting = kodiutils.get_setting('manifest_proxy')

        kodiutils.set_setting('manifest_proxy', 'true')
        routing.run([routing.url_for(addon.play, category='movies', item=EXAMPLE_MOVIE), '0', ''])

        kodiutils.set_setting('manifest_proxy', 'false')
        routing.run([routing.url_for(addon.play, category='movies', item=EXAMPLE_MOVIE), '0', ''])

        kodiutils.set_setting('manifest_proxy', old_setting)

    def test_play_episode(self):
        routing.run([routing.url_for(addon.play, category='episodes', item=EXAMPLE_EPISODE), '0', ''])


if __name__ == '__main__':
    unittest.main()
