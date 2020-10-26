# -*- coding: utf-8 -*-
""" Library module """

from __future__ import absolute_import, division, unicode_literals

import logging

from resources.lib import kodiutils
from resources.lib.modules.menu import Menu
from resources.lib.streamz import Movie, Program
from resources.lib.streamz.api import Api, CACHE_PREVENT, CACHE_AUTO
from resources.lib.streamz.auth import Auth
from resources.lib.streamz.exceptions import UnavailableException

_LOGGER = logging.getLogger(__name__)

LIBRARY_FULL_CATALOG = 0
LIBRARY_ONLY_MYLIST = 1


class Library:
    """ Menu code related to the catalog """

    def __init__(self):
        """ Initialise object """
        self._auth = Auth(kodiutils.get_setting('username'),
                          kodiutils.get_setting('password'),
                          kodiutils.get_setting('loginprovider'),
                          kodiutils.get_setting('profile'),
                          kodiutils.get_tokens_path())
        self._api = Api(self._auth)

    def show_library_movies(self):
        """ Return a list of the movies that should be exported. """
        if kodiutils.get_setting_int('library_movies') == LIBRARY_FULL_CATALOG:
            # Full catalog
            # Use cache if available, fetch from api otherwise so we get rich metadata for new content
            items = self._api.get_items(content_filter=Movie, cache=CACHE_AUTO)

            # Remove old caches
            # When Kodi does a clean of the library, we validate a movie by its presence in the cache, so we need to make sure that
            # items that aren't available anymore are also removed from the cache
            kodiutils.cleanup_cache('movie', [item.movie_id for item in items])
        else:
            # Only favourites, use cache if available, fetch from api otherwise
            items = self._api.get_swimlane('my-list', content_filter=Movie)

        listing = []
        for item in items:
            title_item = Menu.generate_titleitem(item)
            # title_item.path = kodiutils.url_for('library_movies', movie=item.movie_id)
            title_item.path = 'plugin://plugin.video.streamz/library/movies/?movie=%s' % item.movie_id
            listing.append(title_item)

        kodiutils.show_listing(listing, 30003, content='movies', sort=['label', 'year', 'duration'])

    def show_library_tvshows(self):
        """ Return a list of the series that should be exported. """
        if kodiutils.get_setting_int('library_tvshows') == LIBRARY_FULL_CATALOG:
            # Full catalog
            # Use cache if available, fetch from api otherwise so we get rich metadata for new content
            # NOTE: We should probably use CACHE_PREVENT here, so we can pick up new episodes, but we can't since that would
            #       require a massive amount of API calls for each update. We do this only for programs in 'My list'.
            items = self._api.get_items(content_filter=Program, cache=CACHE_AUTO)

            # Remove old caches
            # When Kodi does a clean of the library, we validate a tvshow by its presence in the cache, so we need to make sure that
            # items that aren't available anymore are also removed from the cache
            kodiutils.cleanup_cache('program', [item.program_id for item in items])
        else:
            # Only favourites, don't use cache, fetch from api
            # If we use CACHE_AUTO, we will miss updates until the user manually opens the program in the Add-on
            items = self._api.get_swimlane('my-list', content_filter=Program, cache=CACHE_PREVENT)

        listing = []
        for item in items:
            title_item = Menu.generate_titleitem(item)
            # title_item.path = kodiutils.url_for('library_tvshows', program=item.program_id) + '/'  # Folders need a trailing slash
            title_item.path = 'plugin://plugin.video.streamz/library/tvshows/?program={program_id}'.format(program_id=item.program_id)
            listing.append(title_item)

        kodiutils.show_listing(listing, 30003, content='tvshows', sort=['label', 'year', 'duration'])

    def show_library_tvshows_program(self, program):
        """ Return a list of the episodes that should be exported. """
        program_obj = self._api.get_program(program)

        listing = []
        for season in list(program_obj.seasons.values()):
            for item in list(season.episodes.values()):
                title_item = Menu.generate_titleitem(item)
                # title_item.path = kodiutils.url_for('library_tvshows', program=item.program_id, episode=item.episode_id)
                title_item.path = 'plugin://plugin.video.streamz/library/tvshows/?program={program_id}&episode={episode_id}'.format(program_id=item.program_id,
                                                                                                                                    episode_id=item.episode_id)
                listing.append(title_item)

        # Sort by episode number by default. Takes seasons into account.
        kodiutils.show_listing(listing, 30003, content='episodes', sort=['episode', 'duration'])

    def check_library_movie(self, movie):
        """ Check if the given movie is still available. """
        _LOGGER.debug('Checking if movie %s is still available', movie)

        # Our parent path always exists
        if movie is None:
            kodiutils.library_return_status(True)
            return

        if kodiutils.get_setting_int('library_movies') == LIBRARY_FULL_CATALOG:
            # Full library
            try:
                result = self._api.get_movie(movie)
            except UnavailableException:
                result = None
            kodiutils.library_return_status(result is not None)

        else:
            # Only favourites
            mylist_ids = self._api.get_swimlane_ids('my-list')
            kodiutils.library_return_status(movie in mylist_ids)

    def check_library_tvshow(self, program):
        """ Check if the given program is still available. """
        _LOGGER.debug('Checking if program %s is still available', program)

        # Our parent path always exists
        if program is None:
            kodiutils.library_return_status(True)
            return

        if kodiutils.get_setting_int('library_tvshows') == LIBRARY_FULL_CATALOG:
            # Full catalog
            try:
                result = self._api.get_program(program, cache=CACHE_PREVENT)
            except UnavailableException:
                result = None
            kodiutils.library_return_status(result is not None)

        else:
            # Only favourites
            mylist_ids = self._api.get_swimlane_ids('my-list')
            kodiutils.library_return_status(program in mylist_ids)

    @staticmethod
    def configure():
        """ Configure the library integration. """
        # There seems to be no way to add sources automatically.
        # * https://forum.kodi.tv/showthread.php?tid=228840

        # Open the sources view
        kodiutils.execute_builtin('ActivateWindow(Videos,sources://video/)')

    @staticmethod
    def update():
        """ Update the library integration. """
        kodiutils.jsonrpc(method='VideoLibrary.Scan')

    @staticmethod
    def clean():
        """ Cleanup the library integration. """
        kodiutils.jsonrpc(method='VideoLibrary.Clean')
