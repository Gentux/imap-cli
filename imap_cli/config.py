# -*- coding: utf-8 -*-


"""Configurator"""


import ConfigParser
import logging
import os


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)


class Ctx(object):
    username = None
    password = None
    hostname = None
    ssl = True


def new_context(config_filename):
    ctx = Ctx()

    config = ConfigParser.RawConfigParser()
    config.read(config_filename)

    ctx.username = config.get('imap', 'username')
    ctx.password = config.get('imap', 'password')
    ctx.hostname = config.get('imap', 'hostname')
    ctx.ssl = config.getboolean('imap', 'ssl')
    return ctx
