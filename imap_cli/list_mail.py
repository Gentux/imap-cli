# -*- coding: utf-8 -*-


"""Functions returning an IMAP account state

Usage: imap-cli-list [options] [<directory>]

Options:
    -c, --config-file=<FILE>    Configuration file (`~/.config/imap-cli` by
                                default)
    -f, --format=<FMT>          Output format
    -l, --limit=<limit>         Limit number of mail displayed
    -t, --thread                Display mail by thread
    -v, --verbose               Generate verbose messages
    -h, --help                  Show help options.
    --version                   Print program version.

    Format of the format string <FMT>
        The follwing placeholders are replaced by their values:
        {uid}, {flags}, {from}, {to}, {date}, {subject}

---
imap-cli-list 0.7
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
    args = docopt.docopt('\n'.join(__doc__.split('\n')[2:]),
                         version=const.VERSION)
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.INFO,
        stream=sys.stdout,
    )

    connect_conf = config.new_context_from_file(args['--config-file'],
                                                section='imap')
    if connect_conf is None:
        return 1
    display_conf = config.new_context_from_file(args['--config-file'],
                                                section='display')
    if args['--format'] is not None:
        config_key = 'format_thread' if args['--thread'] else 'format_list'
        display_conf[config_key] = args['--format']
    if args['--limit'] is not None:
        try:
            limit = int(args['--limit'])
            if limit < 1:
                raise ValueError
        except ValueError:
            log.error('Invalid argument limit : {}'.format(args['--limit']))
            return 1
    else:
        limit = None

    try:
        imap_account = imap_cli.connect(**connect_conf)
        imap_cli.change_dir(
            imap_account,
            directory=args['<directory>'] or const.DEFAULT_DIRECTORY)
        if args['--thread'] is False:
            for mail_info in search.fetch_mails_info(imap_account,
                                                     limit=limit):
                sys.stdout.write(
                    display_conf['format_list'].format(**mail_info))
                sys.stdout.write('\n')
        else:
            threads = search.fetch_threads(imap_account, limit=limit)
            mail_tree = search.threads_to_mail_tree(threads)
            for output in search.display_mail_tree(
                    imap_account,
                    mail_tree,
                    format_thread=display_conf['format_thread']):
                sys.stdout.write(output)
                sys.stdout.write('\n')
        imap_cli.disconnect(imap_account)
    except KeyboardInterrupt:
        log.info('Interrupt by user, exiting')

    return 0


if __name__ == '__main__':
    sys.exit(main())
