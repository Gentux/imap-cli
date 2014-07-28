# -*- coding: utf-8 -*-


"""IMAP lib fetch helpers"""


import collections
import logging
import os

from imap_cli import const


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)


def fetch(ctx, message_set=None, message_parts=None):
    """Return mails corresponding to mails_id.

    Keyword arguments:
    message_set     -- Iterable containing mails ID (integers)
    message_parts   -- Iterable of message part names or IMAP protocoles ENVELOP string

    Avalable message_parts are listed in const.MESSAGE_PARTS, for more information checkout RFC3501
    """
    if message_set is None or not isinstance(message_set, collections.Iterable):
        log.error('Can\'t fetch email {}'.format(message_set))
        return None
    if message_parts is None:
        message_parts = ['RFC822']

    request_message_set = ','.join(str(mail_id) for mail_id in message_set)
    request_message_parts = '({})'.format(' '.join(message_parts)
                                          if isinstance(message_parts, collections.Iterable)
                                          else message_parts)
    typ, data = ctx.mail_account.uid('FETCH', request_message_set, request_message_parts)
    if typ == const.STATUS_OK:
        return data
