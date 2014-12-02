# -*- coding: utf-8 -*-


"""Test helpers"""


import imaplib
import sys
import unittest

from imap_cli import const
from imap_cli import summary
from imap_cli import tests


class FetchTest(unittest.TestCase):
    def setUp(self):
        imaplib.IMAP4_SSL = tests.ImapConnectionMock()

    def test_status_command(self):
        const.DEFAULT_CONFIG_FILE = 'config-example.ini'

        sys.argv = ['imap-cli-status']
        assert summary.main() == 0

        sys.argv = ['imap-cli-status', '--config-file=config-example.ini']
        assert summary.main() == 0

        sys.argv = ['imap-cli-status',
                    '--config-file=config-imaginary-file.ini']
        assert summary.main() == 1

        sys.argv = ['imap-cli-status', '--format=\"{directory:>10} {unseen}\"']
        assert summary.main() == 0

        sys.argv = ['imap-cli-status', '-v']
        assert summary.main() == 0
