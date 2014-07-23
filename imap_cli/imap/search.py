# -*- coding: utf-8 -*-


"""IMAP lib helpers to get list of mails"""


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


def list_mail(ctx, limit=None, search_criterion='ALL'):
    return search(ctx, limit=limit, search_criterion=search_criterion)


def create_search_criteria_by_text(text):
    """Return a search criteria for fulltext search."""
    return 'BODY "{}"'.format(text)


def create_search_criteria_by_tag(tags):
    """Return a search criteria for specified tags."""
    tags = list(
        tag
        if tag.upper() not in const.IMAP_SPECIAL_FLAGS
        else tag.upper()
        for tag in tags
    )
    return 'KEYWORD "{}"'.format(' '.join(tags))


def search(ctx, charset=None, limit=None, search_criterion=None):
    """Return a list of mails id corresponding to specified search.

    Keyword arguments:
    charset             -- Request a particular charset from IMAP server
    limit               -- Limit the number of mail returned
    search_criterion    -- Iterable containing criterion

    Search criterion avalaible are listed in const.SEARH_CRITERION
    """
    request_search_criterion = search_criterion
    if search_criterion is None:
        request_search_criterion = 'ALL'
    else:
        request_search_criterion = '({})'.format(' '.join(search_criterion))

    status, data = ctx.mail_account.search(charset, request_search_criterion)
    if status == const.STATUS_OK:
        return data[0].split() if limit is None else data[0].split()[-limit:]
