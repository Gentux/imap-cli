# -*- coding: utf-8 -*-


"""IMAP lib helpers to manage directories"""


import logging
import os

from imap_cli import const


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)


def list_dir(ctx):
    status, data = ctx.mail_account.list()
    if status == const.STATUS_OK:
        for datum in data:
            parts = datum.split()
            yield parts[0], parts[1], parts[2]


def change_dir(ctx, directory, read_only=True):
    if ctx.mail_account.state == 'SELECTED':
        ctx.mail_account.close()
    status, mail_count = ctx.mail_account.select(directory, read_only)
    if status == const.STATUS_OK:
        return mail_count
    else:
        log.error('Can\'t select directory {}'.format(directory))
        return -1
