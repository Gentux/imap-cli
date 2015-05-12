# -*- coding: utf-8 -*-


"""IMAP basic helpers"""


import imaplib
import logging
import re

from imap_cli import const
from imap_cli import string


log = logging.getLogger('imap-cli')

LIST_DIR_RE = re.compile(
    r'\((?P<flags>[^\)]*)\) "(?P<delimiter>[^"]*)" "(?P<directory>[^"]*)"')
STATUS_RE = re.compile(
    r'{directory} \({messages_count} {recent} {unseen}\)'.format(
        directory=r'"(?P<directory>.*)"',
        messages_count=r'MESSAGES (?P<mail_count>\d{1,5})',
        recent=r'RECENT (?P<mail_recent>\d{1,5})',
        unseen=r'UNSEEN (?P<mail_unseen>\d{1,5})'))


def change_dir(imap_account, directory, read_only=True):
    if imap_account.state == 'SELECTED':
        imap_account.close()
    status, mail_count = imap_account.select(directory, read_only)
    if status == const.STATUS_OK:
        return mail_count[0]
    else:
        log.error('Can\'t select directory {}'.format(directory))
        return -1


def connect(hostname, username, password, port=None, ssl=True):
    """Return an IMAP account object (see imaplib documentation for details)

    .. versionadded:: 0.1

    Example:

    >>> import imap_cli
    >>> from imap_cli import config
    >>> conf = config.new_context_from_file(section='imap')
    >>> imap_cli.connect(**conf)
    <imaplib.IMAP4_SSL instance at 0x7fccd57579e0>
    """
    if port is None:
        port = const.DEFAULT_PORT if ssl is False else const.DEFAULT_SSL_PORT

    if ssl is True:
        log.debug('Connecting with SSL on {}'.format(hostname))
        imap_account = imaplib.IMAP4_SSL(hostname, port)
    else:
        log.debug('Connecting on {}'.format(hostname))
        imap_account = imaplib.IMAP4(hostname, port)
    imap_account.login(username, password)
    return imap_account


def disconnect(imap_account):
    """Disconnect IMAP account object

    .. versionadded:: 0.1

    Example:

    >>> import imap_cli
    >>> from imap_cli import config
    >>> conf = config.new_context_from_file(section='imap')
    >>> imap_account = imap_cli.connect(**conf)
    >>> imap_account
    <imaplib.IMAP4_SSL instance at 0x7fccd57579e0>
    >>> imap_cli.change_dir(imap_account, 'INBOX')
    >>> imap_cli.disconnect(imap_account)
    """
    log.debug('Disconnecting from {}'.format(imap_account.host))
    if imap_account.state == 'SELECTED':
        imap_account.close()
    if imap_account.state != 'LOGOUT':
        imap_account.logout()


def list_dir(imap_account):
    status, data = imap_account.list()
    if status == const.STATUS_OK:
        for datum in data:
            datum_match = LIST_DIR_RE.match(datum)
            if datum_match is None:
                log.warning('Ignoring "LIST" response part : {}'.format(datum))
                continue
            datum_dict = datum_match.groupdict()
            yield {
                'flags': datum_dict['flags'],
                'delimiter': datum_dict['delimiter'],
                'directory': datum_dict['directory'],
            }


def status(imap_account):
    """Return an interator of directory status.

    Each directory status provide the following keys::

        u'count'    # Number of mail in directory
        u'directory # Name of directory
        u'recent    # Number of recent mail
        u'unseen    # Number of unseen mail

    .. versionadded:: 0.1

    Example:

    >>> import imap_cli
    >>> from imap_cli import config
    >>> conf = config.new_context_from_file(section='imap')
    >>> imap_account = imap_cli.connect(**conf)
    >>> for directory_status in imap_cli.status(imap_account):
    >>>     print directory_status
    """
    for directory_info in list_dir(imap_account):
        status, data = imap_account.status(directory_info['directory'],
                                           '(MESSAGES RECENT UNSEEN)')
        if status != const.STATUS_OK:
            log.warning('Wrong status : {}'.format(repr(data)))
            continue
        status_match = STATUS_RE.match(data[0])
        if status_match is None:
            log.warning('Ignoring directory : {}'.format(repr(data)))
            continue
        group_dict = status_match.groupdict()
        yield {
            'directory': string.decode(group_dict['directory']),
            'unseen': group_dict['mail_unseen'],
            'count': group_dict['mail_count'],
            'recent': group_dict['mail_recent'],
        }
