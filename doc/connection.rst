Connection
==========

Once :ref:configuration is done, you can connect to your imap account


.. function:: connect(ctx)

    Set IMAP account object in context
    Example::

        import imap_cli
        from imap_cli import config

        ctx = config.new_context_from_file()
        imap_cli.connect(ctx)

    .. versionadded:: 0.1


.. function:: disconnect(ctx)

    Disconnect IMAP account object in context
    Example::

        import imap_cli
        from imap_cli import config

        ctx = config.new_context_from_file()
        imap_cli.connect(ctx)
        ctx.mail_account.select('INBOX')
        imap_cli.disconnect(ctx)

    .. versionadded:: 0.1
