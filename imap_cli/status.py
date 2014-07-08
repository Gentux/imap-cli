# -*- coding: utf-8 -*-


"""Functions returning an IMAP account state

Usage: status [options]

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
import logging
import os
import re
import sys

from imap_cli import config, helpers


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)

DEFAULT_CONFIG_FILE = '~/.config/imap-cli'
STATUS_RE = r'{dirname} \({messages_count} {recent} {unseen}\)'.format(
    dirname=r'"(?P<dirname>.*)"',
    messages_count=r'MESSAGES (?P<mail_count>\d{1,5})',
    recent=r'RECENT (?P<mail_recent>\d{1,5})',
    unseen=r'UNSEEN (?P<mail_unseen>\d{1,5})',
    )


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
    status_cre = re.compile(STATUS_RE)
    helpers.connect(ctx)
    for tags, delimiter, dirname in helpers.list_dir(ctx):
        status, data = ctx.mail_account.status(dirname, '(MESSAGES RECENT UNSEEN)')
        if status != 'OK':
            continue
        status_match = status_cre.match(data[0])
        if status_match is not None:
            group_dict = status_match.groupdict()
            print u'{:>20} : {:>5} Unseen   {:>5} Mails     {:>5} Recent'.format(
                group_dict['dirname'],
                group_dict['mail_unseen'],
                group_dict['mail_count'],
                group_dict['mail_recent'],
            )


if __name__ == '__main__':
    sys.exit(main())
