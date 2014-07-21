# -*- coding: utf-8 -*-


"""Functions searching in IMAP account

Usage: search [options] [-t <tags>] [-T <full-text>] [<directory>]

    -c, --config-file=<FILE>    Configuration file (`~/.config/imap-cli` by default)
    -f, --format=<FMT>          Output format
    -l, --limit=<limit>         Limit number of mail displayed
    -t, --tags=<tags>           Searched tags (Comma separated values)
    -T, --full-text=<text>      Searched tags (Comma separated values)
    -v, --verbose               Generate verbose messages
    -h, --help                  Show help options.
    --version                   Print program version.
----
imap-cli-status 0.1.0
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
from imap_cli import helpers
from imap_cli import list_mail


log = logging.getLogger('imap-cli-list')


def search(ctx, directory=None, tags=None, text=None):
    if directory is None:
        directory = const.DEFAULT_DIRECTORY
    status, mail_count = ctx.mail_account.select(directory, True)
    if status != 'OK':
        log.error('No such direcotory on IMAP account')
        return
    search_criterion = 'ALL'
    if tags is not None:
        tags = list(tag if tag.upper() not in const.IMAP_SPECIAL_FLAGS else tag.upper() for tag in tags)
        search_criterion = '(KEYWORD "{}")'.format(' '.join(tags))

    if text is not None:
        search_criterion = '(BODY "{}")'.format(text)

    for result in helpers.list_mail(ctx, search_criterion=search_criterion):
        yield result


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

    helpers.connect(ctx)
    mail_set = search(ctx, directory=args['<directory>'], tags=args['--tags'], text=args['--full-text'])
    for mail_info in list_mail.list_mail(ctx, directory=args['<directory>'], mail_set=mail_set):
        sys.stdout.write(ctx.format_list.format(**mail_info))
        sys.stdout.write('\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
