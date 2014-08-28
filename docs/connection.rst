Connection
==========

Once :ref:configuration is done, you can connect to your imap account


.. function:: connect(hostname, username, password, port=None, ssl=True)

    Return an IMAP account object (see imaplib documentation for details)
    Example::

        import imap_cli
        from imap_cli import config

        conf = config.new_context_from_file(section='imap')
        imap_account = imap_cli.connect(**conf)

    .. versionadded:: 0.1


.. function:: disconnect(imap_account)

    Disconnect IMAP account object
    Example::

        import imap_cli
        from imap_cli import config

        conf = config.new_context_from_file(section='imap')
        imap_account = imap_cli.connect(**conf)
        imap_cli.change_dir(imap_account, 'INBOX'):
        imap_cli.disconnect(imap_account)

    .. versionadded:: 0.1
