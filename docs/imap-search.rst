Search
======

This module aim to provide all search options available in IMAP protocoles without having to read the entire IMAP RFC.

For now, you can do following searches

* Simple listing of all mails
* Search by tag
* Search by flag
* Search full text in mails body
* search by subject
* search by mail adresse, in *bcc*, *cc*, *from* or *to* header fields
* search by date, *before*, *after* or *on* a particular date
* search by header, given a pair of haeder name and header value to search
* search by size, *larger* or *smaller* than given value

Moreover, a few logical combination of the above

* Not
* Or

.. automodule:: imap_cli.search
    :members:
