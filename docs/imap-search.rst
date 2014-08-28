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


.. function:: create_search_criterion(tags=None, text=None):

    Keywords arguments:
        tags: An iterable of tags string
        text: A string to search trhough all mails

    Return a list of IMAP search criterion

    Example::

        import imap_cli
        from imap_cli import search

        print search.create_search_criterion(ctx, directory="Perso", tags=["family", "unseen"])

    .. versionadded:: 0.2


.. function:: fetch_uids(imap_account, search_criterion=None):

    Keywords arguments:
        imap_account: Imap lib object
        search_criterion: A list of IMAP criterion produced by search module helpers

    Return a list of mail uid

    Example::

        import imap_cli
        from imap_cli import search

        imap_account = imap_cli.connect('hostname', 'username', 'password')
        search_criterion = search.create_search_criterion(tags=["family", "unseen"])

        mails_uid = search.fetch_uids(imap_account, search_criterion=search_criterion)

    .. versionadded:: 0.2


.. function:: fetch_mails_info(imap_account, mail_set=None, decode=True, limit=None):

    Keywords arguments:
        imap_account: Imap lib object
        mail_set: A list of mail uid to retrieve
        decode: Decode mail content
        limit: Return a limited number of mails

    Return a list of dict with minimal information about mails

    Example::

        import imap_cli
        from imap_cli import search

        imap_account = imap_cli.connect('hostname', 'username', 'password')
        search_criterion = search.create_search_criterion(tags=["family", "unseen"])

        mails_uid = search.fetch_uids(imap_account, search_criterion=search_criterion)
        mails_info = search.fetch_mails_info(imap_account, mails_uid)

    .. versionadded:: 0.2
