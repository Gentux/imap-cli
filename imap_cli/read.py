# -*- coding: utf-8 -*-


"""Functions returning an IMAP account state

Usage: read [options] [<directory>] <mail_id>

    -c, --config-file=<FILE>    Configuration file (`~/.config/imap-cli` by default)
    -f, --format=<FMT>          Output format
    -v, --verbose               Generate verbose messages
    -h, --help                  Show help options.
    --version                   Print program version.
----
imap-cli-read 0.1.0
Copyright (C) 2014 Romain Soufflet
License MIT
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"""


import email
from email import header
import logging
import sys

import docopt

from imap_cli import config
from imap_cli import helpers


log = logging.getLogger('imap-cli-read')


def read(ctx, mail_id, directory=None):
    status, mail_count = ctx.mail_account.select(directory, True)
    return helpers.fetch(ctx, mail_id)[0][1]


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
    mail = email.message_from_string(read(ctx, args['<mail_id>'], directory=args['<directory>']))
    for header_name, header_value in mail.items():
        mail.replace_header(header_name, header.decode_header(header_value)[0][0])
    sys.stdout.write(mail.as_string())
    return 0

if __name__ == '__main__':
    sys.exit(main())
