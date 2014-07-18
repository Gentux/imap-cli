# -*- coding: utf-8 -*-


"""Functions searching in IMAP account

Usage: search [options] [-t <tags>] [-H <headers>] [<directory>]

    -c, --config-file=<FILE>    Configuration file (`~/.config/imap-cli` by default)
    -f, --format=<FMT>          Output format
    -H, --headers=<headers>     Search through headers (Comma separated values)
    -l, --limit=<limit>         Limit number of mail displayed
    -t, --tags=<tags>           Searched tags (Comma separated values)
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


from docopt import docopt
import logging
import sys

from imap_cli import config, const, helpers


log = logging.getLogger('imap-cli-list')


def before(ctx, datetime):
    if datetime is None or not isinstance(datetime, datetime.datetime):
        log.error(
            'Wrong argument, expected datetime and receive {}'.format(datetime if datetime is None else type(datetime))
        )
        return
    search_criterion = u'(BEFORE {})'.format(datetime.strformat('%d-%b-%Y %H:%M:%S %z'))
    for result in helpers.list_mail(ctx, search_criterion=search_criterion):
        yield result


def search(ctx, directory=None, tags=None, headers=None):
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

    print search_criterion
    print '#' * 140
    for result in helpers.list_mail(ctx, search_criterion=search_criterion):
        yield result


def main():
    args = docopt('\n'.join(__doc__.split('\n')[2:]))
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.WARNING,
        stream=sys.stdout,
    )

    ctx = config.new_context_from_file(args['--config-file'])
    if args['--format'] is not None:
        ctx.format_status = args['--format']
    if args.get('--tags') is not None:
        args['--tags'] = args['--tags'].split(',')
    if args.get('--headers') is not None:
        args['--headers'] = args['--headers'].split(',')

    print args
    print '-' * 140
    helpers.connect(ctx)
    for truc in search(ctx, directory=args['<directory>'], tags=args['--tags'], headers=args['--headers']):
        print truc
    return 0


if __name__ == '__main__':
    sys.exit(main())
