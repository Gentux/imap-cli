# -*- coding: utf-8 -*-


"""Functions searching in IMAP account"""


import ast
import codecs
import datetime
import email
from email import header
import logging
import re
import sys

import docopt
import six

import imap_cli
from imap_cli import config
from imap_cli import const
from imap_cli import fetch


log = logging.getLogger('imap-cli-list')
usage = """Usage: imap-cli-search [options] [-t <tags>] [-T <full-text>]
[<directory>]

Options:
    -a, --address=<address>     Search for specified "FROM" address
    -c, --config-file=<FILE>    Configuration file (`~/.config/imap-cli` by
                                default)
    -d, --date=<date>           Search mail receive since the specified date
                                (format YYYY-MM-DD)
    -f, --format=<FMT>          Output format
    -l, --limit=<limit>         Limit number of mail displayed
    -s, --size=<SIZE>           Search mails larger than specified size (in
                                bytes)
    -S, --subject=<subject>     Search by subject
    -t, --tags=<tags>           Searched tags (Comma separated values)
    -T, --full-text=<text>      Searched tags (Comma separated values)
    --thread                    Display mail by thread
    -v, --verbose               Generate verbose messages
    -h, --help                  Show help options.
    --version                   Print program version.

----
imap-cli-search 0.7
Copyright (C) 2014 Romain Soufflet
License MIT
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"""


FLAGS_RE = r'.*FLAGS \((?P<flags>[^\)]*)\)'
MAIL_ID_RE = r'^(?P<mail_id>\d+) \('
UID_RE = r'.*UID (?P<uid>[^ ]*)'


def combine_search_criterion(search_criterion, operator='AND'):
    """Return a single IMAP search string combining all criterion given.

    .. versionadded:: 0.4

    :param operator: Possible values are : 'AND', 'OR' and 'NOT'
    """
    if operator not in ['AND', 'OR', 'NOT']:
        operator = 'AND'
        log.warning(u''.join([
            u'Wrong value for "operator" argument,',
            u'taking default value "{}"']).format(operator))

    if operator == 'AND':
        return '({})'.format(' '.join(search_criterion))
    if operator == 'OR':
        return 'OR {}'.format(' '.join(search_criterion))
    if operator == 'NOT':
        return 'NOT {}'.format(' '.join(search_criterion))


def create_search_criterion(address=None, date=None, size=None, subject=None,
                            tags=None, text=None, operator='AND'):
    """Create a list for all search criterion

    Wrapper helping developer to construct a list of search criterion with
    a single method.

    .. versionadded:: 0.2

    """
    search_criterion = []
    if address is not None:
        search_criterion.append(create_search_criterion_by_mail_address(
            address))
    if date is not None:
        search_criterion.append(create_search_criterion_by_date(date))
    if tags is not None:
        search_criterion.append(create_search_criteria_by_tag(tags))
    if text is not None:
        search_criterion.append(create_search_criteria_by_text(text))
    if subject is not None:
        search_criterion.append(create_search_criterion_by_subject(subject))
    if size is not None:
        search_criterion.append(create_search_criterion_by_size(size))

    if len(search_criterion) == 0:
        search_criterion.append('ALL')

    return search_criterion


def create_search_criterion_by_date(datetime, relative=None, sent=False):
    """Return a search criteria by date.

    .. versionadded:: 0.4

    :param relative: Can be one of 'BEFORE', 'SINCE', 'ON'.
    :param sent: Search after "sent" date instead of "received" date.
    """
    if relative not in ['BEFORE', 'ON', 'SINCE']:
        relative = 'SINCE'
    formated_date = datetime.strftime('%d-%h-%Y')
    return '{}{} {}'.format('SENT'
                            if sent is True
                            else '', relative, formated_date)


def create_search_criterion_by_header(header_name, header_value):
    """Return search criteria by header.

    .. versionadded:: 0.4
    """
    return 'HEADER {} {}'.format(header_name, header_value)


def create_search_criterion_by_mail_address(mail_address, header_name='FROM'):
    """Return a search criteria over mail address.

    .. versionadded:: 0.4

    :param header_name: Specify in wich header address must be searched. \
                        Possible values are "FROM", "CC", "BCC" and "TO"
    """
    if header_name not in ['BCC', 'CC', 'FROM', 'TO']:
        header_name = 'FROM'
        log.warning(
            'Wrong "header_name" value, taking default value {}'.format(
                header_name))

    return '{} "{}"'.format(header_name, mail_address)


def create_search_criterion_by_size(size, relative='LARGER'):
    """Return a search criteria by size.

    .. versionadded:: 0.4

    :param relative: Can be one of 'LARGER' or 'SMALLER'
    """
    # TODO(rsoufflet) sannitize "size" arg
    if relative not in ['LARGER', 'SMALLER']:
        relative = 'LARGER'
        log.warning(
            'Wrong "relative" argument, taking default value "{}"'.format(
                relative))
    return '{} "{}"'.format(relative, size)


def create_search_criterion_by_subject(subject):
    """Return search criteria by subject.

    .. versionadded:: 0.4
    """
    return 'SUBJECT "{}"'.format(subject)


def create_search_criteria_by_tag(tags):
    """Return a search criteria for specified tags.

    .. versionadded:: 0.3
    """
    if len(tags) == 0:
        return ''

    criterion = []
    for tag in tags:
        if tag.upper() in const.IMAP_SPECIAL_FLAGS:
            criterion.append(tag.upper())
        else:
            criterion.append('KEYWORD "{}"'.format(tag))
    return '({})'.format(
        ' '.join(criterion)) if len(criterion) > 1 else criterion[0]


def create_search_criteria_by_text(text):
    """Return a search criteria for fulltext.

    .. versionadded: 0.4
    """
    return 'BODY "{}"'.format(text)


def create_search_criterion_by_uid(uid):
    """Return a search criteria for UID.

    .. versionadded: 0.4
    """
    return 'UID {}'.format(uid)


def display_mail_tree(imap_account, threads, mail_info_by_uid=None, depth=0,
                      format_thread=None):
    """Generate indented string representing threads.

    .. versionadded:: 0.5

    :param imap_account: imaplib.IMAP4 or imaplib.IMAP4_SSL instance
    :param threads: List containing other list or uids
    :param mail_info_by_uid: Dict of information for every mail listed in
                             threads
    :param depth: Actual depth of indentation
    :param format_thread: Format string to apply to mail informations
    """
    if mail_info_by_uid is None:
        mail_set = list(threads_to_mail_set(threads))
        if len(mail_set) == 0:
            log.error('No mail found')

        mail_info_by_uid = {}
        for mail_info in fetch_mails_info(imap_account, mail_set=mail_set):
            mail_info_by_uid[int(mail_info['uid'])] = mail_info

    for idx, thread in enumerate(threads):
        if isinstance(thread, int):
            indent = depth if idx > 0 else depth - 1
            if mail_info_by_uid.get(thread) is None:
                continue
            yield u'{}{}'.format('  ' * indent, format_thread.format(
                **mail_info_by_uid[thread]))[0:140]
        else:
            for output in display_mail_tree(
                    imap_account,
                    thread,
                    mail_info_by_uid=mail_info_by_uid,
                    depth=depth + 1,
                    format_thread=format_thread):
                yield output


def fetch_mails_info(imap_account, mail_set=None, decode=True, limit=None):
    """Retrieve information for every mail in mail_set

    .. versionadded:: 0.2

    :param imap_account: imaplib.IMAP4 or imaplib.IMAP4_SSL instance
    :param mail_set: List of mail UID
    :param decode: Wether we must or mustn't decode mails informations
    :param limit: Return only last mails
    """
    flags_re = re.compile(FLAGS_RE)
    mail_id_re = re.compile(MAIL_ID_RE)
    uid_re = re.compile(UID_RE)

    if mail_set is None:
        mail_set = fetch_uids(imap_account, limit=limit)
    elif isinstance(mail_set, six.string_types):
        mail_set = mail_set.split()

    mails_data = fetch.fetch(imap_account, mail_set,
                             ['BODY.PEEK[HEADER]', 'FLAGS', 'UID'])
    if mails_data is None:
        return

    for mail_data in mails_data:
        flags_match = flags_re.match(mail_data[0])
        mail_id_match = mail_id_re.match(mail_data[0])
        uid_match = uid_re.match(mail_data[0])
        if mail_id_match is None or flags_match is None or uid_match is None:
            continue

        flags = flags_match.groupdict().get('flags').split()
        mail_id = mail_id_match.groupdict().get('mail_id').split()[0]
        mail_uid = uid_match.groupdict().get('uid').split()[0]

        mail = email.message_from_string(mail_data[1])
        if decode is True:
            for header_name, header_value in mail.items():
                header_new_value = []
                for value, encoding in header.decode_header(header_value):
                    if value is None:
                        continue
                    try:
                        decoded_value = codecs.decode(value,
                                                      encoding or 'utf-8',
                                                      'ignore')
                    except TypeError:
                        log.debug(u'Can\'t decode {} with {} encoding'.format(
                            value, encoding))
                        decoded_value = value
                    header_new_value.append(decoded_value)
                mail.replace_header(header_name, ' '.join(header_new_value))

        yield dict([
            ('flags', flags),
            ('id', mail_id),
            ('uid', mail_uid),
            ('from', mail['from']),
            ('to', mail['to']),
            ('date', mail['date']),
            ('subject', mail.get('subject', '')),
        ])


def fetch_threads(imap_account, charset=None, limit=None,
                  search_criterion=None):
    """Retrieve information for every mail search_criterion by thread.

    .. versionadded:: 0.5

    :param imap_account: imaplib.IMAP4 or imaplib.IMAP4_SSL instance
    :param charset: Desired charset for IMAP response
    :param limit: Return only last mails
    :param search_criterion: List of criteria for IMAP Search
    """
    request_search_criterion = search_criterion
    if search_criterion is None or search_criterion == ['ALL']:
        request_search_criterion = 'ALL'
    if charset is None:
        charset = 'UTF-8'
    if isinstance(search_criterion, list):
        request_search_criterion = combine_search_criterion(search_criterion)

    if imap_account.state != 'SELECTED':
        log.warning(u'No directory specified, selecting {}'.format(
            const.DEFAULT_DIRECTORY))
        imap_cli.change_dir(imap_account, const.DEFAULT_DIRECTORY)

    status, data = imap_account.uid('THREAD', 'REFERENCES', charset,
                                    request_search_criterion)
    if status != const.STATUS_OK:
        return None
    threads = parse_thread_response(data[0])
    return threads if limit is None else threads[-limit:]


def fetch_uids(imap_account, charset=None, limit=None, search_criterion=None):
    """Retrieve information for every mail search_criterion.

    .. versionadded:: 0.3

    :param imap_account: imaplib.IMAP4 or imaplib.IMAP4_SSL instance
    :param charset: Desired charset for IMAP response
    :param limit: Return only last mails
    :param search_criterion: List of criteria for IMAP Search
    """
    request_search_criterion = search_criterion
    if search_criterion is None:
        request_search_criterion = 'ALL'
    elif isinstance(search_criterion, list):
        request_search_criterion = combine_search_criterion(search_criterion)

    if imap_account.state != 'SELECTED':
        log.warning(u'No directory specified, selecting {}'.format(
            const.DEFAULT_DIRECTORY))
        imap_cli.change_dir(imap_account, const.DEFAULT_DIRECTORY)

    status, data_bytes = imap_account.uid(
        'SEARCH',
        charset,
        request_search_criterion)
    data = [data_bytes[0].decode('utf-8')]
    if status == const.STATUS_OK:
        return data[0].split() if limit is None else data[0].split()[-limit:]


def parse_thread_response(thread_string):
    """Parse IMAP THREAD response into a list of thread.

    We define thread as list of mail UID (int) which can contain other thread
    (nested list)

    Example:

    >>> imap_account = imap_cli.connect('serveur', 'login', 'password')
    >>> imap_response = fetch_threads(imap_account)
    >>> repr(parse_thread_response(imap_response))
    '[[[6], [7]], [14, 19], [23, 58, 60, 61, 62, 63, 68, 69, 70]]'
    """
    # FIXME(rsoufflet) Not sure the use of "ast" module is the right solution.
    # Any ideas are welcome here
    return ast.literal_eval('[{}]'.format(
        thread_string
        .decode('utf-8')
        .replace(' ', ', ')
        .replace('(', '[')
        .replace(')', '], ')))


def threads_to_mail_set(threads):
    for value in threads:
        if isinstance(value, list):
            for sub_value in threads_to_mail_set(value):
                yield sub_value
        else:
            yield value


def threads_to_mail_tree(threads):
    mail_tree = []
    for thread in threads:
        if isinstance(thread, list):
            if len(thread) == 1:
                mail_tree.append(thread[0])
            else:
                mail_tree.append(threads_to_mail_tree(thread))
        else:
            mail_tree.append(thread)
    return mail_tree


def main():
    args = docopt.docopt('\n'.join(usage.split('\n')), version=const.VERSION)
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.INFO,
        stream=sys.stdout,
    )

    connect_conf = config.new_context_from_file(args['--config-file'],
                                                section='imap')
    if connect_conf is None:
        return 1
    display_conf = config.new_context_from_file(args['--config-file'],
                                                section='display')
    if args['--format'] is not None:
        display_conf_key = ('format_thread'
                            if args['--thread'] is True
                            else 'format_list')
        display_conf[display_conf_key] = args['--format']
    if args.get('--tags') is not None:
        args['--tags'] = args['--tags'].split(',')
    if args['--date'] is not None:
        try:
            date = datetime.datetime.strptime(args['--date'], '%Y-%m-%d')
        except ValueError:
            date = None
    else:
        date = None
    if args['--limit'] is not None:
        try:
            limit = int(args['--limit'])
            if limit < 1:
                raise ValueError
        except ValueError:
            log.error('Invalid argument limit : {}'.format(args['--limit']))
            return 1
    else:
        limit = None

    try:
        imap_account = imap_cli.connect(**connect_conf)
        imap_cli.change_dir(
            imap_account,
            directory=args['<directory>'] or const.DEFAULT_DIRECTORY)
        search_criterion = create_search_criterion(
            address=args['--address'],
            date=date,
            subject=args['--subject'],
            size=args['--size'],
            tags=args['--tags'],
            text=args['--full-text'],
        )
        if args['--thread'] is False:
            mail_set = fetch_uids(imap_account,
                                  search_criterion=search_criterion)
            if len(mail_set) == 0:
                log.error('No mail found')
                return 0
            for mail_info in fetch_mails_info(imap_account,
                                              limit=limit, mail_set=mail_set):
                sys.stdout.write(
                    display_conf['format_list'].format(**mail_info))
                sys.stdout.write('\n')
        else:
            threads = fetch_threads(imap_account, limit=limit,
                                    search_criterion=search_criterion)
            mail_tree = threads_to_mail_tree(threads)
            for output in display_mail_tree(
                    imap_account, mail_tree,
                    format_thread=display_conf['format_thread']):
                sys.stdout.write(output)
                sys.stdout.write('\n')

        imap_cli.disconnect(imap_account)
    except KeyboardInterrupt:
        log.info('Interrupt by user, exiting')

    return 0


if __name__ == '__main__':
    sys.exit(main())
