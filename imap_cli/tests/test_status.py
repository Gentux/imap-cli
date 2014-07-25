# -*- coding: utf-8 -*-


"""Test helpers"""


import imaplib
import unittest

from imap_cli import config
from imap_cli import status
from imap_cli import tests


class StatusTest(unittest.TestCase):
    def setUp(self):
        self.ctx = config.new_context()
        imaplib.IMAP4_SSL = tests.ImapConnectionMock()

    def test_status(self):
        self.ctx.mail_account = imaplib.IMAP4_SSL()
        self.ctx.mail_account.login()

        for directory_status in status.status(self.ctx):
            assert directory_status == {'directory': "Directory_name", 'unseen': "0", 'count': "1", 'recent': "1"}
