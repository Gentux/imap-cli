# -*- coding: utf-8 -*-


"""Helpers using IMAP lib to get IMAP informations"""


import imaplib
import logging
import os


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)


def connect(ctx):
    if ctx.ssl is True:
        log.debug('Connecting with SSL on {}'.format(ctx.hostname))
        ctx.mail_account = imaplib.IMAP4_SSL(ctx.hostname, 993)
    else:
        log.debug('Connecting on {}'.format(ctx.hostname))
        ctx.mail_account = imaplib.IMAP4(ctx.hostname)
    ctx.mail_account.login(ctx.username, ctx.password)


def disconnect(ctx):
    log.debug('Disconnecting from {}'.format(ctx.hostname))
    ctx.mail_account.close()
    ctx.mail_account.logout()


def list_dir(ctx):
    status, data = ctx.mail_account.list()
    if status == 'OK':
        for datum in data:
            parts = datum.split()
            yield parts[0], parts[1], parts[2]


def list_mail(ctx, search_criterion='ALL'):
#    typ, data = ctx.mail_account.search(None, 'ALL')
#    typ, data = ctx.mail_account.search(None, 'ANSWERED')
#    typ, data = ctx.mail_account.search(None, 'UNSEEN')
#    typ, data = ctx.mail_account.search(None, 'UNREAD')
#    typ, data = ctx.mail_account.search(None, 'SEEN')
    typ, data = ctx.mail_account.search(None, search_criterion)
    for num in data[0].split():
        yield num


def fetch(ctx, mail_id=None):
    if mail_id is None:
        return 'KO', None
    typ, data = ctx.mail_account.fetch(mail_id, '(RFC822)')
    if typ == 'OK':
        return data
    else:
        return None
