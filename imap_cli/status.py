# -*- coding: utf-8 -*-


"""Functions returning an IMAP account state

Usage: imap-cli-status [options]

Options:
    -c, --config-file=<FILE>    Configuration file (`~/.config/imap-cli` by default)
    -f, --format=<FMT>          Output format
    -v, --verbose               Generate verbose messages
    -h, --help                  Show help options.
    --version                   Print program version.

----
imap-cli-status 0.2
Copyright (C) 2014 Romain Soufflet
License MIT
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"""


import logging
import re
import sys

import docopt

from imap_cli import config
from imap_cli import const
from imap_cli.imap import connection
from imap_cli.imap import search


log = logging.getLogger('imap-cli-status')

STATUS_RE = r'{dirname} \({messages_count} {recent} {unseen}\)'.format(
    dirname=r'"(?P<dirname>.*)"',
    messages_count=r'MESSAGES (?P<mail_count>\d{1,5})',
    recent=r'RECENT (?P<mail_recent>\d{1,5})',
    unseen=r'UNSEEN (?P<mail_unseen>\d{1,5})',
)


def status(ctx):
    status_cre = re.compile(STATUS_RE)
    for tags, delimiter, dirname in search.list_dir(ctx):
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


def main():
    args = docopt.docopt('\n'.join(__doc__.split('\n')[2:]))
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.WARNING,
        stream=sys.stdout,
    )

    ctx = config.new_context_from_file(args['--config-file'])
    if args['--format'] is not None:
        ctx.format_status = args['--format']

    connection.connect(ctx)
    for directory_info in status(ctx):
        sys.stdout.write(ctx.format_status.format(**directory_info))
        sys.stdout.write('\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
