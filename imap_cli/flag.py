# -*- coding: utf-8 -*-


"""Set flags on a set of mails

Usage: imap-cli-flag [options] [<directory>] <mail_id> <flag>...

Options:
    -c, --config-file=<FILE>    Configuration file
    -v, --verbose               Generate verbose messages
    -h, --help                  Show help options.
    --version                   Print program version.

----
imap-cli-flag 0.3
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


def unset_flag(imap_account, mail_id=None, flags_str=''):
    if mail_id is None:
        log.error('Can\'t set flag on email {}'.format(mail_id))
        return None
    # TODO(rsoufflet)
    truc = imap_account.store(mail_id, '+FLAGS', flags_str)
    log.debug(repr(truc))


def flag(imap_account, mail_id, flags, directory=const.DEFAULT_DIRECTORY):
    status, mail_count = imap_account.select(directory)
    if status != const.STATUS_OK:
        log.warn(u'Cannot access directory {}'.format(directory))
        return
    for flag in flags:
        if mail_id is None:
            log.error('Can\'t set flag on email {}'.format(mail_id))
            continue
        # TODO(rsoufflet)
        truc = imap_account.store(mail_id, '+FLAGS', r'({})'.format(flag))
        log.debug(repr(truc))


def main():
    args = docopt.docopt('\n'.join(__doc__.split('\n')[2:]))
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.WARNING,
        stream=sys.stdout,
    )

    conf = config.new_context_from_file(args['--config-file'], section='imap')
    imap_account = imap_cli.connect(**conf)
    flag(imap_account, args['<mail_id>'], args['<flag>'], directory=args['<directory>'])
    imap_cli.disconnect(imap_account)
    return 0


if __name__ == '__main__':
    sys.exit(main())
