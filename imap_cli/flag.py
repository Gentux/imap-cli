# -*- coding: utf-8 -*-


"""Set flags on a set of mails

Usage: imap-cli-flag [options] <mail_id> <flag>...

Options:
    -c, --config-file=<FILE>    Configuration file
    -d, --directory=<DIR>       Imap folder
    -u, --unset                 Remove flag instead of setting them
    -v, --verbose               Generate verbose messages
    -h, --help                  Show help options.
    --version                   Print program version.

----
imap-cli-flag 0.6
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


log = logging.getLogger('imap-cli-flag')


def flag(imap_account, message_set, flags, unset=False):
    if message_set is None or len(message_set) == 0:
        log.error('Invalid message set')
    request_message_set = ','.join(str(mail_id) for mail_id in message_set)
    status, result = imap_account.uid(
        u'STORE',
        request_message_set,
        u'+FLAGS' if unset is False else '-FLAGS',
        u'({})'.format(u' '.join(flags)),
    )
    if status == const.STATUS_OK:
        log.debug('Flags "{}" have been set : {}'.format(flags, result))
    else:
        log.error('Flags "{}" have not been set : {}'.format(flags, result))


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
                            args['--directory'] or const.DEFAULT_DIRECTORY,
                            read_only=False)

        flag(imap_account, [args['<mail_id>']], args['<flag>'],
             unset=args['--unset'])

        imap_cli.disconnect(imap_account)
    except KeyboardInterrupt:
        log.info('Interrupt by user, exiting')

    return 0


if __name__ == '__main__':
    sys.exit(main())
