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


def flag(ctx, mail_id=None, flags_str=''):
    if mail_id is None:
        log.error('Can\'t set flag on email {}'.format(mail_id))
        return None
    # TODO(rsoufflet)
    truc = ctx.mail_account.store(mail_id, '+FLAGS', flags_str)
    log.debug(repr(truc))


def list_dir(ctx):
    status, data = ctx.mail_account.list()
    if status == const.STATUS_OK:
        for datum in data:
            parts = datum.split()
            yield parts[0], parts[1], parts[2]


def list_mail(ctx, limit=None, search_criterion='ALL'):
    """
    <sequence set>
    ALL
    ANSWERED
    BCC <string>
    BEFORE <date>
    BODY <string>
    CC <string>
    DELETED
    DRAFT
    FLAGGED
    FROM <string>
    HEADER <field-name> <string>
    KEYWORD <flag>
    LARGER <n>
    NEW
    NOT <search-key>
    OLD
    ON <date>
    OR <search-key1> <search-key2>
    RECENT
    SEEN
    SENTBEFORE <date>
    SENTON <date>
    SENTSINCE <date>
    SINCE <date>
    SMALLER <n>
    SUBJECT <string>
    TEXT <string>
    TO <string>
    UID <sequence set>
    UNANSWERED
    UNDELETED
    UNDRAFT
    UNFLAGGED
    UNKEYWORD <flag>
    UNSEEN

    Example:    C: A282 SEARCH FLAGGED SINCE 1-Feb-1994 NOT FROM "Smith"
                S: * SEARCH 2 84 882
                S: A282 OK SEARCH completed
                C: A283 SEARCH TEXT "string not in mailbox"
                S: * SEARCH
                S: A283 OK SEARCH completed
                C: A284 SEARCH CHARSET UTF-8 TEXT {6}
                C: XXXXXX
                S: * SEARCH 43
                S: A284 OK SEARCH completed

         Note: Since this document is restricted to 7-bit ASCII
         text, it is not possible to show actual UTF-8 data.  The
         "XXXXXX" is a placeholder for what would be 6 octets of
         8-bit data in an actual transaction.
    """
    typ, data = ctx.mail_account.search(None, search_criterion)
    return data[0].split() if limit is None else data[0].split()[-limit:]
