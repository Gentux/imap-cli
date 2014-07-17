# -*- coding: utf-8 -*-


"""Configurator"""


import ConfigParser
import logging
import os

from imap_cli import const


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)


class Ctx(object):
    # Account
    username = None
    password = None
    hostname = None
    ssl = True
    # Display
    limit = None
    format_status = None
    format_list = None


def new_context_from_file(config_filename=None):
    ctx = Ctx()
    if config_filename is None:
        config_filename = const.DEFAULT_CONFIG_FILE
    config_filename = os.path.abspath(os.path.expanduser(os.path.expandvars(config_filename)))

    config = ConfigParser.RawConfigParser()
    config.read(config_filename)
    log.debug("Reading configuration file '{}'".format(config_filename))

    # Account
    ctx.username = config.get('imap', 'username')
    ctx.password = config.get('imap', 'password')
    ctx.hostname = config.get('imap', 'hostname')
    ctx.ssl = config.getboolean('imap', 'ssl')

    # Display
    if config.has_option('display', 'limit'):
        ctx.limit = config.getint('display', 'limit')

    ctx.format_status = config.get('display', 'format_status') \
        if config.has_option('display', 'format_status') \
        else u'{directory}:{unseen} Unseen - {count} Mails - {recent} Recent'

    ctx.format_list = config.get('display', 'format_list') \
        if config.has_option('display', 'format_list') \
        else u'From: {mail_from:<30} To: {to:<20} Subjetc: {subject}'
    return ctx
