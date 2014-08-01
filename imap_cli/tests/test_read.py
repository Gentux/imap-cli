# -*- coding: utf-8 -*-


"""Test helpers"""


import imaplib
import unittest

from imap_cli import config
from imap_cli import fetch
from imap_cli import tests


class ReadTest(unittest.TestCase):
    def setUp(self):
        self.ctx = config.new_context()
        imaplib.IMAP4_SSL = tests.ImapConnectionMock()

    def test_read(self):
        self.ctx.mail_account = imaplib.IMAP4_SSL()
        self.ctx.mail_account.login()

        mail = fetch.read(self.ctx, 1, directory="INBOX")
        reference_mail = {
            u'headers': {
                u'From': u'exampleFrom <example@from.org>',
                u'Content-Transfer-Encoding': u'quoted-printable',
                u'To': u'exampleTo <example@to.org>',
                u'Date': u'Tue, 03 Jan 1989 09:42:34 +0200',
                u'Subject': u'Mocking IMAP Protocols',
                u'Content-Type': u'text/html;\r\n\tcharset="windows-1252"',
                u'MIME-Version': u'1.0'
            },
            u'parts': [
                {
                    u'data': '\n'.join([
                        u'From: exampleFrom <example@from.org>',
                        u'Date: Tue, 03 Jan 1989 09:42:34 +0200',
                        u'Subject: Mocking IMAP Protocols',
                        u'To: exampleTo <example@to.org>',
                        u'MIME-Version: 1.0',
                        u'Content-Type: text/html;',
                        u'\tcharset="windows-1252"',
                        u'Content-Transfer-Encoding: quoted-printable',
                        u'',
                        u'EMAIL BODY CONTENT',
                    ]),
                    u'content_type': 'text/html'
                }
            ]
        }

        for header_name, header_value in mail['headers'].items():
            assert reference_mail['headers'][header_name] == header_value
        assert len(mail['parts']) == len(reference_mail['parts'])
