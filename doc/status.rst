Status
======

Status module allow you to get the actual state of your IMAP account. It will tell you for each one of your
directories

* The name of directory
* Total number of mail in this directory
* Number of *Recent* mail in this directory
* Number of *Unseen* mail in this directory


.. function:: status(ctx)

    Return an interator of directory status. Each directory status provide the following key:
        u'count'    # Number of mail in directory
        u'directory # Name of directory
        u'recent    # Number of recent mail
        u'unseen    # Number of unseen mail

    Example::

        import imap_cli
        from imap_cli import config

        ctx = config.new_context_from_file()
        imap_cli.connect(ctx)

        for directory_status in imap_cli.status(ctx):
            print directory_status

    .. versionadded:: 0.1
