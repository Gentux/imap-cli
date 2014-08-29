# -*- coding: utf-8 -*-


"""Imaplib IMAP4_SSL mocking class"""


import mock


example_email_content = u'\r\n'.join([
    u'From: exampleFrom <example@from.org>',
    u'Date: Tue, 03 Jan 1989 09:42:34 +0200',
    u'Subject: Mocking IMAP Protocols',
    u'To: exampleTo <example@to.org>',
    u'MIME-Version: 1.0',
    u'Content-Type: text/html;\r\n\tcharset="windows-1252"',
    u'Content-Transfer-Encoding: quoted-printable',
    u'',
    u'EMAIL BODY CONTENT',
])


class ImapConnectionMock(mock.Mock):
    state = None

    def fetch(self, mails_id_set, request):
        flag_str = ""
        if request.find('FLAG') >= 0:
            flag_str = u'FLAGS (\\Seen NonJunk) '
        uid_str = ""
        if request.find('UID') >= 0:
            uid_str = u'UID 1 '

        imap_header = u'1 ({uid_str}{flag_str}BODY[HEADER] {{1621}}'.format(flag_str=flag_str, uid_str=uid_str)
        return (u'OK', [(imap_header, example_email_content), ')'])

    def list(self, *args):
        return (u'OK', [u'(\\HasNoChildren) "." "Directory_name"', u'(\\HasNoChildren) "." "INBOX"'])

    def login(self, *args):
        return (u'OK', [u'Logged in'])

    def logout(self, *args):
        self.state = 'LOGOUT'

    def select(self, *args):
        if args[0] not in ['INBOX', 'Test', 'Directory_name']:
            self.state = 'LOGOUT'
            return (u'NO', None)
        self.state = 'SELECTED'
        return (u'OK', [u'1'])

    def search(self, *args):
        return (u'OK', [u'1'])

    def status(self, *args):
        return (u'OK', [u'"Directory_name" (MESSAGES 1 RECENT 1 UNSEEN 0)'])

    def uid(self, command, *args):
        command_upper = command.upper()
        if command_upper == 'FETCH':
            return self.fetch(*args)
        if command_upper == 'SEARCH':
            return self.search(*args)
