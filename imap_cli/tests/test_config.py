# -*- coding: utf-8 -*-


"""Test config"""


import json
from os import SEEK_SET
from six.moves import configparser
from tempfile import NamedTemporaryFile
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


class SASLAuthConfigTest(unittest.TestCase):
    def setUp(self):
        self.config_file = NamedTemporaryFile('w+')
        self.config_file.write('[imap]\n')
        self.config_file.write('hostname = imap.example.org\n')
        self.config_file.write('username = username\n')
        self.config_file.write('ssl = True\n')

    def test_xoauth2_with_bearer_access_token(self):
        self.config_file.write('sasl_auth = XOAUTH2\n')
        self.config_file.write('bearer_access_token = 12345abcde\n')
        self.config_file.seek(SEEK_SET, 0)

        self.conf = config.new_context_from_file(self.config_file.name,
                                                 section='imap')
        assert self.conf['hostname'] == 'imap.example.org'
        assert self.conf['username'] == 'username'
        assert self.conf['sasl_auth'] == 'XOAUTH2'
        assert self.conf['sasl_ir'] == \
            'user=username\x01auth=Bearer 12345abcde\x01\x01'

    def test_xoauth2_with_initial_response(self):
        self.config_file.write('sasl_auth = XOAUTH2\n')
        self.config_file.write('sasl_ir = 12345abcde\x01\n')
        self.config_file.seek(SEEK_SET, 0)

        self.conf = config.new_context_from_file(self.config_file.name,
                                                 section='imap')
        assert self.conf['hostname'] == 'imap.example.org'
        assert self.conf['username'] == 'username'
        assert self.conf['sasl_auth'] == 'XOAUTH2'
        assert self.conf['sasl_ir'] == '12345abcde\x01'

    def test_other_sasl_auth_with_initial_response(self):
        self.config_file.write('sasl_auth = OAUTHBEARER\n')
        self.config_file.write('sasl_ir = 12345abcde\n')
        self.config_file.seek(SEEK_SET, 0)

        self.conf = config.new_context_from_file(self.config_file.name,
                                                 section='imap')
        assert self.conf['hostname'] == 'imap.example.org'
        assert self.conf['username'] == 'username'
        assert self.conf['sasl_auth'] == 'OAUTHBEARER'
        assert self.conf['sasl_ir'] == '12345abcde'

    def test_sasl_auth_no_initial_response(self):
        self.config_file.write('sasl_auth = XOAUTH2\n')
        self.config_file.seek(SEEK_SET, 0)

        self.assertRaises(configparser.NoOptionError,
                          config.new_context_from_file,
                          self.config_file.name,
                          section='imap')

    def tearDown(self):
        self.config_file.close()
