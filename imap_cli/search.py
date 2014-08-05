# -*- coding: utf-8 -*-


"""Functions searching in IMAP account

Usage: imap-cli-search [options] [-t <tags>] [-T <full-text>] [<directory>]

Options:
    -c, --config-file=<FILE>    Configuration file (`~/.config/imap-cli` by default)
    -f, --format=<FMT>          Output format
    -t, --tags=<tags>           Searched tags (Comma separated values)
    -T, --full-text=<text>      Searched tags (Comma separated values)
    -v, --verbose               Generate verbose messages
    -h, --help                  Show help options.
    --version                   Print program version.

----
imap-cli-status 0.3
Copyright (C) 2014 Romain Soufflet
License MIT
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"""


import email
from email import header
import logging
import re
import sys

import docopt
import six

import imap_cli
from imap_cli import config
from imap_cli import const
from imap_cli import fetch


log = logging.getLogger('imap-cli-list')

FLAGS_RE = r'.*FLAGS \((?P<flags>[^\)]*)\)'
MAIL_ID_RE = r'^(?P<mail_id>\d+) \('
UID_RE = r'.*UID (?P<uid>[^ ]*)'


def create_search_criteria_by_text(text):
    """Return a search criteria for fulltext search."""
    return 'BODY "{}"'.format(text)


def create_search_criteria_by_tag(tags):
    """Return a search criteria for specified tags."""
    if len(tags) == 0:
        return ''

    criterion = []
    for tag in tags:
        if tag.upper() in const.IMAP_SPECIAL_FLAGS:
            criterion.append(tag.upper())
        else:
            criterion.append('KEYWORD "{}"'.format(tag))
    return '({})'.format(' '.join(criterion)) if len(criterion) > 1 else criterion[0]


def fetch_mails_info(imap_account, mail_set=None, decode=True, limit=None):
    flags_re = re.compile(FLAGS_RE)
    mail_id_re = re.compile(MAIL_ID_RE)
    uid_re = re.compile(UID_RE)

    if mail_set is None:
        mail_set = fetch_uids(imap_account, limit=limit)
    elif isinstance(mail_set, six.string_types):
        mail_set = mail_set.split()

    mails_data = fetch.fetch(imap_account, mail_set, ['BODY.PEEK[HEADER]', 'FLAGS', 'UID'])
    if mails_data is None:
        return

    for mail_data in mails_data:
        flags_match = flags_re.match(mail_data[0])
        mail_id_match = mail_id_re.match(mail_data[0])
        uid_match = uid_re.match(mail_data[0])
        if mail_id_match is None or flags_match is None or uid_match is None:
            continue

        flags = flags_match.groupdict().get('flags').split()
        mail_id = mail_id_match.groupdict().get('mail_id').split()
        mail_uid = uid_match.groupdict().get('uid').split()

        mail = email.message_from_string(mail_data[1])
        if decode is True:
            for header_name, header_value in mail.items():
                header_new_value = []
                for value, encoding in header.decode_header(header_value):
                    header_new_value.append(value.decode(encoding or 'utf-8'))
                mail.replace_header(header_name, ' '.join(header_new_value))

        yield dict([
            ('flags', flags),
            ('id', mail_id),
            ('uid', mail_uid),
            ('mail_from', mail['from']),
            ('to', mail['to']),
            ('date', mail['date']),
            ('subject', mail.get('subject', '')),
        ])


def create_search_criterion(tags=None, text=None):
    search_criterion = ['ALL']
    if tags is not None:
        search_criterion = [create_search_criteria_by_tag(tags)]

    if text is not None:
        search_criterion = [create_search_criteria_by_text(text)]

    return search_criterion


def fetch_uids(imap_account, charset=None, limit=None, search_criterion=None):
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

    if imap_account.state != 'SELECTED':
        log.warning(u'No directory specified, selecting {}'.format(const.DEFAULT_DIRECTORY))
        imap_cli.change_dir(imap_account, const.DEFAULT_DIRECTORY)

    status, data = imap_account.uid('SEARCH', charset, request_search_criterion)
    if status == const.STATUS_OK:
        return data[0].split() if limit is None else data[0].split()[-limit:]


def main():
    args = docopt.docopt('\n'.join(__doc__.split('\n')[2:]))
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.WARNING,
        stream=sys.stdout,
    )

    connect_conf = config.new_context_from_file(args['--config-file'], section='imap')
    display_conf = config.new_context_from_file(args['--config-file'], section='display')
    if args['--format'] is not None:
        display_conf['format_status'] = args['--format']
    if args.get('--tags') is not None:
        args['--tags'] = args['--tags'].split(',')

    imap_account = imap_cli.connect(**connect_conf)
    imap_cli.change_dir(imap_account, directory=args['<directory>'] or const.DEFAULT_DIRECTORY)
    search_criterion = create_search_criterion(
        tags=args['--tags'],
        text=args['--full-text'],
    )
    mail_set = fetch_uids(imap_account, search_criterion=search_criterion)
    for mail_info in fetch_mails_info(imap_account, directory=args['<directory>'], mail_set=mail_set):
        sys.stdout.write(display_conf['format_list'].format(**mail_info))
        sys.stdout.write('\n')

    imap_cli.disconnect(imap_account)
    return 0


if __name__ == '__main__':
    sys.exit(main())
