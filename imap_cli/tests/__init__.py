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
    fail = False
    error = False
    state = None

    def fetch(self, mails_id_set, request):
        flag_str = ""
        if request.find('FLAG') >= 0:
            flag_str = u'FLAGS (\\Seen NonJunk) '
        uid_str = ""
        if self.error is True:
            uid_str = u'UD 1 '
        elif request.find('UID') >= 0:
            uid_str = u'UID 1 '

        imap_header = u'1 ({uid_str}{flag_str}BODY[HEADER] {{1621}}'.format(
            flag_str=flag_str, uid_str=uid_str)
        return (u'OK', [(imap_header, example_email_content), ')'])

    def store(self, mails_id_set, request, flags):
        flags = [u'\\\\Answered', u'\\\\Seen', 'NonJunk']
        if '+FLAGS' in request:
            flags.append('testFlag')
        return (u'OK', [u'1 (UID 1 FLAGS ({}))'.format(' '.join(flags))])

    def list(self, *args):
        if self.fail is True:
            return (u'OK', [(
                u'(\\HasNoChildren) ) "." '
                u'"&A5Q-i&A8A-ect&API-r&AP8-_&APEA5A-m&AOk-"'),
                u'(\\HasNoChildren) "." "INBOX"'])
        return (u'OK', [(
            u'(\\HasNoChildren) "." '
            u'"&A5Q-i&A8A-ect&API-r&AP8-_&APEA5A-m&AOk-"'),
            u'(\\HasNoChildren) "." "INBOX"'])

    def login(self, *args):
        return (u'OK', [u'Logged in'])

    def logout(self, *args):
        self.state = 'LOGOUT'

    def select(self, *args):
        if args[0] not in ['INBOX', 'Test', u'Δiπectòrÿ_ñämé']:
            self.state = 'LOGOUT'
            return (u'NO', None)
        self.state = 'SELECTED'
        return (u'OK', [u'1'])

    def search(self, *args):
        return (u'OK', [u'1'])

    def status(self, *args):
        if self.fail is True:
            return (u'NO', None)
        if self.error is True:
            return (u'OK', [(u'"&A5Q-i&A8A-ect&API-r&AP8-_&APEA5A-m&AOk-" '
                             u'((MESSAGES 1 RECENT 1 UNSEEN 0)')])
        return (u'OK', [(u'"&A5Q-i&A8A-ect&API-r&AP8-_&APEA5A-m&AOk-" '
                         u'(MESSAGES 1 RECENT 1 UNSEEN 0)')])

    def uid(self, command, *args):
        command_upper = command.upper()
        if command_upper == 'FETCH':
            return self.fetch(*args)
        if command_upper == 'SEARCH':
            return self.search(*args)
        if command_upper == 'STORE':
            return self.store(*args)
        if command_upper == 'THREAD':
            return self.thread(*args)

    def thread(self, *args):
        return (u'OK', [u'((1)(2))(3 4)'])
