# -*- coding: utf-8 -*-


"""Functions returning an IMAP account state

Usage: imap-cli-read [options] <mail_uid>

Options:
    -c, --config-file=<FILE>    Configuration file (`~/.config/imap-cli` by default)
    -v, --verbose               Generate verbose messages
    -h, --help                  Show help options.
    --version                   Print program version.

----
imap-cli-read 0.3
Copyright (C) 2014 Romain Soufflet
License MIT
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"""


import email
from email import header
import logging
import sys

import docopt

from imap_cli import config
from imap_cli import const
from imap_cli.imap import connection
from imap_cli.imap import directories
from imap_cli.imap import fetch


log = logging.getLogger('imap-cli-read')


def read(ctx, mail_uid, directory=None):
    """Return mail information within a dict"""
    assert directories.change_dir(ctx, directory or const.DEFAULT_DIRECTORY) >= 0

    raw_mail = fetch.fetch(ctx, [mail_uid])[0][1]
    mail = email.message_from_string(raw_mail)

    mail_headers = {}
    for header_name, header_value in mail.items():
        value, encoding = header.decode_header(header_value)[0]
        if encoding is not None:
            value = value.decode(encoding)
        elif not isinstance(value, unicode):
            value = unicode(value)
        mail_headers[header_name] = value

    message_parts = []
    for part in mail.walk():
        # multipart/* are just containers
        if part.get_content_maintype() == 'multipart':
            continue

        if part.get_content_type().startswith('text'):
            message_parts.append({
                'content_type': part.get_content_type(),
                'data': part.as_string(),
            })
        elif part.get_filename():
            message_parts.append({
                'content_type': part.get_content_type(),
                'filename': part.get_filename(),
                'data': part.get_payload(decode=True),
            })

    return {
        'headers': mail_headers,
        'parts': message_parts,
    }


def main():
    args = docopt.docopt('\n'.join(__doc__.split('\n')[2:]))
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.WARNING,
        stream=sys.stdout,
    )

    ctx = config.new_context_from_file(args['--config-file'])

    connection.connect(ctx)
    mail_data = read(ctx, args['<mail_uid>'])

    sys.stdout.write('\n'.join([
        u'From       : {}'.format(mail_data['headers']['From']),
        u'Subject    : {}'.format(mail_data['headers']['Subject']),
        u'Date       : {}'.format(mail_data['headers']['Date']),
        u'',
        u'\n\n'.join([part['data'] for part in mail_data['parts'] if part['content_type'] == 'text/plain']),
    ]))
    other_parts = [part for part in mail_data['parts'] if not part['content_type'].startswith('text')]
    if len(other_parts) > 0:
        sys.stdout.write('\nAttachement :\n')
        for part in other_parts:
            sys.stdout.write('    ')
            sys.stdout.write(part.get('filename', part.get('content_type', '')))
            sys.stdout.write('\n')

    return 0

if __name__ == '__main__':
    sys.exit(main())
