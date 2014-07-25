Imap-CLI
========

Travis :
[![Build Status](https://travis-ci.org/Gentux/imap-cli.svg?branch=master)](https://travis-ci.org/Gentux/imap-cli)

## Description ##

Command line interface and API for imap accounts. It provide the following actions through a minial python
library:

* Get imap account status (New mails, mail counting… etc…)
* Get list of mails in INBOX (or any other directory)
* Search through mail
* Read mail
* Flag mail (Read, Unread, Delete… etc…_

You can read about my initial motivation to write this software
[here](http://romain.soufflet.io/bash/2014/07/11/Mail-Mail-and-mail-again-my-head-will-explode.html).

A presentation of Imap-CLI is available [here](http://gentux.github.io/imap-cli/)


## Quickstart ##

Install imap-cli with the following command :

```
pip install imap-cli
```

Then, configure imap-cli creating a configuration file in `~/.config/imap-cli` containing :

    imap_account="imaps://imap.gentux.io/"
    imap_pass = 'secret'
    imap_user = userName

If you want to add a minimal autocompletion, you can copy **imapcli_bash_completion.sh** in the file
**/etc/bash_completion.d/imapcli** or simply source.


## Usage CLI ##

    Usage: imapcli [options] <command> [<args>]

    Available commands are:
        status      List unseen, recent and total number of mail per directory in IMAP account
        list        List mail within a specified directory
        search      Search for mail
        read        Display Header and Body of specified mail(s)
        flag        Set or unset flag on specified mail(s)

    Options:
        -v, --verbose           Generate verbose messages
        -h, --help              Show help options
        --version               Print program version

    See 'imapcli help <command>' to get further information about specified command

    ----
    imap-cli 0.3
    Copyright (C) 2014 Romain Soufflet
    License MIT
    This is free software: you are free to change and redistribute it.
    There is NO WARRANTY, to the extent permitted by law.


## Usage Python API ##

This is work in progress. Python API aims to be as complete as possible to ease the creation of API and clients.

    from imap_cli import config
    from imap_cli.imap import connection
    from imap_cli import status

    config_filename = '~/.config/imap-cli'
    ctx = config.new_context_from_file(config_filename)

    connection.connect(ctx)
    for directory_info in status.status(ctx):
        print ctx.format_status.format(**directory_info)


## Configuration ##

The file **config-example.ini** show you available parameters and their default value when they have one.

You can also find in this file some comment describing all possibilities about each parameters.

File configuration is not the only possibility. As the package imap-cli is designed to be an API, all configuration data
are shared in a *context* object. You can load this context progamatically if you want.


## Contributing ##

All contributions are welcome.

If your patche(s) contain new features, ensure you have written correspondig unit test. Also ensure all tests pass using
*tox*

You can also [open new issues](https://github.com/Gentux/imap-cli/issues/new) for questions, bugs or new feature.


## Roadmap ##

The actual version of Imap-CLI is 0.3.

Impa-CLI aims to map all IMAP protocols functionnality within a simple python API, and points in development are listed
below

### v0.1 ###

* Status (list directory and new mail per directory)
* List (list content of a directory
* Read (display content of specified email)

### v0.2 ###

* Basic Search (search amongs tag, subject and full text within mails)
* Tags (Add or Remove tag from mails)

### v0.3 (current) ###

* Rewrite code structure to ease the creation of API
* Map all feature on REST API (separate project)
* Documentation

### v0.4 ###

* Advanced Search


## Creator ##

### Romain Soufflet ###

* [Twitter](http://twitter.com/Romain_Soufflet)
* [Github](http://github.com/Gentux)
* [http://romain.soufflet.io](http://romain.soufflet.io)


## Further documentation ##

Full documentation available [here](http://imap-cli.readthedocs.org/en/latest/).


## Legal notices ##

Released under the [MIT License](http://www.opensource.org/licenses/mit-license.php).
