#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""Use IMAP CLI to gt a summary of IMAP account state."""


import argparse
import logging
import os
import sys
import time

import pynotify

import imap_cli
from imap_cli import config


app_name = os.path.splitext(os.path.basename(__file__))[0]
keep_alive_timer = 10
log = logging.getLogger(app_name)

watched_dir = [
    'INBOX',
    'Openstack',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        stream=sys.stdout,
    )
    pynotify.init(app_name)

    connection_config = config.new_context_from_file(section='imap')
    if connection_config is None:
        return 1

    imap_account = imap_cli.connect(**connection_config)

    time_count = 0
    sys.stdout.write('\n')
    while True:
        time_count += 1
        if time_count % keep_alive_timer == 0:
            notifications = []
            for status in imap_cli.status(imap_account):
                if status['directory'] in watched_dir and status['unseen'] != '0':
                    notifications.append(u'{} has {} new mails'.format(status['directory'], status['unseen']))
            if len(notifications) > 0:
                notifier = pynotify.Notification("IMAP Notify", u'\n'.join(notifications))
                notifier.show()
        time.sleep(1)

    return 0


if __name__ == "__main__":
    sys.exit(main())
