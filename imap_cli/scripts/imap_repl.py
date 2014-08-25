#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""Use IMAP CLI to gt a summary of IMAP account state."""


import argparse
import cmd
import datetime
import logging
import os
import sys

import docopt

import imap_cli
from imap_cli import config
from imap_cli import fetch
from imap_cli import flag
from imap_cli import search


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)


class ImapShell(cmd.Cmd):
    completekey = 'Tab'
    intro = 'IMAP interactive Command Line Interpreter.  Type help or ? to list commands.\n'
    prompt = '(imap-cli "INBOX") '
    stdout = sys.stdout
    cmdqueue = []

    def __init__(self, imap_account):
        self.imap_account = imap_account

    def do_cd(self, arg):
        '''Change selected IMAP folder.'''
        args = docopt.docopt('Usage: cd <directory>', arg)
        cd_result = imap_cli.change_dir(self.imap_account, directory=args['<directory>'])
        if cd_result == -1:
            sys.stdout.write('IMAP Folder can\'t be found\n')
        else:
            self.prompt = '(imap-cli "{}") '.format(args['<directory>'])

    def do_flag(self, arg):
        '''Set or Unset flag on mails.'''
        args = docopt.docopt('\n'.join([
            'Usage: flag [options] <mail_id> <flag>',
            '',
            'Options:',
            '    -u, --unset    Remove flag instead of setting them',
            '    -h, --help     Show help options',
        ]), argv=arg)
        flag.flag(self.imap_account, [args['<mail_id>']], args['<flag>'], unset=args['--unset'])

    def do_list(self, arg):
        '''List mail in specified folder.'''

        args = docopt.docopt('\n'.join([
            'Usage: list [options] [<directory>]',
            '',
            'Options:',
            '    -l, --limit=<LIMIT>    Limit number of mail displayed',
            '    -h, --help             Show this message',
        ]), argv=arg)

        try:
            limit = int(args['--limit'] or 10)
        except ValueError:
            limit = 10
        for mail_info in search.fetch_mails_info(self.imap_account, limit=limit):
            sys.stdout.write(u'UID : {:<10} From : {:<40} Subject : {}\n'.format(
                mail_info['uid'][0],
                truncate_string(mail_info['from'], 33),
                truncate_string(mail_info['subject'], 50),
            ))

    def do_read(self, arg):
        '''Read mail by uid.'''
        args = docopt.docopt('Usage: read <mail_uid> [<save_directory>]', arg)
        fetched_mail = fetch.read(self.imap_account, args['<mail_uid>'], save_directory=args['<save_directory>'])
        if fetched_mail is None:
            log.error("Mail was not fetched, an error occured")

        sys.stdout.write(fetch.display(fetched_mail))

    def do_search(self, arg):
        '''Search mail.'''
        args = docopt.docopt('\n'.join([
            'Usage: search [options]',
            '',
            'Options:',
            '    -a, --address=<address>     Search for specified "FROM" address',
            '    -d, --date=<date>           Search mail receive since the specified date (format YYYY-MM-DD)',
            '    -s, --size=<SIZE>           Search mails larger than specified size (in bytes)',
            '    -S, --subject=<subject>     Search by subject',
            '    -t, --tags=<tags>           Searched tags (Comma separated values)',
            '    -T, --full-text=<text>      Searched tags (Comma separated values)',
            '    -h, --help                  Show help options.',
        ]), argv=arg)

        if args.get('--tags') is not None:
            args['--tags'] = args['--tags'].split(',')
        if args['--date'] is not None:
            try:
                date = datetime.datetime.strptime(args['--date'], '%Y-%m-%d')
            except ValueError:
                date = None
        else:
            date = None

        search_criterion = search.create_search_criterion(
            address=args['--address'],
            date=date,
            subject=args['--subject'],
            size=args['--size'],
            tags=args['--tags'],
            text=args['--full-text'],
        )
        mail_set = search.fetch_uids(self.imap_account, search_criterion=search_criterion)
        if len(mail_set) == 0:
            log.error('No mail found')
            return 0
        for mail_info in search.fetch_mails_info(self.imap_account, mail_set=mail_set):
            sys.stdout.write(u'UID : {:<10} From : {:<40} Subject : {}\n'.format(
                mail_info['uid'][0],
                truncate_string(mail_info['from'], 33),
                truncate_string(mail_info['subject'], 50),
            ))

    def do_status(self, arg):
        'Print status of all IMAP folder in this account'
        directory_statuses = sorted(imap_cli.status(self.imap_account), key=lambda obj: obj['directory'])
        for directory_status in directory_statuses:
            sys.stdout.write(u'{:<30} : Unseen {:<6}   Recent {:<6}   Total {:<6}\n'.format(
                directory_status['directory'],
                directory_status['unseen'],
                directory_status['recent'],
                directory_status['count'],
            ))

    def do_quit(self, arg):
        'Exit this shell'
        print('Bye')
        return True

    def emptyline(self):
        pass


def truncate_string(string, length):
    minus_than_position = string.find('<')
    if minus_than_position > 0 and string.find('>') > minus_than_position:
        string = string[0:minus_than_position]
    return string if len(string) < length else u'{0}…'.format(string[0:length])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        stream=sys.stdout,
    )

    connection_config = config.new_context_from_file(section='imap')
    imap_account = imap_cli.connect(**connection_config)
    ImapShell(imap_account).cmdloop()

    return 0


if __name__ == "__main__":
    sys.exit(main())
