# -*- coding: utf-8 -*-


"""Test encoding helpers"""


import unittest

from imap_cli import string


class ImapUTF7Test(unittest.TestCase):
    encoded_string = (u'&AN8A7A-g '
                      u'T&AOo-st '
                      u'&A8kA7g-th spe&AOc-i&AOQ-l ch&AOIDwA-')
    decoded_string = u"ßìg Têst ωîth speçiäl châπ"

    def test_encode(self):
        assert string.decode(self.encoded_string) == self.decoded_string

    def test_decode(self):
        assert string.encode(self.decoded_string) == self.encoded_string
