# -*- coding: utf-8 -*-


"""Functions returning an IMAP account state

Usage: imap-cli-status [options]

Options:
    -c, --config-file=<FILE>    Configuration file (`~/.config/imap-cli` by
                                default)
    -f, --format=<FMT>          Output format
    -v, --verbose               Generate verbose messages
    -h, --help                  Show help options.
    --version                   Print program version.

----
imap-cli-status 0.7
Copyright (C) 2014 Romain Soufflet
License MIT
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"""


import logging
import sys

import docopt
import six

import imap_cli
from imap_cli import config
from imap_cli import const


log = logging.getLogger('imap-cli-status')


def main():
    args = docopt.docopt('\n'.join(__doc__.split('\n')[2:]),
                         version=const.VERSION)
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.INFO,
        stream=sys.stdout,
    )

    try:
        connect_conf = config.new_context_from_file(args['--config-file'],
                                                    section='imap')
        if connect_conf is None:
            return 1
        display_conf = config.new_context_from_file(args['--config-file'],
                                                    section='display')
        if args['--format'] is not None:
            display_conf['format_status'] = six.text_type(args['--format'])

        imap_account = imap_cli.connect(**connect_conf)
        for directory_status in sorted(imap_cli.status(imap_account),
                                       key=lambda obj: obj['directory']):
            sys.stdout.write(
                display_conf['format_status'].format(**directory_status).encode('UTF-8'))
            sys.stdout.write('\n')
    except KeyboardInterrupt:
        log.info('Interrupt by user, exiting')

    return 0


if __name__ == '__main__':
    sys.exit(main())
