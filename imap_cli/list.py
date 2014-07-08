# -*- coding: utf-8 -*-


"""Functions returning an IMAP account state

Usage: list [options] [<directory>]

    -c, --config-file=<FILE>    Configuration file (`~/.config/imap-cli` by default)
    -f, --format=<FMT>          Output format
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
import os
import sys

from imap_cli import config, helpers


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)

DEFAULT_CONFIG_FILE = '~/.config/imap-cli'
DEFAULT_DIRECTORY = 'INBOX'


def main():
    args = docopt(__doc__[2:], version='IMAP-Cli Status v0.1')
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.WARNING,
        stream=sys.stdout,
    )
    config_filename = args['--config-file'] or DEFAULT_CONFIG_FILE
    config_filename = os.path.abspath(os.path.expanduser(os.path.expandvars(config_filename)))
    log.debug("Using configuration file '{}'".format(config_filename))

    ctx = config.new_context(config_filename)
    ctx.directory = args['<directory>'] or DEFAULT_DIRECTORY

    helpers.connect(ctx)
    status, mail_count = ctx.mail_account.select(ctx.directory, True)
    for mail_id in helpers.list_mail(ctx):
        status, mail_data = ctx.mail_account.fetch(mail_id, '(BODY.PEEK[HEADER])')
        if status != 'OK':
            print u'Error fetching mail {}'.format(mail_id)
            continue
        mail = email.message_from_string(mail_data[0][1])
        print ctx.format_list.format(
            mail_from=mail['from'],
            to=mail['to'],
            subject=mail.get('subject', '').decode('utf-8'),
            )


if __name__ == '__main__':
    sys.exit(main())
