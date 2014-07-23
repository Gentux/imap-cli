# -*- coding: utf-8 -*-


"""Test helpers"""


import imaplib
import unittest

from imap_cli import config
from imap_cli import list_mail
from imap_cli import tests


class HelpersTest(unittest.TestCase):
    def setUp(self):
        self.ctx = config.new_context_from_file('config-example.ini')
        imaplib.IMAP4_SSL = tests.ImapConnectionMock()

    def test_basic_search(self):
        self.ctx.mail_account = imaplib.IMAP4_SSL()
        self.ctx.mail_account.login()
        for mail_info in list_mail.list_mail(self.ctx, directory='INBOX'):
            assert mail_info == {
                'date': 'Tue, 03 Jan 1989 09:42:34 +0200',
                'flags': ['\\Seen', 'NonJunk'],
                'mail_id': ['1'],
                'mail_from': 'exampleFrom <example@from.org>',
                'subject': u'Mocking IMAP Protocols',
                'to': 'exampleTo <example@to.org>',
            }
