Search
======

This module aim to provide all search options available in IMAP protocoles without having to read the entire IMAP RFC.

For now, you can do following searches

* Simple listing of all mails
* Search By tag
* Search By flag
* Search full text in mails body

In v0.4, following options should be available

* By subject
* By mail adresse, in *bcc*, *cc*, *from* or *to* header fields
* By date, *before*, *after* or *on* a particular date
* By header, given a pair of haeder name and header value to search
* By size, *larger* or *smaller* than given value

Moreover, a few logical combination of the above

* Not
* Or


.. function:: prepare_search(ctx, directory=None, tags=None, text=None):

    Keywords arguments:
        directory: Name of directory in wich the search is done ("INBOX" by default)
        tags: An iterable of tags string
        text: A string to search trhough all mails

    Return a list of IMAP search criterion

    Example::

        from imap_cli import config
        from imap_cli.imap import connection
        from imap_cli import search

        ctx = config.new_context_from_file()
        connection.connect(ctx)

        print search.prepare_search(ctx, directory="Perso", tags=["family", "unseen"])

    .. versionadded:: 0.2


This method is a wrapper for **imap_cli.imap.search** methods.
