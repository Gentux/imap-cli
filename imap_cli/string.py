# -*- coding: utf-8 -*-


"""Encoding and Decoding function for special UTF-7 encoding used bu IMAP"""


import binascii

import six


def modified_base64(string):
    # TODO(rsoufflet) Found this code somewhere on internet, this is crapy,
    # need to work on that
    string = string.encode('utf-16be')
    base64_string = six.text_type(binascii.b2a_base64(string))
    base64_string = base64_string.rstrip('\\n\'').lstrip('b\'')
    return base64_string.rstrip('\n=').replace('/', ',')


def encode(string):
    r = []
    other_chars = []
    for character in string:
        ordC = ord(character)
        if 0x20 <= ordC <= 0x7e:
            if other_chars:
                r.append('&{0}-'.format(modified_base64(''.join(other_chars))))
            del other_chars[:]
            r.append(character)
            if character == '&':
                r.append('-')
        else:
            other_chars.append(character)
    if other_chars:
        r.append('&{0}-'.format(modified_base64(''.join(other_chars))))
        del other_chars[:]
    return ''.join(r)


def modified_unbase64(string):
    b = binascii.a2b_base64(string.replace(',', '/') + '===')
    return six.text_type(b, 'utf-16be')


def decode(string):
    r = []
    decode_chars = []
    for character in string:
        if character == '&' and not decode_chars:
            decode_chars.append('&')
        elif character == '-' and decode_chars:
            if len(decode_chars) == 1:
                r.append('&')
            else:
                r.append(modified_unbase64(''.join(decode_chars[1:])))
            decode_chars = []
        elif decode_chars:
            decode_chars.append(character)
        else:
            r.append(character)
    if decode_chars:
        r.append(modified_unbase64(''.join(decode_chars[1:])))
    bin_str = ''.join(r)
    return bin_str
