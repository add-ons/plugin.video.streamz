# -*- coding: utf-8 -*-
""" Streamz API """

from __future__ import absolute_import, division, unicode_literals

import json
import logging

from resources.lib import kodiutils
from resources.lib.streamz import API_ANDROID_ENDPOINT, API_ENDPOINT, STOREFRONT_MAIN, Category, Episode, Movie, Program, Season, Teaser, util

_LOGGER = logging.getLogger(__name__)

try:  # Python 3
    from urllib.parse import quote
except ImportError:  # Python 2
    from urllib import quote

CACHE_AUTO = 1  # Allow to use the cache, and query the API if no cache is available
CACHE_ONLY = 2  # Only use the cache, don't use the API
CACHE_PREVENT = 3  # Don't use the cache

CONTENT_TYPE_MOVIE = 'MOVIE'
CONTENT_TYPE_PROGRAM = 'PROGRAM'
CONTENT_TYPE_EPISODE = 'EPISODE'

ROW_TYPES_CATEGORY = ['SWIMLANE_DEFAULT', 'SWIMLANE_PORTRAIT', 'SWIMLANE_LANDSCAPE', 'SWIMLANE_TOP10', 'CONTINUE_WATCHING']


class Api:
    """ Streamz API """

    def __init__(self, tokens):
        """ Initialise object
        :param resources.lib.vtmgo.vtmgoauth.AccountStorage token:       An authenticated token.
        """
        self._tokens = tokens

    def _mode(self):
        """ Return the mode that should be used for API calls. """
        return self._tokens.product

    @staticmethod
    def get_config():
        """ Returns the config for the app. """
        response = util.http_get(API_ANDROID_ENDPOINT + '/streamz/config')
        info = json.loads(response.text)

        # This contains a player.updateIntervalSeconds that could be used to notify Streamz about the playing progress
        return info

    def get_storefront(self, storefront):
        """ Returns a storefront.

         :param str storefront:         The ID of the storefront.
         :rtype: list[Category|Teaser]
         """
        result = self._get_storefront_json(storefront)

        items = []
        for row in result.get('rows', []):
            if row.get('rowType') in ROW_TYPES_CATEGORY:
                items.append(Category(
                    category_id=row.get('id'),
                    title=(row.get('title') or '').strip(),
                ))
                continue

            if row.get('rowType') == 'CAROUSEL':
                items.extend(self._parse_teaser(item) for item in row.get('teasers', []))
                continue

            if row.get('rowType') in ['TOP_BANNER', 'MARKETING_BLOCK']:
                if row.get('teaser'):
                    items.append(self._parse_teaser(row.get('teaser')))
                continue

            _LOGGER.debug('Skipping recommendation %s with type %s', row.get('title'), row.get('rowType'))

        return [item for item in items if item]

    def get_continue_watching_id(self):
        """ Returns the ID of the "Continue watching" row on the main storefront, or None.

        :rtype: str
        """
        result = self._get_storefront_json(STOREFRONT_MAIN)
        for row in result.get('rows', []):
            if row.get('rowType') == 'CONTINUE_WATCHING':
                return row.get('id')
        return None

    def _get_storefront_json(self, storefront):
        """ Fetch the raw json of a storefront. """
        response = util.http_get(API_ENDPOINT + '/%s/storefronts/%s' % (self._mode(), storefront),
                                 token=self._tokens.access_token,
                                 profile=self._tokens.profile)
        return json.loads(response.text)

    def get_storefront_category(self, storefront, category):
        """ Returns a storefront.

         :param str storefront:         The ID of the storefront.
         :param str category:           The ID of the category.
         :rtype: Category
         """
        response = util.http_get(API_ENDPOINT + '/%s/storefronts/%s/detail/%s' % (self._mode(), storefront, category),
                                 token=self._tokens.access_token,
                                 profile=self._tokens.profile)
        result = json.loads(response.text)

        items = [self._parse_teaser(item) for item in result.get('row', {}).get('teasers', [])]

        return Category(category_id=category, title=result.get('row', {}).get('title'), content=[item for item in items if item])

    def get_mylist(self, content_filter=None, cache=CACHE_ONLY):
        """ Returns the contents of My List """
        response = util.http_get(API_ENDPOINT + '/%s/my-list' % (self._mode()),
                                 token=self._tokens.access_token,
                                 profile=self._tokens.profile)

        # Result can be empty
        if not response.text:
            return []

        result = json.loads(response.text)

        items = [self._parse_teaser(item, cache=cache) for item in result.get('teasers', [])]
        if content_filter:
            items = [item for item in items if isinstance(item, content_filter)]

        return [item for item in items if item]

    def add_mylist(self, content_id):
        """ Add an item to My List. """
        util.http_put(API_ENDPOINT + '/%s/userData/myList/%s' % (self._mode(), content_id),
                      token=self._tokens.access_token,
                      profile=self._tokens.profile)
        kodiutils.set_cache(['swimlane', 'my-list'], None)

    def del_mylist(self, content_id):
        """ Delete an item from My List. """
        util.http_delete(API_ENDPOINT + '/%s/userData/myList/%s' % (self._mode(), content_id),
                         token=self._tokens.access_token,
                         profile=self._tokens.profile)
        kodiutils.set_cache(['swimlane', 'my-list'], None)

    def get_detail(self, detail_id, cache=CACHE_AUTO):
        """ Get the details of the specified detail page. Returns a Movie or a Program, or None
        when only the cache may be used and nothing is cached.

        :type detail_id: str
        :type cache: int
        :rtype Movie|Program
        """
        detail = None
        if cache in [CACHE_AUTO, CACHE_ONLY]:
            detail = kodiutils.get_cache(['detail', detail_id])
            if detail is None and cache == CACHE_ONLY:
                return None

        if not detail:
            detail = self._get_detail_json(detail_id)
            kodiutils.set_cache(['detail', detail_id], detail)

        if detail.get('seasonPicker') is None:
            return self._parse_movie_detail(detail)

        return self._parse_program_detail(detail_id, detail)

    def get_movie(self, movie_id, cache=CACHE_AUTO):
        """ Get the details of the specified movie.

        :type movie_id: str
        :type cache: int
        :rtype Movie
        """
        detail = self.get_detail(movie_id, cache=cache)
        return detail if isinstance(detail, Movie) else None

    def get_program(self, program_id, cache=CACHE_AUTO):
        """ Get the details of the specified program.

        :type program_id: str
        :type cache: int
        :rtype Program
        """
        detail = self.get_detail(program_id, cache=cache)
        return detail if isinstance(detail, Program) else None

    def _get_detail_json(self, detail_id, season_index=None):
        """ Fetch the raw json of a detail page, optionally for a specific season. """
        url = API_ENDPOINT + '/%s/detail3/%s' % (self._mode(), detail_id)
        if season_index is not None:
            url += '?selectedSeasonIndex=%s' % season_index
        response = util.http_get(url, token=self._tokens.access_token, profile=self._tokens.profile)
        return json.loads(response.text)

    @staticmethod
    def _parse_year(detail):
        """ Return the production year from the header labels, if there is one. """
        for label in detail.get('headerLabels') or []:
            text = (label.get('label') or '').strip()
            if len(text) == 4 and text.isdigit():
                return int(text)
        return None

    def _parse_movie_detail(self, movie):
        """ Parse a detail page of a movie. """
        return Movie(
            movie_id=movie.get('id'),
            playable_id=(movie.get('primaryButton') or {}).get('playableId'),
            name=(movie.get('title') or {}).get('label'),
            description=movie.get('description'),
            duration=movie.get('durationSeconds'),
            thumb=movie.get('landscapeTeaserImageUrl'),
            fanart=movie.get('backgroundImageUrl'),
            year=self._parse_year(movie),
            my_list=movie.get('addedToMyList'),
            available=bool((movie.get('primaryButton') or {}).get('playableId')),
        )

    def _parse_program_detail(self, program_id, program):
        """ Parse a detail page of a program, fetching every season. """
        name = (program.get('title') or {}).get('label')
        picker = program.get('seasonPicker') or {}
        selected = picker.get('selected') or {}

        seasons = {}
        for season_index in picker.get('indices', []):
            if season_index == selected.get('index'):
                season = selected
            else:
                season = (self._get_detail_json(program_id, season_index).get('seasonPicker') or {}).get('selected') or {}

            episodes = {}
            for item_episode in season.get('episodes', []):
                progress = item_episode.get('userProgressPercentage') or 0
                duration = item_episode.get('durationSeconds') or 0
                episodes[item_episode.get('index')] = Episode(
                    episode_id=item_episode.get('id'),
                    program_id=program_id,
                    program_name=name,
                    number=item_episode.get('index'),
                    season=season_index,
                    name=self._strip_episode_number(item_episode.get('title')),
                    description=item_episode.get('description'),
                    duration=duration,
                    thumb=item_episode.get('imageUrl'),
                    fanart=item_episode.get('imageUrl'),
                    progress=int(duration * progress / 100) if progress < 100 else 0,
                    watched=progress >= 100,
                    available=not item_episode.get('blockingOverlayId'),
                )

            seasons[season_index] = Season(
                number=season_index,
                episodes=episodes,
            )

        return Program(
            program_id=program.get('id'),
            name=name,
            description=program.get('description'),
            thumb=program.get('landscapeTeaserImageUrl'),
            fanart=program.get('backgroundImageUrl'),
            seasons=seasons,
            my_list=program.get('addedToMyList'),
        )

    @staticmethod
    def _strip_episode_number(title):
        """ Episode titles look like "1. Title", remove the number since Kodi shows it already. """
        if title and '. ' in title and title.split('. ', 1)[0].isdigit():
            return title.split('. ', 1)[1]
        return title

    @staticmethod
    def get_episode_from_program(program, episode_id):
        """ Extract the specified episode from the program data.
        :type program: Program
        :type episode_id: str
        :rtype Episode
        """
        for season in list(program.seasons.values()):
            for episode in list(season.episodes.values()):
                if episode.episode_id == episode_id:
                    return episode

        return None

    @staticmethod
    def get_next_episode_from_program(program, season, number):
        """ Search for the next episode in the program data.
        :type program: Program
        :type season: int
        :type number: int
        :rtype Episode
        """
        next_season_episode = None

        # First, try to find a match in the current season
        for episode in [e for s in list(program.seasons.values()) for e in list(s.episodes.values())]:
            if episode.season == season and episode.number == number + 1:
                return episode
            if episode.season == season + 1 and episode.number == 1:
                next_season_episode = episode

        # No match, use the first episode of next season
        if next_season_episode:
            return next_season_episode

        # We are playing the last episode
        return None

    def get_episode(self, episode_id):
        """ Get some details of the specified episode.
        :type episode_id: str
        :rtype Episode
        """
        response = util.http_get(API_ENDPOINT + '/%s/play/%s' % (self._mode(), episode_id),
                                 token=self._tokens.access_token,
                                 profile=self._tokens.profile)
        episode = json.loads(response.text)

        # Extract next episode info if available
        next_playable = episode.get('nextPlayable')
        if next_playable:
            next_episode = Episode(
                episode_id=next_playable['id'],
                program_name=next_playable['title'],
                name=next_playable['subtitle'],
                description=next_playable['description'],
                poster=next_playable['imageUrl'],
            )
        else:
            next_episode = None

        return Episode(
            episode_id=episode.get('id'),
            name=episode.get('title'),
            poster=episode.get('posterImageUrl'),
            progress=episode.get('playerPositionSeconds'),
            next_episode=next_episode,
        )

    def do_search(self, search):
        """ Do a search in the full catalog.
        :type search: str
        :rtype list[Teaser]
        """
        response = util.http_get(API_ENDPOINT + '/%s/search?query=%s' % (self._mode(),
                                                                         kodiutils.to_unicode(quote(kodiutils.from_unicode(search)))),
                                 token=self._tokens.access_token,
                                 profile=self._tokens.profile)
        results = json.loads(response.text)

        items = []
        for category in results.get('results', []):
            items.extend(self._parse_teaser(item) for item in category.get('teasers', []))
        return [item for item in items if item]

    def _parse_teaser(self, item, cache=CACHE_ONLY):
        """ Parse a teaser. When the detail page is cached we know if it is a Movie or a Program,
        otherwise we return a Teaser that resolves the type when opened. Teasers that point to a
        playable episode (like in "Continue watching") are returned as an Episode.

        :type item: dict
        :type cache: int
        :rtype Movie|Program|Episode|Teaser
        """
        detail_id = item.get('detailId') or (item.get('target') or {}).get('id')
        if not detail_id:
            return None

        name = item.get('title')
        thumb = item.get('imageUrl') or item.get('landscapeImageUrl') or item.get('largeImageUrl')
        fanart = item.get('heroImageUrl') or thumb

        if item.get('playableId'):
            progress = item.get('userProgressPercentage') or 0
            return Episode(
                episode_id=item.get('playableId'),
                program_id=detail_id,
                program_name=name,
                name=item.get('seasonLabel') or name,
                description=item.get('description'),
                thumb=thumb,
                fanart=fanart,
                watched=progress >= 100,
            )

        detail = self.get_detail(detail_id, cache=cache)
        if detail:
            return detail

        return Teaser(
            detail_id=detail_id,
            name=name,
            description=item.get('description'),
            poster=item.get('portraitImageUrl'),
            thumb=thumb,
            fanart=fanart,
            my_list=item.get('addedToMyList'),
        )

    @staticmethod
    def _parse_channel(url):
        """ Parse the channel logo url, and return an icon that matches resource.images.studios.white
        :type url: str
        :rtype str
        """
        if not url:
            return None

        import os.path

        # The channels id's we use in resources.lib.modules.CHANNELS neatly matches this part in the url.
        return str(os.path.basename(url).split('-')[0])
