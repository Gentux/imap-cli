#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""Use IMAP CLI to gt a summary of IMAP account state."""


import argparse
import getpass
import logging
import os
import sys

import imap_cli
from imap_cli import search


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)


def truncate_string(string, length):
    minus_than_position = string.find('<')
    if minus_than_position > 0 and string.find('>') > minus_than_position:
        string = string[0:minus_than_position]
    return string if len(string) < length else u'{0}…'.format(string[0:length])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('imap_server', help="IMAP Server hostname")
    parser.add_argument('-l', '--login', help="Login for IMAP account")
    parser.add_argument('--no-ssl', action='store_true', help="Don't use SSL")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase output verbosity')

    args = parser.parse_args()
    password = getpass.getpass()

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    try:
        imap_account = imap_cli.connect(
            hostname=args.imap_server,
            username=args.login,
            password=password,
            ssl=not args.no_ssl,
        )
        for directory_status in sorted(imap_cli.status(imap_account),
                                       key=lambda obj: obj['directory']):
            if int(directory_status['unseen']) > 0:
                sys.stdout.write(directory_status['directory'])
                sys.stdout.write('\n')

                imap_cli.change_dir(imap_account,
                                    directory_status['directory'])
                mail_set = search.fetch_uids(
                    imap_account,
                    search_criterion=[
                        search.create_search_criteria_by_tag(['unseen'])],
                )

                for mail_info in search.fetch_mails_info(imap_account,
                                                         mail_set=mail_set):
                    sys.stdout.write(
                        u'    {:<10} From : {:<30} \tSubject : {}\n'.format(
                            mail_info['uid'],
                            truncate_string(mail_info['from'], 30),
                            truncate_string(mail_info['subject'], 50)))
        imap_cli.disconnect(imap_account)
    except KeyboardInterrupt:
        log.info('Interrupt by user, exiting')

    return 0

if __name__ == "__main__":
    sys.exit(main())
