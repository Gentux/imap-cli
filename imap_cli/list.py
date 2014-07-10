# -*- coding: utf-8 -*-


"""Functions returning an IMAP account state

Usage: list [options] [<directory>]

    -c, --config-file=<FILE>    Configuration file (`~/.config/imap-cli` by default)
    -f, --format=<FMT>          Output format
    -l, --limit=<limit>         Limit number of mail displayed
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
import email
import logging
import sys

from imap_cli import config, helpers


log = logging.getLogger('imap-cli-list')


def list(ctx, directory='INBOX'):
    status, mail_count = ctx.mail_account.select(directory, True)
    if status != 'OK':
        log.warn(u'Cannot access directory {}'.format(directory))
        return

    for mail_id in helpers.list_mail(ctx, limit=ctx.limit):
        status, mail_data = ctx.mail_account.fetch(mail_id, '(BODY.PEEK[HEADER])')
        if status != 'OK':
            print u'Error fetching mail {}'.format(mail_id)
            continue
        mail = email.message_from_string(mail_data[0][1])
        yield {
            'mail_id': mail_id,
            'mail_from': mail['from'],
            'to': mail['to'],
            'date': mail['date'],
            'subject': mail.get('subject', '').decode('utf-8'),
        }


def main():
    args = docopt(__doc__[2:], version='IMAP-Cli Status v0.1')
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.WARNING,
        stream=sys.stdout,
    )

    ctx = config.new_context_from_file(args['--config-file'])
    if args['--format'] is not None:
        ctx.format_status = args['--format']

    helpers.connect(ctx)
    for mail_info in list(ctx):
        print ctx.format_list.format(**mail_info)


if __name__ == '__main__':
    sys.exit(main())
