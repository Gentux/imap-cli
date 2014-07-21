# -*- coding: utf-8 -*-


"""Test config"""


import unittest

from imap_cli import config


class HelpersTest(unittest.TestCase):
    def setUp(self):
        self.config_filename = 'config-example.ini'

    def test_config_file(self):
        self.ctx = config.new_context_from_file(self.config_filename)

        assert self.ctx.hostname == 'imap.example.org'
        assert self.ctx.username == 'username'
        assert self.ctx.password == 'secret'
        assert self.ctx.ssl is True

        assert self.ctx.limit == 10
        assert self.ctx.format_status == ("\n",
                                          "ID:         {mail_id}\n",
                                          "Flags:      {flags}\n",
                                          "From:       {mail_from}\n",
                                          "To:         {to}\n",
                                          "Date:       {date}\n",
                                          "Subjetc:    {subject}",
                                          )
        assert self.ctx.format_status == "{directory:>20} : {count:>5} Mails - {unseen:>5} Unseen - {recent:>5} Recent"
