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
imap-cli-status 0.4
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
from imap_cli import const
from imap_cli import search


log = logging.getLogger('imap-cli-list')


def main():
    args = docopt.docopt('\n'.join(__doc__.split('\n')[2:]))
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.INFO,
        stream=sys.stdout,
    )

    connect_conf = config.new_context_from_file(args['--config-file'], section='imap')
    if connect_conf is None:
        return 1
    display_conf = config.new_context_from_file(args['--config-file'], section='display')
    if args['--format'] is not None:
        display_conf['format_status'] = args['--format']
    if args['--limit'] is not None:
        try:
            display_conf['limit'] = int(args['--limit'])
        except ValueError:
            pass

    try:
        imap_account = imap_cli.connect(**connect_conf)
        imap_cli.change_dir(imap_account, directory=args['<directory>'] or const.DEFAULT_DIRECTORY)
        for mail_info in search.fetch_mails_info(imap_account):
            sys.stdout.write(display_conf['format_list'].format(**mail_info))
            sys.stdout.write('\n')
        imap_cli.disconnect(imap_account)
    except KeyboardInterrupt:
        log.info('Interrupt by user, exiting')

    return 0


if __name__ == '__main__':
    sys.exit(main())
