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

        statuses = list(imap_cli.status(self.imap_account))
        for directory_status in statuses:
            assert directory_status == {'directory': u'Δiπectòrÿ_ñämé',
                                        'unseen': "0",
                                        'count': "1", 'recent': "1"}
        assert len(statuses) == 2

    def test_status_with_wrong_imap_call(self):
        # TODO(rsoufflet) This test doesn't seem to be pass
        self.imap_account = imaplib.IMAP4_SSL()
        self.imap_account.fail = True

        for directory_status in imap_cli.status(self.imap_account):
            assert directory_status == {'directory': u'Δiπectòrÿ_ñämé',
                                        'unseen': "0", 'count': "1",
                                        'recent': "1"}

    def test_status_with_error_imap_response(self):
        self.imap_account = imaplib.IMAP4_SSL()
        self.imap_account.error = True

        statuses = list(imap_cli.status(self.imap_account))
        for directory_status in statuses:
            assert directory_status == {'directory': u'Δiπectòrÿ_ñämé',
                                        'unseen': "0", 'count': "1",
                                        'recent': "1"}
        assert len(statuses) == 0
