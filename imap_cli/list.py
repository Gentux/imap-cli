# -*- coding: utf-8 -*-


"""Functions returning an IMAP account state

Usage: list [options] [<directory>]

    -c, --config-file=<FILE>    Configuration file (`~/.config/imap-cli` by default)
    -f, --format=<FMT>          Output format
    -l, --limit=<limit>         Limit number of mail displayed
    -v, --verbose               Generate verbose messages
    -h, --help                  Show help options.
    --version                   Print program version.
----
imap-cli-status 0.1.0
Copyright (C) 2014 Romain Soufflet
License MIT
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"""


import email
import logging
import re
import sys

import docopt

from imap_cli import config
from imap_cli import const
from imap_cli import helpers


log = logging.getLogger('imap-cli-list')

FLAGS_RE = r'^{mail_id} \(FLAGS \({flags}'.format(
    mail_id=r'(?P<mail_id>\d+)',
    flags=r'(?P<flags>[^\)]*)',
)


def list(ctx, directory=None):
    if directory is None:
        directory = const.DEFAULT_DIRECTORY
    flags_re = re.compile(FLAGS_RE)
    status, mail_count = ctx.mail_account.select(directory, True)
    if status != 'OK':
        log.warn(u'Cannot access directory {}'.format(directory))
        return

    for mail_id in helpers.list_mail(ctx, limit=ctx.limit):
        status, mail_data = ctx.mail_account.fetch(mail_id, '(BODY.PEEK[HEADER] FLAGS)')
        if status != 'OK':
            log.error(u'Error fetching mail {}'.format(mail_id))
            continue
        flag_match = flags_re.match(mail_data[0][0])
        mail = email.message_from_string(mail_data[0][1])
        flags = flag_match.groupdict().get('flags').split()
        yield {
            'flags': flags,
            'mail_id': mail_id,
            'mail_from': mail['from'],
            'to': mail['to'],
            'date': mail['date'],
            'subject': mail.get('subject', '').decode('utf-8'),
        }


def main():
    args = docopt.docopt('\n'.join(__doc__.split('\n')[2:]))
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.WARNING,
        stream=sys.stdout,
    )

    ctx = config.new_context_from_file(args['--config-file'])
    if args['--format'] is not None:
        ctx.format_status = args['--format']

    helpers.connect(ctx)
    for mail_info in list(ctx, directory=args['<directory>']):
        sys.stdout.write(ctx.format_list.format(**mail_info))
        sys.stdout.write('\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
