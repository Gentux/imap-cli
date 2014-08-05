# -*- coding: utf-8 -*-


"""Test helpers"""


import imaplib
import unittest

import imap_cli
from imap_cli import tests


class StatusTest(unittest.TestCase):
    def setUp(self):
        imaplib.IMAP4_SSL = tests.ImapConnectionMock()

    def test_status(self):
        self.imap_account = imaplib.IMAP4_SSL()
        self.imap_account.login()

        for directory_status in imap_cli.status(self.imap_account):
            assert directory_status == {'directory': "Directory_name", 'unseen': "0", 'count': "1", 'recent': "1"}
