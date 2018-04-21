# -*- coding: utf-8 -*-


"""Set flags on a set of mails

Usage: imap-cli-delete [options] <mail_id>...

Options:
    -c, --config-file=<FILE>    Configuration file
    -d, --directory MAILBOX     Specify a Mailbox
    -v, --verbose               Generate verbose messages
    -h, --help                  Show help options.
    --version                   Print program version.

----
imap-cli-copy 0.7
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
from imap_cli import copy
from imap_cli import flag


log = logging.getLogger('imap-cli-delete')


def main():
    args = docopt.docopt('\n'.join(__doc__.split('\n')[2:]),
                         version=const.VERSION)
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.INFO,
        stream=sys.stdout,
    )

    conf = config.new_context_from_file(args['--config-file'], section='imap')
    delete_conf = config.new_context_from_file(args['--config-file'],
                                               section='trash')
    if conf is None:
        return 1

    try:
        imap_account = imap_cli.connect(**conf)
        imap_cli.change_dir(imap_account,
                            args['--directory'] or const.DEFAULT_DIRECTORY,
                            read_only=False)

        if delete_conf['delete_method'] == 'MOVE_TO_TRASH':
            copy.copy(imap_account, args['<mail_id>'],
                      delete_conf['trash_directory'])
        flag.flag(imap_account, args['<mail_id>'], [const.FLAG_DELETED])
        if delete_conf['delete_method'] in ['MOVE_TO_TRASH', 'EXPUNGE']:
            imap_account.expunge()

        imap_cli.disconnect(imap_account)
    except KeyboardInterrupt:
        log.info('Interrupt by user, exiting')

    return 0


if __name__ == '__main__':
    sys.exit(main())
