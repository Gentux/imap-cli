# -*- coding: utf-8 -*-


"""Set flags on a set of mails

Usage: imap-cli-flag [options] [<directory>] <mail_id> <flag>...

Options:
    -c, --config-file=<FILE>    Configuration file
    -v, --verbose               Generate verbose messages
    -h, --help                  Show help options.
    --version                   Print program version.

----
imap-cli-flag 0.2
Copyright (C) 2014 Romain Soufflet
License MIT
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"""


import logging
import sys

import docopt

from imap_cli import config
from imap_cli import const
from imap_cli.imap import connection
from imap_cli.imap import flag as imap_flag


log = logging.getLogger('imap-cli-flag')


def flag(ctx, mail_id, flags, directory=const.DEFAULT_DIRECTORY):
    status, mail_count = ctx.mail_account.select(directory)
    if status != const.STATUS_OK:
        log.warn(u'Cannot access directory {}'.format(directory))
        return
    for flag in flags:
        imap_flag.flag(ctx, mail_id, r'({})'.format(flag))


def main():
    args = docopt.docopt('\n'.join(__doc__.split('\n')[2:]))
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.WARNING,
        stream=sys.stdout,
    )

    ctx = config.new_context_from_file(args['--config-file'])
    connection.connect(ctx)
    flag(ctx, args['<mail_id>'], args['<flag>'], directory=args['<directory>'])
    connection.disconnect(ctx)
    return 0


if __name__ == '__main__':
    sys.exit(main())
