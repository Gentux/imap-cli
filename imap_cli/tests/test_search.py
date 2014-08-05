# -*- coding: utf-8 -*-


"""Test helpers"""


import imaplib
import unittest

from imap_cli import search
from imap_cli import tests


class SearchTests(unittest.TestCase):
    def setUp(self):
        imaplib.IMAP4_SSL = tests.ImapConnectionMock()

    def test_basic_search(self):
        self.imap_account = imaplib.IMAP4_SSL()
        self.imap_account.login()

        assert search.create_search_criterion() == ['ALL']

    def test_prepare_search_by_tag(self):
        self.imap_account = imaplib.IMAP4_SSL()
        self.imap_account.login()

        tags = ['seen']
        search_criterion = search.create_search_criterion(tags=tags)
        assert search_criterion == ['SEEN']

        tags = ['testTag']
        search_criterion = search.create_search_criterion(tags=tags)
        assert search_criterion == ['KEYWORD "testTag"']

        tags = ['seen', 'testTag']
        search_criterion = search.create_search_criterion(tags=tags)
        assert search_criterion == ['(SEEN KEYWORD "testTag")']

    def test_prepare_search_by_text(self):
        self.imap_account = imaplib.IMAP4_SSL()
        self.imap_account.login()

        text = 'CONTENT'
        search_criterion = search.create_search_criterion(text=text)
        assert search_criterion == ['BODY "CONTENT"']

    def test_execute_simple_search(self):
        self.imap_account = imaplib.IMAP4_SSL()
        self.imap_account.login()

        assert search.fetch_uids(self.imap_account) == ['1']
