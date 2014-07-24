# -*- coding: utf-8 -*-


"""Functions searching in IMAP account

Usage: imap-cli-search [options] [-t <tags>] [-T <full-text>] [<directory>]

Options:
    -c, --config-file=<FILE>    Configuration file (`~/.config/imap-cli` by default)
    -f, --format=<FMT>          Output format
    -t, --tags=<tags>           Searched tags (Comma separated values)
    -T, --full-text=<text>      Searched tags (Comma separated values)
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
import sys

import docopt

from imap_cli import config
from imap_cli import const
from imap_cli.imap import connection
from imap_cli.imap import search
from imap_cli import list_mail


log = logging.getLogger('imap-cli-list')


def prepare_search(ctx, directory=None, tags=None, text=None):
    if directory is None:
        directory = const.DEFAULT_DIRECTORY
    status, mail_count = ctx.mail_account.select(directory, True)
    if status != const.STATUS_OK:
        log.error('No such direcotory on IMAP account')
        return

    search_criterion = 'ALL'
    if tags is not None:
        search_criterion = [search.create_search_criteria_by_tag(tags)]

    if text is not None:
        search_criterion = [search.create_search_criteria_by_text(text)]

    return search_criterion


def main():
    args = docopt.docopt('\n'.join(__doc__.split('\n')[2:]))
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.WARNING,
        stream=sys.stdout,
    )

    ctx = config.new_context_from_file(args['--config-file'])
    if args['--format'] is not None:
        ctx.format_status = args['--format']
    if args.get('--tags') is not None:
        args['--tags'] = args['--tags'].split(',')

    connection.connect(ctx)

    search_criterion = prepare_search(ctx, directory=args['<directory>'], tags=args['--tags'], text=args['--full-text'])
    mail_set = search.search(ctx, search_criterion=search_criterion)
    for mail_info in list_mail.list_mail(ctx, directory=args['<directory>'], mail_set=mail_set):
        sys.stdout.write(ctx.format_list.format(**mail_info))
        sys.stdout.write('\n')

    connection.disconnect(ctx)
    return 0


if __name__ == '__main__':
    sys.exit(main())
