# -*- coding: utf-8 -*-


"""Test flag module"""


import imaplib
import sys
import unittest

from imap_cli import const
from imap_cli import flag
from imap_cli import tests


class FlagTests(unittest.TestCase):
    def setUp(self):
        imaplib.IMAP4_SSL = tests.ImapConnectionMock()

    def test_flag_cli_tools(self):
        const.DEFAULT_CONFIG_FILE = 'config-example.ini'

        sys.argv = ['imap-cli-flag', '-c', 'config-example.ini', '1',
                    'testFlag']
        assert flag.main() == 0

        sys.argv = ['imap-cli-flag', '-u', '1', 'testFlag']
        assert flag.main() == 0
