Connection
==========

Once :ref:configuration is done, you can connect to your imap account


.. function:: connect(ctx)

    Set IMAP account object in context
    Example::

        from imap_cli import config
        from imap_cli.imap import connection

        ctx = config.new_context_from_file()
        connection.connect(ctx)

    .. versionadded:: 0.1


.. function:: disconnect(ctx)

    Disconnect IMAP account object in context
    Example::

        from imap_cli import config
        from imap_cli.imap import connection

        ctx = config.new_context_from_file()
        connection.connect(ctx)
        ctx.mail_account.select('INBOX')
        connection.disconnect(ctx)

    .. versionadded:: 0.1
