# -*- coding: utf-8 -*-


"""Test helpers"""


import datetime
import imaplib
import sys
import unittest

from imap_cli import search
from imap_cli import tests


class SearchTests(unittest.TestCase):
    def setUp(self):
        imaplib.IMAP4_SSL = tests.ImapConnectionMock()

    def test_basic_search(self):
        self.imap_account = imaplib.IMAP4_SSL()

        assert search.create_search_criterion() == ['ALL']

    def test_combine_search_criterion(self):
        self.imap_account = imaplib.IMAP4_SSL()

        date = datetime.datetime(1989, 1, 3)
        mail_address = 'user@example.tld'
        search_criterion = [
            search.create_search_criterion_by_date(date, relative='BEFORE'),
            search.create_search_criterion_by_mail_address(mail_address,
                                                           header_name='TO'),
        ]

        imap_request = search.combine_search_criterion(search_criterion)
        assert imap_request == '(BEFORE 03-Jan-1989 TO "user@example.tld")'

        imap_request = search.combine_search_criterion(search_criterion,
                                                       operator='AND')
        assert imap_request == '(BEFORE 03-Jan-1989 TO "user@example.tld")'

        imap_request = search.combine_search_criterion(search_criterion,
                                                       operator='OR')
        assert imap_request == 'OR BEFORE 03-Jan-1989 TO "user@example.tld"'

        imap_request = search.combine_search_criterion(search_criterion,
                                                       operator='NOT')
        assert imap_request == 'NOT BEFORE 03-Jan-1989 TO "user@example.tld"'

        imap_request = search.combine_search_criterion(search_criterion,
                                                       operator='WRONG')
        assert imap_request == '(BEFORE 03-Jan-1989 TO "user@example.tld")'

    def test_create_search_criteria_by_date(self):
        self.imap_account = imaplib.IMAP4_SSL()

        date = datetime.datetime(1989, 1, 3)
        search_criterion = search.create_search_criterion(date=date)
        assert search_criterion == ['SINCE 03-Jan-1989']

        search_criterion = search.create_search_criterion_by_date(
            date, relative='BEFORE')
        assert search_criterion == 'BEFORE 03-Jan-1989'

        search_criterion = search.create_search_criterion_by_date(
            date, relative='ON')
        assert search_criterion == 'ON 03-Jan-1989'

        search_criterion = search.create_search_criterion_by_date(
            date, relative='SINCE')
        assert search_criterion == 'SINCE 03-Jan-1989'

        search_criterion = search.create_search_criterion_by_date(
            date, relative='BEFORE', sent=True)
        assert search_criterion == 'SENTBEFORE 03-Jan-1989'

        search_criterion = search.create_search_criterion_by_date(
            date, relative='ON', sent=True)
        assert search_criterion == 'SENTON 03-Jan-1989'

        search_criterion = search.create_search_criterion_by_date(
            date, relative='SINCE', sent=True)
        assert search_criterion == 'SENTSINCE 03-Jan-1989'

    def test_create_search_criteria_by_header(self):
        self.imap_account = imaplib.IMAP4_SSL()

        search_criterion = search.create_search_criterion_by_header(
            "FROM", "user@example.tld")
        assert search_criterion == 'HEADER FROM user@example.tld'

    def test_create_search_criterion_by_mail_address(self):
        self.imap_account = imaplib.IMAP4_SSL()

        mail_address = 'user@example.tld'
        search_criterion = search.create_search_criterion(address=mail_address)
        assert search_criterion == ['FROM "user@example.tld"']

        search_criterion = search.create_search_criterion_by_mail_address(
            mail_address, header_name='WRONG')
        assert search_criterion == 'FROM "user@example.tld"'

        search_criterion = search.create_search_criterion_by_mail_address(
            mail_address, header_name='CC')
        assert search_criterion == 'CC "user@example.tld"'

        search_criterion = search.create_search_criterion_by_mail_address(
            mail_address, header_name='BCC')
        assert search_criterion == 'BCC "user@example.tld"'

        search_criterion = search.create_search_criterion_by_mail_address(
            mail_address, header_name='TO')
        assert search_criterion == 'TO "user@example.tld"'

    def test_create_search_criteria_by_size(self):
        self.imap_account = imaplib.IMAP4_SSL()

        size = 3141592
        search_criterion = search.create_search_criterion(size=size)
        assert search_criterion == ['LARGER "3141592"']

        search_criterion = search.create_search_criterion_by_size(
            size, relative='SMALLER')
        assert search_criterion == 'SMALLER "3141592"'

        search_criterion = search.create_search_criterion_by_size(
            size, relative='LARGER')
        assert search_criterion == 'LARGER "3141592"'

        search_criterion = search.create_search_criterion_by_size(
            size, relative='Anything')
        assert search_criterion == 'LARGER "3141592"'

    def test_create_search_criterion_by_subject(self):
        self.imap_account = imaplib.IMAP4_SSL()

        subject = 'subject searched'
        search_criterion = search.create_search_criterion(subject=subject)
        assert search_criterion == ['SUBJECT "subject searched"']

        search_criterion = search.create_search_criterion_by_subject(subject)
        assert search_criterion == 'SUBJECT "subject searched"'

    def test_create_search_criteria_by_tag(self):
        self.imap_account = imaplib.IMAP4_SSL()

        tags = ['seen']
        search_criterion = search.create_search_criterion(tags=tags)
        assert search_criterion == ['SEEN']

        tags = ['testTag']
        search_criterion = search.create_search_criterion(tags=tags)
        assert search_criterion == ['KEYWORD "testTag"']

        tags = ['seen', 'testTag']
        search_criterion = search.create_search_criterion(tags=tags)
        assert search_criterion == ['(SEEN KEYWORD "testTag")']

        tags = []
        search_criterion = search.create_search_criterion(tags=tags)
        assert search_criterion == ['']

    def test_create_search_criteria_by_text(self):
        self.imap_account = imaplib.IMAP4_SSL()

        text = 'CONTENT'
        search_criterion = search.create_search_criterion(text=text)
        assert search_criterion == ['BODY "CONTENT"']

    def test_create_search_criteria_by_uid(self):
        self.imap_account = imaplib.IMAP4_SSL()

        uid = 42
        search_criterion = search.create_search_criterion_by_uid(uid)
        assert search_criterion == 'UID 42'

    def test_display_empty_mail_tree(self):
        self.imap_account = imaplib.IMAP4_SSL()
        assert list(search.display_mail_tree(self.imap_account, [])) == []

    def test_execute_simple_search(self):
        self.imap_account = imaplib.IMAP4_SSL()

        assert search.fetch_uids(self.imap_account) == ['1']

    def test_fetch_mails_info(self):
        self.imap_account = imaplib.IMAP4_SSL()

        reference_mails_info = [{
            'from': u'exampleFrom <example@from.org>',
            'to': u'exampleTo <example@to.org>',
            'subject': u'Mocking IMAP Protocols',
            'id': u'1',
            'flags': [u'\\Seen', u'NonJunk'],
            'date': u'Tue, 03 Jan 1989 09:42:34 +0200',
            'uid': u'1',
        }]
        assert list(search.fetch_mails_info(
            self.imap_account)) == reference_mails_info
        assert list(search.fetch_mails_info(
            self.imap_account, mail_set="42 24")) == reference_mails_info

        self.imap_account.error = True
        assert list(search.fetch_mails_info(self.imap_account)) == []

    def test_fetch_uids(self):
        self.imap_account = imaplib.IMAP4_SSL()

        assert list(search.fetch_uids(self.imap_account)) == ['1']

    def test_fetch_threads(self):
        self.imap_account = imaplib.IMAP4_SSL()

        assert list(search.fetch_threads(self.imap_account)) == [[[1], [2]],
                                                                 [3, 4]]
        threads = search.fetch_threads(
            self.imap_account,
            search_criterion=['BODY "CONTENT"'],
        )
        assert list(threads) == [[[1], [2]], [3, 4]]

    def test_search_cli_tools(self):
        sys.argv = ['imap-cli-search', '-c', 'config-example.ini']
        assert search.main() == 0

        sys.argv = ['imap-cli-search', '--thread', '-c', 'wrong-config.ini']
        assert search.main() == 1

        sys.argv = ['imap-cli-search', '--thread', '-c', 'config-example.ini']
        assert search.main() == 0

        sys.argv = ['imap-cli-search', '-t testTag -T testText', '-c',
                    'config-example.ini']
        assert search.main() == 0

        sys.argv = ['imap-cli-search', '-t testTag,test2Tag -T testText', '-c',
                    'config-example.ini']
        assert search.main() == 0

        sys.argv = ['imap-cli-search', '-d', '2014-03-13', '-c',
                    'config-example.ini']
        assert search.main() == 0

        sys.argv = ['imap-cli-search', '-d', '201403-13', '-c',
                    'config-example.ini']
        assert search.main() == 0

        sys.argv = ['imap-cli-search', '-a', 'user@exemple.org']
        assert search.main() == 0

        sys.argv = ['imap-cli-search', '-f', '{from}']
        assert search.main() == 0

        sys.argv = ['imap-cli-search', '-l', '10']
        assert search.main() == 0

        sys.argv = ['imap-cli-search', '-l', '0']
        assert search.main() == 1
