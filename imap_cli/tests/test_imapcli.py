# -*- coding: utf-8 -*-


"""Test helpers"""


import imaplib
import unittest

import imap_cli
from imap_cli import tests


class ImapCLITest(unittest.TestCase):
    def setUp(self):
        imaplib.IMAP4 = tests.ImapConnectionMock()
        imaplib.IMAP4_SSL = tests.ImapConnectionMock()

    def test_change_dir(self):
        self.imap_account = imaplib.IMAP4_SSL()
        self.imap_account.login()

        imap_cli.change_dir(self.imap_account, 'Test')

    def test_change_dir_twice(self):
        self.imap_account = imaplib.IMAP4_SSL()
        self.imap_account.login()

        assert imap_cli.change_dir(self.imap_account, 'Test') == '1'
        assert imap_cli.change_dir(self.imap_account, 'INBOX') == '1'

    def test_connect(self):
        self.imap_account = imap_cli.connect('hostname', 'username',
                                             'password')
        assert isinstance(self.imap_account, tests.ImapConnectionMock)

    def test_connect_no_ssl(self):
        self.imap_account = imap_cli.connect('hostname', 'username',
                                             'password', ssl=False)
        assert isinstance(self.imap_account, tests.ImapConnectionMock)

    def test_wrong_change_dir(self):
        self.imap_account = imaplib.IMAP4_SSL()
        self.imap_account.login()

        assert imap_cli.change_dir(self.imap_account, 'NotADirectory') == -1

    def test_disconnect(self):
        self.imap_account = imaplib.IMAP4_SSL()
        self.imap_account.login()

        imap_cli.disconnect(self.imap_account)
        assert self.imap_account.state == 'LOGOUT'

    def test_disconnect_selected_state(self):
        self.imap_account = imaplib.IMAP4_SSL()
        self.imap_account.login()

        imap_cli.change_dir(self.imap_account, 'Test')
        imap_cli.disconnect(self.imap_account)
        assert self.imap_account.state == 'LOGOUT'
