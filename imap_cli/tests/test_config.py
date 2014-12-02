# -*- coding: utf-8 -*-


"""Test config"""


import json
import unittest

from imap_cli import config
from imap_cli import const


class ConfigTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_default_config(self):
        self.conf = config.new_context()

        for key, value in config.DEFAULT_CONFIG.items():
            assert self.conf[key] == value

    def test_config_file_from_example_config_file(self):
        config_example_filename = 'config-example.ini'
        self.conf = config.new_context_from_file(config_example_filename)

        for key, value in config.DEFAULT_CONFIG.items():
            assert self.conf[key] == value

    def test_config_file_from_default_config_file(self):
        const.DEFAULT_CONFIG_FILE = 'config-example.ini'

        self.conf = config.new_context_from_file()

        if self.conf is not None:
            for key, value in config.DEFAULT_CONFIG.items():
                self.assertEqual(self.conf[key], value)

    def test_config_file_from_non_existing_file(self):
        const.DEFAULT_CONFIG_FILE = 'config-imaginary-file.ini'

        self.conf = config.new_context_from_file()

        if self.conf is not None:
            for key, value in config.DEFAULT_CONFIG.items():
                assert self.conf[key] == value

    def test_config_file_from_json(self):
        json_config = ''.join([
            '{"username": "username", "hostname": "imap.example.org", ',
            '"format_list": "\\nID:         {uid}\\nFlags:      ',
            '{flags}\\nFrom:       {from}\\nTo:         {to}\\nDate:       ',
            '{date}\\nSubject:    {subject}", "ssl": true, "limit": 10, ',
            '"format_status": "{directory:>20} : {count:>5} Mails - ',
            '{unseen:>5} Unseen - {recent:>5} Recent", "password": "secret"}',
        ])
        self.conf = config.new_context(json.loads(json_config))

        for key, value in config.DEFAULT_CONFIG.items():
            assert self.conf[key] == value
