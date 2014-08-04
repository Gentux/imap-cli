# -*- coding: utf-8 -*-


"""Functions returning an IMAP account state

Usage: imap-cli-read [options] <mail_uid>

Options:
    -c, --config-file=<FILE>    Configuration file (`~/.config/imap-cli` by default)
    -d, --directory=<DIR>       Directory in wich the search occur
    -s, --save=<DIR>            Save attachement in specified directory
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


import collections
import email
from email import header
import logging
import os
import sys

import docopt

import imap_cli
from imap_cli import config
from imap_cli import const


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)


def display(fetched_mail):
    displayable_parts = list([
        part.get('as_string')
        for part in fetched_mail['parts']
        if part['content_type'] == 'text/plain'
    ])
    if len(displayable_parts) == 0:
        displayable_parts = list([
            part.get('as_string')
            for part in fetched_mail['parts']
            if part['content_type'].startswith('text')
        ])
    output = [
        u'From       : {}'.format(fetched_mail['headers']['From']),
        u'Subject    : {}'.format(fetched_mail['headers']['Subject']),
        u'Date       : {}'.format(fetched_mail['headers']['Date']),
        u'',
        u'\n\n'.join(displayable_parts).strip(),
    ]
    other_parts = [part for part in fetched_mail['parts'] if not part['content_type'].startswith('text')]
    if len(other_parts) > 0:
        output.append('\nAttachement :')
        for part in other_parts:
            if part.get('filename'):
                output.append('    {}'.format(part.get('filename')))

    return u'{}\n'.format(u'\n'.join(output))


def fetch(ctx, message_set=None, message_parts=None):
    """Return mails corresponding to mails_id.

    Keyword arguments:
    message_set     -- Iterable containing mails ID (integers)
    message_parts   -- Iterable of message part names or IMAP protocoles ENVELOP string

    Avalable message_parts are listed in const.MESSAGE_PARTS, for more information checkout RFC3501
    """
    if message_set is None or not isinstance(message_set, collections.Iterable):
        log.error('Can\'t fetch email {}'.format(message_set))
        return None
    if message_parts is None:
        message_parts = ['RFC822']

    request_message_set = ','.join(str(mail_id) for mail_id in message_set)
    request_message_parts = '({})'.format(' '.join(message_parts)
                                          if isinstance(message_parts, collections.Iterable)
                                          else message_parts)
    if ctx.mail_account.state != 'SELECTED':
        log.warning(u'No directory specified, selecting {}'.format(const.DEFAULT_DIRECTORY))
        imap_cli.change_dir(ctx, const.DEFAULT_DIRECTORY)
    typ, data = ctx.mail_account.uid('FETCH', request_message_set, request_message_parts)
    if typ == const.STATUS_OK:
        return data


def get_charset(message, default="ascii"):
    """Get the message charset."""
    if message.get_content_charset():
        return message.get_content_charset()
    if message.get_charset():
        return message.get_charset()

    return default


def read(ctx, mail_uid, directory=None, save_directory=None):
    """Return mail information within a dict."""
    raw_mail = fetch(ctx, [mail_uid])[0]
    if raw_mail is None:
        log.error('Server didn\'t sent this email')
        return None
    mail = email.message_from_string(raw_mail[1])

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

    imap_cli.connect(ctx)
    imap_cli.change_dir(ctx, args['--directory'] or const.DEFAULT_DIRECTORY)
    fetched_mail = read(ctx, args['<mail_uid>'], save_directory=args['--save'])
    if fetched_mail is None:
        log.error("Mail was not fetched, an error occured")
        return 1
    imap_cli.disconnect(ctx)

    sys.stdout.write(display(fetched_mail).encode('utf-8'))
    return 0

if __name__ == '__main__':
    sys.exit(main())
