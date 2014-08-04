# -*- coding: utf-8 -*-


"""IMAP basic helpers"""


import imaplib
import logging
import os
import re

from imap_cli import const


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)

STATUS_RE = r'{dirname} \({messages_count} {recent} {unseen}\)'.format(
    dirname=r'"(?P<dirname>.*)"',
    messages_count=r'MESSAGES (?P<mail_count>\d{1,5})',
    recent=r'RECENT (?P<mail_recent>\d{1,5})',
    unseen=r'UNSEEN (?P<mail_unseen>\d{1,5})',
)


def change_dir(ctx, directory, read_only=True):
    if ctx.mail_account.state == 'SELECTED':
        ctx.mail_account.close()
    status, mail_count = ctx.mail_account.select(directory, read_only)
    if status == const.STATUS_OK:
        return mail_count
    else:
        log.error('Can\'t select directory {}'.format(directory))
        return -1


def connect(ctx):
    if ctx.port is None:
        ctx.port = const.DEFAULT_PORT if ctx.ssl is False else const.DEFAULT_SSL_PORT

    if ctx.ssl is True:
        log.debug('Connecting with SSL on {}'.format(ctx.hostname))
        ctx.mail_account = imaplib.IMAP4_SSL(ctx.hostname, ctx.port)
    else:
        log.debug('Connecting on {}'.format(ctx.hostname))
        ctx.mail_account = imaplib.IMAP4(ctx.hostname, ctx.port)
    ctx.mail_account.login(ctx.username, ctx.password)


def disconnect(ctx):
    log.debug('Disconnecting from {}'.format(ctx.hostname))
    ctx.mail_account.close()
    ctx.mail_account.logout()


def list_dir(ctx):
    status, data = ctx.mail_account.list()
    if status == const.STATUS_OK:
        for datum in data:
            parts = datum.split()
            yield parts[0], parts[1], parts[2]


def status(ctx):
    status_cre = re.compile(STATUS_RE)
    for tags, delimiter, dirname in list_dir(ctx):
        status, data = ctx.mail_account.status(dirname, '(MESSAGES RECENT UNSEEN)')
        if status != const.STATUS_OK:
            continue
        status_match = status_cre.match(data[0])
        if status_match is not None:
            group_dict = status_match.groupdict()
            yield {
                'directory': group_dict['dirname'],
                'unseen': group_dict['mail_unseen'],
                'count': group_dict['mail_count'],
                'recent': group_dict['mail_recent'],
            }
