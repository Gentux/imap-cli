Installation
============

To install Imap-CLI, you can use pip::

    pip install imap-cli

Or install it from its source code::

    git clone https://github.com/Gentux/imap-cli.git
    cd imap-cli
    python setup.py install --user


This installation will provide command line tools allowing you to do simple task an IMAP account::

* imap-cli-status: List directories and display count of mail *seen*, *unseen* and *recent* [#f1]_
* imap-cli-list: List mail in specified directory
* imap-cli-search: Search throug specified directory for tag or plain text
* imap-cli-read: Display a mail on standard output
* imap-cli-flag: Set or Unset flag on specified set of mail

Each one of these command has its own *documentation* with the *--help* options

You can also find in Imap-CLI source code 2 bash script. The first one is **imapcli**, it is a little wrapper to help
user with mail command::

    imapcli status
    imapcli list
    imapcli read 23

Is equivalent to::

    imap-cli-status
    imap-cli-list
    imap-cli-read 23

You can also access to help message of the wanted command with::

    imapcli help status

The last script included in source code is **imapcli_bash_completion.sh**. This script give autocompletion to
**imapcli** script. To install it, you just have to do::

    cp imapcli_bash_completion.sh /etc/bash_completion.d/imapcli
    source ~/.bashrc

And then, autocompletion will be available.


.. [#f1] *seen*, *unseen* and *recent* are special tags defined in IMAP's RFC
