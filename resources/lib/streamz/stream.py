# -*- coding: utf-8 -*-
""" Streamz Stream API """

from __future__ import absolute_import, division, unicode_literals

import json
import logging

from resources.lib.streamz import ResolvedStream, util, API_ENDPOINT
from resources.lib.streamz.exceptions import StreamGeoblockedException, StreamUnavailableException

_LOGGER = logging.getLogger(__name__)


class Stream:
    """ Streamz Stream API """

    _API_KEY = 'zs06SrhsKN2fEQvDdTMDR2t6wYwfceQu5HAmGa0p'
    _ANVATO_USER_AGENT = 'ANVSDK Android/5.0.39 (Linux; Android 6.0.1; Nexus 5)'

    def __init__(self, auth):
        """ Initialise object """
        self._auth = auth
        self._tokens = self._auth.login()

    def get_stream(self, stream_type, stream_id):
        """ Return a ResolvedStream based on the stream type and id.
        :type stream_type: str
        :type stream_id: str
        :rtype ResolvedStream
        """
        # We begin with asking the api about the stream info.
        stream_tokens = self._get_stream_tokens(stream_type, stream_id)
        player_token = stream_tokens.get('playerToken')

        # Return video information
        video_info = self._get_video_info(stream_type, stream_id, player_token)

        # Extract the anvato stream from our stream_info.
        stream_info = self._extract_stream_from_video_info('dash', video_info)

        # Send heartbeat
        # We might need to do this to keep the session active, see video_info.get('heartbeat', {}).get('expiry')
        self._send_heartbeat(video_info.get('heartbeat', {}).get('token'), video_info.get('heartbeat', {}).get('correlationId'))

        # Get published urls.
        url = stream_info.get('url')
        license_url = stream_info.get('drm', {}).get('com.widevine.alpha', {}).get('licenseUrl')

        # Extract subtitles from our video_info.
        # subtitles = self._extract_subtitles_from_stream_info(video_info)
        # TODO: add subtitles, but it seems that some are burned in the video

        if stream_type == 'episodes':
            return ResolvedStream(
                program=video_info['video']['metadata']['program']['title'],
                program_id=video_info['video']['metadata']['program']['id'],
                title=video_info['video']['metadata']['title'],
                duration=video_info['video']['duration'],
                url=url,
                # subtitles=subtitles,
                license_url=license_url,
            )

        if stream_type == 'movies':
            return ResolvedStream(
                program=None,
                title=video_info['video']['metadata']['title'],
                duration=video_info['video']['duration'],
                url=url,
                # subtitles=subtitles,
                license_url=license_url,
            )

        raise Exception('Unknown video type {type}'.format(type=stream_type))

    def _get_stream_tokens(self, strtype, stream_id):
        """ Get the stream info for the specified stream.
        :type strtype: str
        :type stream_id: str
        :rtype: dict
        """

        if strtype == 'movies':
            url = API_ENDPOINT + '/streamz/play/movie/%s' % stream_id
        elif strtype == 'episodes':
            url = API_ENDPOINT + '/streamz/play/episode/%s' % stream_id
        else:
            raise Exception('Unknown stream type: %s' % strtype)

        _LOGGER.debug('Getting stream info from %s', url)
        response = util.http_get(url, token=self._tokens.jwt_token, profile=self._tokens.profile)

        _LOGGER.debug('Got response (status=%s): %s', response.status_code, response.text)

        # TODO: handle errors
        # if response.status_code == 403:
        #     error = json.loads(response.text)
        #     if error['type'] == 'videoPlaybackGeoblocked':
        #         raise StreamGeoblockedException()
        #     if error['type'] == 'serviceError':
        #         raise StreamUnavailableException()

        if response.status_code == 404:
            raise StreamUnavailableException()

        if response.status_code != 200:
            raise StreamUnavailableException()

        return json.loads(response.text)

    def _get_video_info(self, strtype, stream_id, player_token):
        """ Get the stream info for the specified stream.
        :type strtype: str
        :type stream_id: str
        :type player_token: str
        :rtype: dict
        """
        url = 'https://videoplayer-service.api.persgroep.cloud/config/%s/%s' % (strtype, stream_id)
        _LOGGER.debug('Getting stream info from %s', url)
        response = util.http_get(url,
                                 params={
                                     'startPosition': '0.0',
                                     'autoPlay': 'true',
                                 },
                                 headers={
                                     'Accept': 'application/json',
                                     'x-api-key': self._API_KEY,
                                     # 'x-dpg-correlation-id': '',
                                     'Popcorn-SDK-Version': '4',
                                     'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; MotoG3 Build/MPIS24.107-55-2-17)',
                                     'Authorization': 'Bearer ' + player_token,
                                 })

        _LOGGER.debug('Got response (status=%s): %s', response.status_code, response.text)

        if response.status_code == 403:
            error = json.loads(response.text)
            if error['type'] == 'videoPlaybackGeoblocked':
                raise StreamGeoblockedException()
            if error['type'] == 'serviceError':
                raise StreamUnavailableException()

        if response.status_code == 404:
            raise StreamUnavailableException()

        if response.status_code != 200:
            raise StreamUnavailableException()

        info = json.loads(response.text)
        return info

    def _send_heartbeat(self, token, correlation_id):
        """ Notify the service we will start playing.
        :type token: str
        :type correlation_id: str
        :rtype: dict
        """
        url = 'https://videoplayer-service.api.persgroep.cloud/config/heartbeat'
        _LOGGER.debug('Sending heartbeat to %s', url)
        response = util.http_put(url,
                                 data={
                                     'token': token,
                                 },
                                 headers={
                                     'Accept': 'application/json',
                                     'Content-Type': 'application/json',
                                     'x-api-key': self._API_KEY,
                                     'x-dpg-correlation-id': correlation_id,
                                     'Popcorn-SDK-Version': '4',
                                     'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; MotoG3 Build/MPIS24.107-55-2-17)',
                                 })

        _LOGGER.debug('Got response (status=%s): %s', response.status_code, response.text)

        if response.status_code != 204:
            raise StreamUnavailableException()

    @staticmethod
    def _extract_stream_from_video_info(stream_type, stream_info):
        """ Extract the anvato stream details.
        :type stream_info: dict
        :rtype dict
        """
        # Loop over available streams, and return the one from anvato
        if stream_info.get('video'):
            for stream in stream_info.get('video').get('streams'):
                if stream.get('type') == stream_type:
                    return stream
        elif stream_info.get('code'):
            _LOGGER.error('Streamz Videoplayer service API error: %s', stream_info.get('type'))
        raise Exception('No stream found that we can handle')

    @staticmethod
    def _extract_subtitles_from_stream_info(stream_info):
        """ Extract a list of the subtitles.
        :type stream_info: dict
        :rtype list[dict]
        """
        subtitles = list()
        if stream_info.get('video').get('subtitles'):
            for idx, subtitle in enumerate(stream_info.get('video').get('subtitles')):
                program = stream_info.get('video').get('metadata').get('program')
                if program:
                    name = '{} - {}_{}'.format(program.get('title'), stream_info.get('video').get('metadata').get('title'), idx)
                else:
                    name = '{}_{}'.format(stream_info.get('video').get('metadata').get('title'), idx)
                subtitles.append(dict(name=name, url=subtitle.get('url')))
                _LOGGER.debug('Found subtitle url %s', subtitle.get('url'))
        return subtitles

    @staticmethod
    def create_license_key(key_url, key_type='R', key_headers=None, key_value=None):
        """ Create a license key string that we need for inputstream.adaptive.
        :type key_url: str
        :type key_type: str
        :type key_headers: dict[str, str]
        :type key_value: str
        :rtype str
        """
        try:  # Python 3
            from urllib.parse import urlencode, quote
        except ImportError:  # Python 2
            from urllib import urlencode, quote

        header = ''
        if key_headers:
            header = urlencode(key_headers)

        if key_type in ('A', 'R', 'B'):
            key_value = key_type + '{SSM}'
        elif key_type == 'D':
            if 'D{SSM}' not in key_value:
                raise ValueError('Missing D{SSM} placeholder')
            key_value = quote(key_value)

        return '%s|%s|%s|' % (key_url, header, key_value)
