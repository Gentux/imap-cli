# -*- coding: utf-8 -*-


"""Test config"""


import unittest

from imap_cli import config


class HelpersTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_config_file_from_example_config_file(self):
        config_example_filename = 'config-example.ini'
        self.ctx = config.new_context_from_file(config_example_filename)

        assert self.ctx.hostname == 'imap.example.org'
        assert self.ctx.username == 'username'
        assert self.ctx.password == 'secret'
        assert self.ctx.ssl is True

        assert self.ctx.limit == 10
        assert self.ctx.format_list == "".join([
            "\n",
            "ID:         {mail_id}\n",
            "Flags:      {flags}\n",
            "From:       {mail_from}\n",
            "To:         {to}\n",
            "Date:       {date}\n",
            "Subject:    {subject}",
        ])
        assert self.ctx.format_status == "{directory:>20} : {count:>5} Mails - {unseen:>5} Unseen - {recent:>5} Recent"
