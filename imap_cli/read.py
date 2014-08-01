# -*- coding: utf-8 -*-


"""Functions returning an IMAP account state

Usage: imap-cli-read [options] <mail_uid>

Options:
    -c, --config-file=<FILE>    Configuration file (`~/.config/imap-cli` by default)
    -s, --save=<DIR>            Save attachement in specified directory
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
import os
import sys

import docopt

from imap_cli import config
from imap_cli import const
from imap_cli.imap import connection
from imap_cli.imap import directories
from imap_cli.imap import fetch


log = logging.getLogger('imap-cli-read')


def get_charset(message, default="ascii"):
    """Get the message charset."""
    if message.get_content_charset():
        return message.get_content_charset()
    if message.get_charset():
        return message.get_charset()

    return default


def read(ctx, mail_uid, directory=None, save_directory=None):
    """Return mail information within a dict."""
    directories.change_dir(ctx, directory or const.DEFAULT_DIRECTORY)

    raw_mail = fetch.fetch(ctx, [mail_uid])[0][1]
    mail = email.message_from_string(raw_mail)

    mail_headers = {}
    for header_name, header_value in mail.items():
        value, encoding = header.decode_header(header_value)[0]
        if encoding is not None:
            value = value.decode(encoding)
        mail_headers[header_name] = value

    message_parts = []
    for part in mail.walk():
        # multipart/* are just containers
        if part.get_content_maintype() == 'multipart':
            continue

        if part.get_content_type().startswith('text'):
            charset = get_charset(part, get_charset(mail))
            message_parts.append({
                'content_type': part.get_content_type(),
                'data': part.as_string(),
                'as_string': part.get_payload(decode=True).decode(charset, 'replace'),
            })
        elif part.get_filename():
            message_parts.append({
                'content_type': part.get_content_type(),
                'filename': part.get_filename(),
                'data': part.get_payload(decode=True),
            })
            if save_directory is not None and os.path.isdir(save_directory):
                attachment_full_filename = os.path.join(save_directory, part.get_filename())
                with open(attachment_full_filename, 'wb') as attachement_file:
                    attachement_file.write(part.get_payload(decode=True))
            elif save_directory is not None:
                log.error('Can\'t save attachment, directory {} does not exist'.format(save_directory))

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
    mail_data = read(ctx, args['<mail_uid>'], save_directory=args['--save'])

    # Display mail
    displayable_parts = list([
        part.get('as_string')
        for part in mail_data['parts']
        if part['content_type'] == 'text/plain'
    ])
    if len(displayable_parts) == 0:
        displayable_parts = list([
            part.get('as_string')
            for part in mail_data['parts']
            if part['content_type'].startswith('text')
        ])
    output = [
        u'From       : {}'.format(mail_data['headers']['From']),
        u'Subject    : {}'.format(mail_data['headers']['Subject']),
        u'Date       : {}'.format(mail_data['headers']['Date']),
        u'',
        u'\n\n'.join(displayable_parts).strip(),
    ]
    other_parts = [part for part in mail_data['parts'] if not part['content_type'].startswith('text')]
    if len(other_parts) > 0:
        output.append('\nAttachement :')
        for part in other_parts:
            if part.get('filename'):
                output.append('    {}'.format(part.get('filename')))
    sys.stdout.write(u'{}\n'.format(u'\n'.join(output)).encode('utf-8'))
    return 0

if __name__ == '__main__':
    sys.exit(main())
