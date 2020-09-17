# -*- coding: utf-8 -*-
""" Exceptions """

from __future__ import absolute_import, division, unicode_literals


class NotAvailableInOfferException(Exception):
    """ Is thrown when the requested item isn't available in your offer. """


class UnavailableException(Exception):
    """ Is thrown when an item is unavailable. """


class InvalidTokenException(Exception):
    """ Is thrown when the token is invalid. """


class InvalidLoginException(Exception):
    """ Is thrown when the credentials are invalid. """


class LoginErrorException(Exception):
    """ Is thrown when we could not login """

    def __init__(self, code):
        super(LoginErrorException, self).__init__()
        self.code = code


class ApiUpdateRequired(Exception):
    """ Is thrown when the an API update is required. """


class StreamGeoblockedException(Exception):
    """ Is thrown when a geoblocked item is played. """


class StreamUnavailableException(Exception):
    """ Is thrown when an unavailable item is played. """
