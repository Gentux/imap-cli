# -*- coding: utf-8 -*-


"""Functions returning an IMAP account state

Usage: imap-cli-list [options] [<directory>]

Options:
    -c, --config-file=<FILE>    Configuration file (`~/.config/imap-cli` by default)
    -f, --format=<FMT>          Output format
    -l, --limit=<limit>         Limit number of mail displayed
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

from imap_cli import config
from imap_cli import const
from imap_cli.imap import connection
from imap_cli.imap import fetch
from imap_cli.imap import search


log = logging.getLogger('imap-cli-list')

FLAGS_RE = r'^{mail_id} \(FLAGS \({flags}'.format(
    mail_id=r'(?P<mail_id>\d+)',
    flags=r'(?P<flags>[^\)]*)',
)


def list_mail(ctx, directory=None, mail_set=None):
    if directory is None:
        directory = const.DEFAULT_DIRECTORY
    flags_re = re.compile(FLAGS_RE)
    status, mail_count = ctx.mail_account.select(directory, True)
    if status != const.STATUS_OK:
        log.warn(u'Cannot access directory {}'.format(directory))
        return

    if mail_set is None:
        mail_set = search.search(ctx, limit=ctx.limit)
    elif isinstance(mail_set, six.string_types):
        mail_set = mail_set.split()

    mails_data = fetch.fetch(ctx, mail_set, ['BODY.PEEK[HEADER]', 'FLAGS'])
    if mails_data is None:
        return

    for mail_data in mails_data:
        flag_match = flags_re.match(mail_data[0])
        if flag_match is None:
            continue

        mail = email.message_from_string(mail_data[1])
        flags = flag_match.groupdict().get('flags').split()
        mail_id = flag_match.groupdict().get('mail_id').split()

        yield dict([
            ('flags', flags),
            ('mail_id', mail_id),
            ('mail_from', mail['from']),
            ('to', mail['to']),
            ('date', mail['date']),
            ('subject', mail.get('subject', '')),
        ])


def main():
    args = docopt.docopt('\n'.join(__doc__.split('\n')[2:]))
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.WARNING,
        stream=sys.stdout,
    )

    ctx = config.new_context_from_file(args['--config-file'])
    if args['--format'] is not None:
        ctx.format_status = args['--format']
    if args['--limit'] is not None:
        try:
            ctx.limit = int(args['--limit'])
        except ValueError:
            pass

    connection.connect(ctx)
    for mail_info in list_mail(ctx, directory=args['<directory>']):
        printable_mail_info = dict(map(lambda t: (t[0], header.decode_header(t[1])[0][0]), mail_info.iteritems()))
        sys.stdout.write(ctx.format_list.format(**printable_mail_info))
        sys.stdout.write('\n')
    connection.disconnect(ctx)
    return 0


if __name__ == '__main__':
    sys.exit(main())
