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


log = logging.getLogger('imap-cli-status')


def truncate_string(string, length):
    minus_than_position = string.find('<')
    if minus_than_position > 0 and string.find('>') > minus_than_position:
        string = string[0:minus_than_position]
    return string if len(string) < length else u'{0}…'.format(string[0:length])


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

    imap_account = imap_cli.connect(**connect_conf)
    for directory_status in imap_cli.status(imap_account):
        sys.stdout.write(display_conf['format_status'].format(**directory_status))
        sys.stdout.write('\n')

    return 0


if __name__ == '__main__':
    sys.exit(main())
