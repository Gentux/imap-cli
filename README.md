Imap-CLI
========

Travis :
[![Build Status](https://travis-ci.org/Gentux/imap-cli.svg?branch=master)](https://travis-ci.org/Gentux/imap-cli)

## Description ##

Command line interface for imap account

Imap-CLI aim to provide a dead simple command line tools for the following actions :

* Get imap account status (New mails, mail counting… etc…)
* Get list of directory
* Get list of mails in INBOX (or any other directory)
* Read mail
* Flag mail (Read, Unread, Delete… etc…_
* Reply, Forward, Bounce mails

NOTE: Some of the links below may not work for now. The project is in a development phase.


## Quickstart ##

Install imap-cli with the following command :

```
pip install imap-cli
```

Then, configure imap-cli creating a configuration file in `~/.config/imap-cli` containing :

    imap_account="imaps://imap.gentux.io/"
    imap_pass = 'secret'
    imap_user = userName

If you want to add a minimal autocompletion, you can copy `imapcli_bash_completion.sh` in the file
`/etc/bash_completion.d/imapcli`

## Usage ##

```
Usage:
    imap-cli status
    imap-cli list [<directory>]
    imap-cli read [<directory>] <mail-id>
    imap-cli flag <mail-id>
    imap-cli delete <mail-id>
    imap-cli reply <mail-id>
    imap-cli forward <mail-id>
    imap-cli bounce <mail-id>

    -f, --format=<FMT>    Output format
    -v, --verbose         Generate verbose messages
    -V, --python-verbose  Generate verbose messages in python script
    -h, --help            Show help options.
    --version             Print program version.
----
imap-cli 0.1.0
Copyright (C) 2014 Romain Soufflet
License MIT
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
```

## Further documentation ##

Full documentation available at [LogiCalc](http://logicalc.gentux.io/documentation)

## Legal notices ##

Released under the [MIT License](http://www.opensource.org/licenses/mit-license.php).
