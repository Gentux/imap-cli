# -*- coding: utf-8 -*-


"""Helpers using IMAP lib to get IMAP informations"""


import imaplib
import logging
import os

from imap_cli import const


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


def fetch(ctx, mail_id=None):
    if mail_id is not None:
        typ, data = ctx.mail_account.fetch(mail_id, '(RFC822)')
        if typ == const.STATUS_OK:
            return data
    log.error('Can\'t fetch email {}'.format(mail_id))
    return None


def list_dir(ctx):
    status, data = ctx.mail_account.list()
    if status == const.STATUS_OK:
        for datum in data:
            parts = datum.split()
            yield parts[0], parts[1], parts[2]


def list_mail(ctx, limit=None, search_criterion='ALL'):
#    typ, data = ctx.mail_account.search(None, 'ALL')
#    typ, data = ctx.mail_account.search(None, 'ANSWERED')
#    typ, data = ctx.mail_account.search(None, 'UNSEEN')
#    typ, data = ctx.mail_account.search(None, 'UNREAD')
#    typ, data = ctx.mail_account.search(None, 'SEEN')
    typ, data = ctx.mail_account.search(None, search_criterion)
    return data[0].split() if limit is None else data[0].split()[-limit:]
