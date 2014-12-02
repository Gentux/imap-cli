# -*- coding: utf-8 -*-


"""Constant used by Imap_CLI packages """

# IMAP CLI version number
VERSION = 0.6

# IMAP Constant
#
# All those value are documented in RFC 3501
# http://tools.ietf.org/html/rfc3501#section-2.3.2
DEFAULT_DIRECTORY = 'INBOX'
DEFAULT_PORT = 143
DEFAULT_SSL_PORT = 993
STATUS_OK = 'OK'

IMAP_SPECIAL_FLAGS = [
    'ANSWERED',
    'DELETED',
    'DRAFT',
    'FLAGGED',
    'RECENT',
    'SEEN',
    'UNSEEN',
]

FLAG_DELETED = r'\Deleted'
FLAG_SEEN = r'\Seen'
FLAG_ANSWERED = r'\Answered'
FLAG_FLAGGED = r'\Flagged'
FLAG_DRAFT = r'\Draft'
FLAG_RECENT = r'\Recent'

MESSAGE_PARTS = [
    'BODY',
    'BODYSTRUCTURE',
    'ENVELOPE',
    'FLAGS',
    'INTERNALDATE',
    'RFC822',
    # NOTE(gentux) Functionally equivalent to BODY[], differing in the syntax
    # of the resulting untagged FETCH data.
    'RFC822.HEADER',
    'RFC822.SIZE',
    'RFC822.TEXT',
    'UID',
]

SEARH_CRITERION = [
    'ALL',
    'ANSWERED',
    'BCC <string>',
    'BEFORE <date>',
    'BODY <string>',
    'CC <string>',
    'DELETED',
    'DRAFT',
    'FLAGGED',
    'FROM <string>',
    'HEADER <field-name> <string>',
    'KEYWORD <flag>',
    'LARGER <n>',
    'NEW',
    'NOT <search-key>',
    'OLD',
    'ON <date>',
    'OR <search-key1> <search-key2>',
    'RECENT',
    'SEEN',
    'SENTBEFORE <date>',
    'SENTON <date>',
    'SENTSINCE <date>',
    'SINCE <date>',
    'SMALLER <n>',
    'SUBJECT <string>',
    'TEXT <string>',
    'TO <string>',
    'UID <sequence set>',
    'UNANSWERED',
    'UNDELETED',
    'UNDRAFT',
    'UNFLAGGED',
    'UNKEYWORD <flag>',
    'UNSEEN',
]


# CLI Constant
DEFAULT_CONFIG_FILE = '~/.config/imap-cli'
