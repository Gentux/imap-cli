#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""Use IMAP CLI to gt a summary of IMAP account state."""


import argparse
import cmd
import datetime
import logging
import os
import sys
import tempfile
import threading
import time
import webbrowser

import docopt

import imap_cli
from imap_cli import config
from imap_cli import const
from imap_cli import copy
from imap_cli import fetch
from imap_cli import flag
from imap_cli import search


app_name = os.path.splitext(os.path.basename(__file__))[0]
keep_alive_bool = True
keep_alive_timer = 30
log = logging.getLogger(app_name)


class ImapShell(cmd.Cmd):
    completekey = 'Tab'
    intro = u''.join([
        'IMAP interactive Command Line Interpreter. ',
        'Type help or ? to list commands.\n'])
    prompt = '(imap-cli "INBOX") '
    stdout = sys.stdout
    cmdqueue = []
    delete_conf = None

    def __init__(self, imap_account):
        self.imap_account = imap_account

    def do_cd(self, arg):
        '''Change selected IMAP folder.'''
        try:
            args = docopt.docopt('Usage: cd <directory>', arg)
        except SystemExit:
            return

        cd_result = imap_cli.change_dir(self.imap_account,
                                        directory=args['<directory>'])
        if cd_result == -1:
            sys.stdout.write('IMAP Folder can\'t be found\n')
        else:
            self.prompt = '(imap-cli "{}") '.format(args['<directory>'])

    def do_cp(self, arg):
        '''Copy mail from one mailbox to another.'''
        try:
            args = docopt.docopt('Usage: cp <dest> <mail_id>...', arg)
        except SystemExit:
            return
        copy.copy(self.imap_account, args['<mail_id>'], args['<dest>'])

    def do_flag(self, arg):
        '''Set or Unset flag on mails.'''
        try:
            args = docopt.docopt('\n'.join([
                'Usage: flag [options] <mail_id> <flag>',
                '',
                'Options:',
                '    -u, --unset    Remove flag instead of setting them',
                '    -h, --help     Show help options',
            ]), argv=arg)
        except SystemExit:
            return
        flag.flag(self.imap_account, [args['<mail_id>']], args['<flag>'],
                  unset=args['--unset'])

    def do_list(self, arg):
        '''List mail in specified folder.'''

        try:
            args = docopt.docopt('\n'.join([
                'Usage: list [options] [<directory>]',
                '',
                'Options:',
                '    -l, --limit=<LIMIT>    Limit number of mail displayed',
                '    -h, --help             Show this message',
            ]), argv=arg)
        except SystemExit:
            return

        try:
            limit = int(args['--limit'] or 10)
        except ValueError:
            limit = 10
        for mail_info in search.fetch_mails_info(self.imap_account,
                                                 limit=limit):
            sys.stdout.write(
                u'UID : {:<10} From : {:<40.40} Subject : {:.50}\n'.format(
                    mail_info['uid'],
                    mail_info['from'],
                    mail_info['subject']).encode('UTF-8'))

    def do_mv(self, arg):
        '''Move mail from one mailbox to another.'''
        try:
            args = docopt.docopt('Usage: cp <dest> <mail_id>...', arg)
        except SystemExit:
            return
        copy.copy(self.imap_account, args['<mail_id>'], args['<dest>'])
        flag.flag(self.imap_account, args['<mail_id>'], [const.FLAG_DELETED])
        self.imap_account.expunge()

    def do_quit(self, arg):
        'Exit this shell'
        global keep_alive_bool
        keep_alive_bool = False
        imap_cli.disconnect(self.imap_account)
        sys.stdout.write('Bye\n')
        return True

    def do_rm(self, arg):
        '''Remove mail from one mailbox.'''
        try:
            args = docopt.docopt('Usage: rm <mail_id>...', arg)
        except SystemExit:
            return

        if self.delete_conf['delete_method'] == 'MOVE_TO_TRASH':
            copy.copy(self.imap_account, args['<mail_id>'],
                      self.delete_conf['trash_directory'])
        flag.flag(self.imap_account, args['<mail_id>'], [const.FLAG_DELETED])
        if self.delete_conf['delete_method'] in ['MOVE_TO_TRASH', 'EXPUNGE']:
            self.imap_account.expunge()

    def do_read(self, arg):
        '''Read mail by uid.'''
        try:
            args = docopt.docopt(u'\n'.join([
                u'Usage: read [options] <mail_uid> [<save_directory>]',
                u'',
                u'Options:',
                u'    -b, --browser     Open mail in browser',
            ]), arg)
        except SystemExit:
            return

        fetched_mail = fetch.read(self.imap_account, args['<mail_uid>'],
                                  save_directory=args['<save_directory>'])
        if fetched_mail is None:
            log.error("Mail was not fetched, an error occured")

        if args['--browser'] is True:
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(fetch.display(fetched_mail,
                                          browser=True).encode('utf-8'))

            webbrowser.open_new_tab(temp_file.name)

            temp_file.close()
        else:
            sys.stdout.write(fetch.display(fetched_mail).encode('UTF-8'))

    def do_search(self, arg):
        '''Search mail.'''
        usage = '\n'.join([
            'Usage: search [options]',
            '',
            'Options:',
            '    -a, --address=<address>     Search by address',
            '    -d, --date=<date>           Search by date (YYYY-MM-DD)',
            '    -s, --size=<SIZE>           Search by size (in bytes)',
            '    -S, --subject=<subject>     Search by subject',
            '    -t, --tags=<tags>           Searched tags (Comma separated)',
            '    -T, --full-text=<text>      Searched tags (Comma separated)',
            '    -h, --help                  Show help options.',
        ])
        try:
            args = docopt.docopt(usage, argv=arg)
        except SystemExit:
            return

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
        mail_set = search.fetch_uids(self.imap_account,
                                     search_criterion=search_criterion)
        if len(mail_set) == 0:
            log.error('No mail found')
            return 0
        for mail_info in search.fetch_mails_info(self.imap_account,
                                                 mail_set=mail_set):
            sys.stdout.write(
                u'UID : {:<10} From : {:<40.40} Subject : {:.50}\n'.format(
                    mail_info['uid'],
                    mail_info['from'],
                    mail_info['subject']).encode('UTF-8'))

    def do_status(self, arg):
        'Print status of all IMAP folder in this account'
        directory_statuses = sorted(imap_cli.status(self.imap_account),
                                    key=lambda obj: obj['directory'])
        for directory_status in directory_statuses:
            sys.stdout.write(
                u'{:<30} : Unseen {:<6}   Recent {:<6}   Total {:<6}\n'.format(
                    directory_status['directory'],
                    directory_status['unseen'],
                    directory_status['recent'],
                    directory_status['count']).encode('UTF-8'))

    def do_unseen(self, arg):
        '''List Unseen mail (equivalent to "search -t unseen").'''
        search_criterion = search.create_search_criterion(tags=['unseen'])
        mail_set = search.fetch_uids(self.imap_account,
                                     search_criterion=search_criterion)
        if len(mail_set) == 0:
            log.error('No unseen mail found')
        else:
            for mail_info in search.fetch_mails_info(self.imap_account,
                                                     mail_set=mail_set):
                sys.stdout.write(
                    u'UID : {:<10} From : {:<40.40} Subject : {:.50}\n'.format(
                        mail_info['uid'],
                        mail_info['from'],
                        mail_info['subject']).encode('UTF-8'))

    def emptyline(self):
        pass


def keep_alive(imap_account):
    time_count = 0
    while keep_alive_bool is True:
        time_count += 1
        if time_count % keep_alive_timer == 0:
            log.debug('NOOP send')
            imap_account.noop()
        time.sleep(1)
    log.debug('Keep alive thread terminated')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase output verbosity')

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        stream=sys.stdout,
    )

    connection_config = config.new_context_from_file(section='imap')
    if connection_config is None:
        return 1
    delete_config = config.new_context_from_file(section='trash')

    imap_account = imap_cli.connect(**connection_config)
    imap_shell = ImapShell(imap_account)
    imap_shell.delete_conf = delete_config
    keep_alive_thread = threading.Thread(target=keep_alive,
                                         args=(imap_account,))

    keep_alive_thread.start()
    imap_shell.cmdloop()
    keep_alive_thread.join()

    return 0


if __name__ == "__main__":
    sys.exit(main())
