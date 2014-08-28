Configuration
=============


Imap-CLI need to have information about your IMAP account to connect to it. And to do so, it provide several ways to
retrieve those configurations.


Loading default config
----------------------

Load an *empty* configuration dictionnary with default values listed in file *config-example.ini*::

    from imap_cli import config
    conf = config.new_context()

This is usually not what you want, this configuration method is used by unit tests


Loading config from configuration file
--------------------------------------

If you intend to use command line tools, this is definitely the best method.

Each command line tools will provide the options *-c, --config-file* in order to let you specify your very own config
file. It is also helpful to have multiple file in case you have multiple IMAP account.

There is a default configuration file wich will be used if no one is specified, it's **~/.config/imapcli**.

This file can contains the following options::

    [imap]
    hostname = imap.example.org
    username = username
    password = secret
    ssl = True

    [display]
    format_list =
        ID:         {mail_id}
        Flags:      {flags}
        From:       {from}
        To:         {to}
        Date:       {date}
        Subject:    {subject}
    format_status = {directory:>20} : {count:>5} Mails - {unseen:>5} Unseen - {recent:>5} Recent
    limit = 10


.. warning::

    Don't forget to set correct permission on these files !
    It will store your IMAP Account password, allow only your own user to read this file


Loading config from python code
-------------------------------

If you need to connect and retrieve mail information with a python script, you can load any config file

.. function:: new_context_from_file(config_filename=None, section=None)

    Open and read *config_filename* (`~/.config/imapcli` by default) and parse configuration from it.

    Example::

        from imap_cli import config
        config_file = '~/.config/imapcli'
        conf = config.new_context_from_file(config_file)

    You can also load a single section of this configuration file::

        from imap_cli import config
        config_file = '~/.config/imapcli'
        conf = config.new_context_from_file(config_file, section='imap')

    .. versionadded:: 0.1


But you can also use a python sructure to store your information and load it from a *dict*. In fact, config it's just a
dict, the following method will just "complete" your dict.

.. function:: new_context(config=None)

    Read configuration from *config* dict.

    Example::

        from imap_cli import config
        conf = config.new_context({
            'hostname': 'another.imap-server.org',
            'password': 'another.secret',
            })

    .. versionadded:: 0.1

Every missing key will take the default value.
