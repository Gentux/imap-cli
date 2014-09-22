Imap-CLI
========

[![Build Status](https://travis-ci.org/Gentux/imap-cli.svg?branch=master)](https://travis-ci.org/Gentux/imap-cli)
[![Documentation Status](https://readthedocs.org/projects/imap-cli/badge/?version=master)](https://readthedocs.org/projects/imap-cli/?badge=master)

## Description ##

Command line interface and API for imap accounts. It provide the following actions through a minial python
library:

* Get imap account status (New mails, mail counting… etc…)
* Get list of mails in INBOX (or any other directory)
* Search through mail
* Read mail
* Flag mail (Read, Unread, Delete, etc…)

You can read about my initial motivation to write this software
[here](http://romain.soufflet.io/bash/2014/07/11/Mail-Mail-and-mail-again-my-head-will-explode.html).

A presentation of Imap-CLI is available [here](http://gentux.github.io/imap-cli/)


## Quickstart ##

Install imap-cli with the following command :

```
pip install imap-cli
```

Then, configure imap-cli creating a configuration file in `~/.config/imap-cli` containing :

    hostname = imap.example.org
    username = username
    password = secret
    ssl = True

If you want to add a minimal autocompletion, you can copy **imapcli_bash_completion.sh** in the file
**/etc/bash_completion.d/imapcli** or simply source.

If you want to benefit from the wrapper script described below, copy the script `imapcli` in your PATH


## Usage CLI ##

    Usage: imapcli [options] <command> [<command_options>...]

    Available commands are:
        status      List unseen, recent and total number of mail per directory in IMAP account
        list        List mail within a specified directory
        search      Search for mail
        read        Display Header and Body of specified mail(s)
        flag        Set or unset flag on specified mail(s)

    Options:
        -h, --help              Show help options
        --version               Print program version

    See 'imapcli help <command>' to get further information about specified command"

    ----
    imap-cli 0.6
    Copyright (C) 2014 Romain Soufflet
    License MIT
    This is free software: you are free to change and redistribute it.
    There is NO WARRANTY, to the extent permitted by law.


## Usage Python API ##

This is work in progress, so API migth change. Python API aims to be as complete as possible to ease the creation of
API, caching system and clients. You can find example in `examples` directory.

    import imap_cli
    from imap_cli import config

    config_filename = '~/.config/imap-cli'
    connect_conf = config.new_context_from_file(config_filename, section='imap')
    display_conf = config.new_context_from_file(config_filename, section='display')

    imap_account = imap_cli.connect(**connect_conf)
    for directory_info in imap_cli.status(imap_account):
        print display_conf['format_status'].format(**directory_info)


## Configuration ##

The file **config-example.ini** show you available parameters and their default value when they have one.

You can also find in this file some comment describing all possibilities about each parameters.

File configuration is not the only possibility. As the package imap-cli is designed to be an API, all configuration data
are shared in a *context* object. You can load this context progamatically if you want.


## Further documentation ##

Full documentation available [here](http://imap-cli.readthedocs.org/en/master/).


## Contributing ##

All contributions are welcome.

If your patche(s) contain new features, ensure you have written correspondig unit test. Also ensure all tests pass using
*tox*

You can also [open new issues](https://github.com/Gentux/imap-cli/issues/new) for questions, bugs or new feature.


## Roadmap ##

The actual version of Imap-CLI is 0.6.

Imap-CLI aims to map all IMAP protocols functionnality within a simple python API, and points in development are listed
below

### v0.1 ###

* Status (list directory and new mail per directory)
* List (list content of a directory
* Read (display content of specified email)

### v0.2 ###

* Basic Search (search amongs tag, subject and full text within mails)
* Tags (Add or Remove tag from mails)

### v0.3 ###

* Rewrite code structure to ease the creation of API
* Documentation

### v0.4 ###

* Advanced Search
* Use UID instead of volatil mails id
* Read all type of mail and handle attachments

### v0.5 ###

* List mail by thread
* Display threads

### v0.6 (current) ###

* Clean up and complete documentation
* Clean up code
* Generate Debian package
* Test coverage > 90%


## Creator ##

### Romain Soufflet ###

* [Twitter](http://twitter.com/Romain_Soufflet)
* [Github](http://github.com/Gentux)
* [http://romain.soufflet.io](http://romain.soufflet.io)


## Legal notices ##

Released under the [MIT License](http://www.opensource.org/licenses/mit-license.php).
