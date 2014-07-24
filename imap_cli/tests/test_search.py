# -*- coding: utf-8 -*-


"""Test helpers"""


import imaplib
import unittest

from imap_cli import config
from imap_cli import imap
from imap_cli import search
from imap_cli import tests


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.ctx = config.new_context_from_file('config-example.ini')
        imaplib.IMAP4_SSL = tests.ImapConnectionMock()

    def test_basic_search(self):
        self.ctx.mail_account = imaplib.IMAP4_SSL()
        self.ctx.mail_account.login()

        assert search.prepare_search(self.ctx, directory='INBOX') == 'ALL'

    def test_prepare_search_by_tag(self):
        self.ctx.mail_account = imaplib.IMAP4_SSL()
        self.ctx.mail_account.login()

        tags = ['seen']
        search_criterion = search.prepare_search(self.ctx, directory='INBOX', tags=tags)
        assert search_criterion == ['SEEN']

        tags = ['testTag']
        search_criterion = search.prepare_search(self.ctx, directory='INBOX', tags=tags)
        assert search_criterion == ['KEYWORD "testTag"']

        tags = ['seen', 'testTag']
        search_criterion = search.prepare_search(self.ctx, directory='INBOX', tags=tags)
        assert search_criterion == ['(SEEN KEYWORD "testTag")']

    def test_prepare_search_by_text(self):
        self.ctx.mail_account = imaplib.IMAP4_SSL()
        self.ctx.mail_account.login()

        text = 'CONTENT'
        search_criterion = search.prepare_search(self.ctx, directory='INBOX', text=text)
        assert search_criterion == ['BODY "CONTENT"']

    def test_execute_simple_search(self):
        self.ctx.mail_account = imaplib.IMAP4_SSL()
        self.ctx.mail_account.login()

        assert imap.search.search(self.ctx) == ['1']
