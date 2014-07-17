# -*- coding: utf-8 -*-


"""Test helpers"""


import imaplib
from imap_cli import config, read, status
from mock import Mock
import unittest


class HelpersTest(unittest.TestCase):
    def setUp(self):
        self.ctx = config.new_context_from_file('~/.config/imap-cli')

        imaplib.IMAP4_SSL = Mock()
        imap_connection = imaplib.IMAP4_SSL('localhost')
        imap_connection.fetch = Mock(return_value=('OK', [('1 (RFC822 {2323}', "EMAIL CONTENT"), ')']))
        imap_connection.list = Mock(
            return_value=('OK', ['(\\HasNoChildren) "." "Directory_name"', '(\\HasNoChildren) "." "INBOX"'])
        )
        imap_connection.login = Mock(return_value=('OK', ['Logged in']))
        imap_connection.select = Mock(return_value=('OK', ['1']))
        imap_connection.status(return_value=('OK', ['"Directory_name" (MESSAGES 1 RECENT 1 UNSEEN 0)']))

    def test_read(self):
        self.ctx.mail_account = imaplib.IMAP4_SSL()
        self.ctx.mail_account.login()

        mail = read.read(self.ctx, 1, directory="INBOX")
        assert mail == "EMAIL CONTENT"

    def test_status(self):
        self.ctx.mail_account = imaplib.IMAP4_SSL()
        self.ctx.mail_account.login()

        directories_status = list(status.status(self.ctx))
        assert directories_status == [
            {'directory': "Directory_name", 'unseen': "0", 'count': "1", 'recent': "1"},
            {'directory': "Directory_name", 'unseen': "0", 'count': "1", 'recent': "1"},
        ]
