# -*- coding: utf-8 -*-


"""IMAP lib connect and disconnect helpers"""


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
