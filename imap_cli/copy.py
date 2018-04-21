# -*- coding: utf-8 -*-


"""Set flags on a set of mails

Usage: imap-cli-copy [options] <dest> <mail_id>...

Options:
    -c, --config-file=<FILE>    Configuration file
    -d, --delete                Delete copied mails (Move instead of copy)
    -f, --from                  Directory which store mail_ids
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
from imap_cli import flag


log = logging.getLogger('imap-cli-flag')


def copy(imap_account, message_set, destination):
    if message_set is None or len(message_set) == 0:
        log.error('Invalid message set')
    request_message_set = ','.join(str(mail_id) for mail_id in message_set)
    status, result = imap_account.uid(
        u'COPY',
        request_message_set,
        destination,
    )
    if status == const.STATUS_OK:
        log.debug('Mails "{}" have been copied : {}'.format(
            request_message_set, result))
    else:
        log.error('Mails "{}" have NOT been copied : {}'.format(
            request_message_set, result))


def main():
    args = docopt.docopt('\n'.join(__doc__.split('\n')[2:]),
                         version=const.VERSION)
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.INFO,
        stream=sys.stdout,
    )

    conf = config.new_context_from_file(args['--config-file'], section='imap')
    if conf is None:
        return 1

    try:
        imap_account = imap_cli.connect(**conf)
        imap_cli.change_dir(imap_account,
                            args['--from'] or const.DEFAULT_DIRECTORY,
                            read_only=False)

        copy(imap_account, args['<mail_id>'], args['<dest>'])
        if args['--delete']:
            flag.flag(imap_account, args['<mail_id>'], [const.FLAG_DELETED])
            imap_account.expunge()

        imap_cli.disconnect(imap_account)
    except KeyboardInterrupt:
        log.info('Interrupt by user, exiting')

    return 0


if __name__ == '__main__':
    sys.exit(main())
