#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Command line interface for imap account

Set of high level mail management functions. All managed in CLI"""


import setuptools


setuptools.setup(
    author="Romain Soufflet",
    author_email="romain@soufflet.io",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
    ],
    description=('\n'.join(__doc__.split('\n')[2:])),
    entry_points={
        'console_scripts': [
            'imap-api=imap_cli.scripts.imap_api:main',
            'imap-cli-copy=imap_cli.copy:main',
            'imap-cli-delete=imap_cli.delete:main',
            'imap-cli-flag=imap_cli.flag:main',
            'imap-cli-list=imap_cli.list_mail:main',
            'imap-cli-read=imap_cli.fetch:main',
            'imap-cli-search=imap_cli.search:main',
            'imap-cli-status=imap_cli.summary:main',
            'imap-notify=imap_cli.scripts.imap_notify:main',
            'imap-shell=imap_cli.scripts.imap_shell:main',
        ],
    },
    install_requires=[
        "docopts>=0.6",
        "mock>=1.0.1",
        "future",
    ],
    keywords="imap cli high level",
    license="MIT License",
    long_description=__doc__.split('\n')[0],
    name="Imap-CLI",
    packages=setuptools.find_packages(),
    platforms=["OS Independent"],
    scripts=["imapcli"],
    test_suite="nose.collector",
    url="http://gentux.github.io/imap-cli/",
    version="0.7",
)
