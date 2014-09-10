# -*- coding: utf-8 -*-


"""Test helpers"""


import imaplib
import sys
import unittest

from imap_cli import const
from imap_cli import list_mail
from imap_cli import tests


class ListMailTests(unittest.TestCase):
    def setUp(self):
        imaplib.IMAP4_SSL = tests.ImapConnectionMock()

    def test_list_command(self):
        const.DEFAULT_CONFIG_FILE = 'config-example.ini'

        sys.argv = ['imap-cli-list']
        assert list_mail.main() == 0

        sys.argv = ['imap-cli-list', '--config-file=config-example.ini']
        assert list_mail.main() == 0

        sys.argv = ['imap-cli-list', '--config-file=config-imaginary-file.ini']
        assert list_mail.main() == 1

        sys.argv = ['imap-cli-list', '--format="{from} -> {to}"']
        assert list_mail.main() == 0

        sys.argv = ['imap-cli-list', '-l', '2']
        assert list_mail.main() == 0

        sys.argv = ['imap-cli-list', '-l', 'a']
        assert list_mail.main() == 1

        sys.argv = ['imap-cli-list', '-l', '0']
        assert list_mail.main() == 1

        sys.argv = ['imap-cli-list', '-v']
        assert list_mail.main() == 0

        sys.argv = ['imap-cli-list', '--thread']
        assert list_mail.main() == 0
