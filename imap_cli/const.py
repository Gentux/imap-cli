# -*- coding: utf-8 -*-


"""Constant used by Imap_CLI packages """

# IMAP Constant
#
# All those value are documented in RFC 3501
# http://tools.ietf.org/html/rfc3501#section-2.3.2
DEFAULT_DIRECTORY = 'INBOX'
STATUS_OK = 'OK'

IMAP_SPECIAL_FLAGS = [
    'DELETED',
    'SEEN',
    'ANSWERED',
    'FLAGGED',
    'DRAFT',
    'RECENT',
]

FLAG_DELETED = r'\Deleted'
FLAG_SEEN = r'\Seen'
FLAG_ANSWERED = r'\Answered'
FLAG_FLAGGED = r'\Flagged'
FLAG_DRAFT = r'\Draft'
FLAG_RECENT = r'\Recent'


# CLI Constant
DEFAULT_CONFIG_FILE = '~/.config/imap-cli'
