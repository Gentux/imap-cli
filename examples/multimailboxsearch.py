#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""Use IMAP CLI to search trhough every mailbox on an account."""


import argparse
import getpass
import logging
import os
import sys

import imap_cli
from imap_cli import search


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('imap_server', help="IMAP Server hostname")
    parser.add_argument('searched_address', help="Searched address")
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
            imap_cli.change_dir(imap_account, directory_status['directory'])

            mail_set = search.fetch_uids(
                imap_account,
                search_criterion=[
                    search.create_search_criterion_by_mail_address(
                        args.searched_address)],
            )

            if len(mail_set) > 0:
                sys.stdout.write(u'{} Directory\n'.format(
                    directory_status['directory']).encode('UTF-8'))

                for mail_info in search.fetch_mails_info(imap_account,
                                                         mail_set=mail_set):
                    format_string = u''.join([
                        u'    {:<10} ',
                        u'From : {:<30.30} \t',
                        u'Subject : {:.50}\n'])
                    sys.stdout.write(format_string.format(
                        mail_info['uid'],
                        mail_info['from'],
                        mail_info['subject']).encode('UTF-8'))
        imap_cli.disconnect(imap_account)
    except KeyboardInterrupt:
        log.info('Interrupt by user, exiting')

    return 0

if __name__ == "__main__":
    sys.exit(main())
