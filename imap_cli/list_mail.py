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


import logging
import sys

import docopt

import imap_cli
from imap_cli import config
from imap_cli import search


log = logging.getLogger('imap-cli-list')


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

    imap_cli.connect(ctx)
    for mail_info in search.fetch_mails_info(ctx, directory=args['<directory>']):
        sys.stdout.write(ctx.format_list.format(**mail_info))
        sys.stdout.write('\n')
    imap_cli.disconnect(ctx)
    return 0


if __name__ == '__main__':
    sys.exit(main())
