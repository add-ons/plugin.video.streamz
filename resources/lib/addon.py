# -*- coding: utf-8 -*-
""" Addon code """

from __future__ import absolute_import, division, unicode_literals

import logging

import routing

from resources.lib import kodilogging, kodiutils

kodilogging.config()
routing = routing.Plugin()  # pylint: disable=invalid-name
_LOGGER = logging.getLogger(__name__)


@routing.route('/')
def index():
    """ Show the profile selection, or go to the main menu. """
    # Verify credentials
    from resources.lib.modules.authentication import Authentication
    if not Authentication.verify_credentials():
        kodiutils.end_of_directory()
        kodiutils.execute_builtin('ActivateWindow(Home)')
        return

    if kodiutils.get_setting_bool('auto_login') and kodiutils.get_setting('profile'):
        show_main_menu()
    else:
        select_profile()


@routing.route('/menu')
def show_main_menu():
    """ Show the main menu """
    from resources.lib.modules.menu import Menu
    Menu().show_mainmenu()


@routing.route('/select-profile')
@routing.route('/select-profile/<key>')
def select_profile(key=None):
    """ Select your profile """
    from resources.lib.modules.authentication import Authentication
    Authentication().select_profile(key)


@routing.route('/catalog')
def show_catalog():
    """ Show the catalog """
    from resources.lib.modules.catalog import Catalog
    Catalog().show_catalog()


@routing.route('/catalog/all')
def show_catalog_all():
    """ Show a category in the catalog """
    from resources.lib.modules.catalog import Catalog
    Catalog().show_catalog_category()


@routing.route('/catalog/by-category/<category>')
def show_catalog_category(category):
    """ Show a category in the catalog """
    from resources.lib.modules.catalog import Catalog
    Catalog().show_catalog_category(category)


@routing.route('/catalog/program/<program>')
def show_catalog_program(program):
    """ Show a program from the catalog """
    from resources.lib.modules.catalog import Catalog
    Catalog().show_program(program)


@routing.route('/program/program/<program>/<season>')
def show_catalog_program_season(program, season):
    """ Show a program from the catalog """
    from resources.lib.modules.catalog import Catalog
    Catalog().show_program_season(program, int(season))


@routing.route('/catalog/recommendations/<storefront>')
def show_recommendations(storefront):
    """ Shows the recommendations of a storefront """
    from resources.lib.modules.catalog import Catalog
    Catalog().show_recommendations(storefront)


@routing.route('/catalog/recommendations/<storefront>/<category>')
def show_recommendations_category(storefront, category):
    """ Show the items in a recommendations category """
    from resources.lib.modules.catalog import Catalog
    Catalog().show_recommendations_category(storefront, category)


@routing.route('/catalog/mylist')
def show_mylist():
    """ Show the items in "My List" """
    from resources.lib.modules.catalog import Catalog
    Catalog().show_mylist()


@routing.route('/catalog/mylist/add/<video_type>/<content_id>')
def mylist_add(video_type, content_id):
    """ Add an item to "My List" """
    from resources.lib.modules.catalog import Catalog
    Catalog().mylist_add(video_type, content_id)


@routing.route('/catalog/mylist/del/<video_type>/<content_id>')
def mylist_del(video_type, content_id):
    """ Remove an item from "My List" """
    from resources.lib.modules.catalog import Catalog
    Catalog().mylist_del(video_type, content_id)


@routing.route('/catalog/continuewatching')
def show_continuewatching():
    """ Show the items in "Continue Watching" """
    from resources.lib.modules.catalog import Catalog
    Catalog().show_continuewatching()


@routing.route('/search')
@routing.route('/search/<query>')
def show_search(query=None):
    """ Shows the search dialog """
    from resources.lib.modules.search import Search
    Search().show_search(query)


@routing.route('/metadata/update')
def metadata_update():
    """ Update the metadata for the listings (called from settings) """
    from resources.lib.modules.metadata import Metadata
    Metadata().update()


@routing.route('/metadata/clean')
def metadata_clean():
    """ Clear metadata (called from settings) """
    from resources.lib.modules.metadata import Metadata
    Metadata().clean()


@routing.route('/play/catalog/<category>/<item>')
def play(category, item):
    """ Play the requested item """
    from resources.lib.modules.player import Player
    Player().play(category, item)


def run(params):
    """ Run the routing plugin """
    routing.run(params)
