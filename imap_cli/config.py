# -*- coding: utf-8 -*-


"""Configurator"""


import codecs
import itertools
import logging
import os

from six.moves import configparser

from imap_cli import const


app_name = os.path.splitext(os.path.basename(__file__))[0]
DEFAULT_CONFIG = {
    u'hostname': u'imap.example.org',
    u'username': u'username',
    u'password': u'secret',
    u'ssl': True,

    u'limit': 10,
    u'format_list': u''.join([
        u'\n',
        u'ID:         {uid}\n',
        u'Flags:      {flags}\n',
        u'From:       {mail_from}\n',
        u'To:         {to}\n',
        u'Date:       {date}\n',
        u'Subject:    {subject}',
    ]),
    u'format_status': u'{directory:>20} : {count:>5} Mails - {unseen:>5} Unseen - {recent:>5} Recent'
}
log = logging.getLogger(app_name)


def new_context(config=None):
    if config is None:
        log.debug(u'Loading default configuration')
        config = DEFAULT_CONFIG
    else:
        log.debug(u'Loading custom configuration')

    return dict(
        (key, value)
        for key, value in itertools.chain(DEFAULT_CONFIG.items(), config.items())
    )


def new_context_from_file(config_filename=None, encoding='utf-8', section=None):
    if config_filename is None:
        config_filename = const.DEFAULT_CONFIG_FILE
    config_filename = os.path.abspath(os.path.expanduser(os.path.expandvars(config_filename)))
    log.debug(u'Reading configuration file \'{}\''.format(config_filename))

    config_reader = configparser.RawConfigParser()
    with codecs.open(config_filename, 'r', encoding) as config_file:
        config_reader.readfp(config_file)

    config = {}
    if section is None or section == 'imap':
        # Account
        config['username'] = config_reader.get('imap', 'username')
        config['password'] = config_reader.get('imap', 'password')
        config['hostname'] = config_reader.get('imap', 'hostname')
        config['ssl'] = config_reader.getboolean('imap', 'ssl')

    if section is None or section == 'display':
        # Display
        if config_reader.has_option('display', 'limit'):
            config['limit'] = config_reader.getint('display', 'limit')

        config['format_status'] = config_reader.get('display', 'format_status') \
            if config_reader.has_option('display', 'format_status') \
            else u'{directory}:{unseen} Unseen - {count} Mails - {recent} Recent'

        config['format_list'] = config_reader.get('display', 'format_list') \
            if config_reader.has_option('display', 'format_list') \
            else u'From: {mail_from:<30} To: {to:<20} Subject: {subject}'
    return config
