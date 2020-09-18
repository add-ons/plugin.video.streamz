# -*- coding: utf-8 -*-
""" Tests for Routing """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from resources.lib import addon, kodiutils

routing = addon.routing  # pylint: disable=invalid-name


@unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
class TestRouting(unittest.TestCase):
    """ Tests for Routing """

    def __init__(self, *args, **kwargs):
        super(TestRouting, self).__init__(*args, **kwargs)

    def test_main_menu(self):
        routing.run([routing.url_for(addon.show_main_menu), '0', ''])


if __name__ == '__main__':
    unittest.main()
