# -*- coding: utf-8 -*-


"""Set flags on a set of mails

Usage: list [options] [<directory>] <mail_id> <flag>...

    -c, --config-file=<FILE>    Configuration file (`~/.config/imap-cli` by default)
    -v, --verbose               Generate verbose messages
    -h, --help                  Show help options.
    --version                   Print program version.
----
imap-cli-flag 0.1.0
Copyright (C) 2014 Romain Soufflet
License MIT
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"""


from docopt import docopt
import logging
import sys

from imap_cli import config, const, helpers


log = logging.getLogger('imap-cli-flag')


def flag(ctx, mail_id, flags, directory=const.DEFAULT_DIRECTORY):
    status, mail_count = ctx.mail_account.select(directory)
    if status != 'OK':
        log.warn(u'Cannot access directory {}'.format(directory))
        return
    for flag in flags:
        helpers.flag(ctx, mail_id, r'({})'.format(flag))


def main():
    args = docopt('\n'.join(__doc__.split('\n')[2:]))
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.WARNING,
        stream=sys.stdout,
    )

    ctx = config.new_context_from_file(args['--config-file'])
    helpers.connect(ctx)
    flag(ctx, args['<mail_id>'], args['<flag>'], directory=args['<directory>'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
