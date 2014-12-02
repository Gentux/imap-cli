#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""Simple REST API for Imap-CLI."""


import copy
import json
import logging
import re
import sys
from wsgiref import simple_server

import six
from webob.dec import wsgify
from webob.exc import status_map

import imap_cli
from imap_cli import config
from imap_cli import const
from imap_cli import fetch
from imap_cli import search


conf = config.new_context_from_file(section='imap')
imap_account = None
log = logging.getLogger('Imap-CLI API')
routes = []


@wsgify
def read_controller(req):
    params = req.params
    inputs = {
        'directory': params.get('directory') or const.DEFAULT_DIRECTORY,
        'uid': req.urlvars.get('uid'),
    }

    if inputs['uid'] is None:
        return 'You need to specify an UID'

    imap_cli.change_dir(imap_account,
                        inputs['directory'] or const.DEFAULT_DIRECTORY)
    fetched_mail = fetch.read(imap_account, inputs['uid'])
    if fetched_mail is None:
        # TODO(rsoufflet) Handle this error with HTTP
        return 'Mail was not fetched, an error occured'

    return_json = copy.deepcopy(fetched_mail)
    for part in return_json['parts']:
        if not part['content_type'].startswith('text'):
            del part['data']
    return json.dumps(return_json, indent=2)


@wsgify
def search_controller(req):
    params = req.params
    inputs = {
        'directory': params.get('directory') or const.DEFAULT_DIRECTORY,
        'tags': params.getall('tag') or None,
        'text': params.get('text') or None,
    }

    imap_cli.change_dir(imap_account, inputs['directory'])

    search_criterion = search.create_search_criterion(tags=inputs['tags'],
                                                      text=inputs['text'])
    mail_set = search.fetch_uids(imap_account,
                                 search_criterion=search_criterion or [])
    mails_info = list(
        search.fetch_mails_info(imap_account, mail_set=mail_set)
    )
    return json.dumps(mails_info, indent=2)


@wsgify
def status_controller(req):
    return json.dumps(sorted(imap_cli.status(imap_account),
                             key=lambda obj: obj['directory']), indent=2)


routings = [
    ('GET', '^/v1/status.json$', status_controller),
    ('GET', '^/v1/list/?$', search_controller),
    ('GET', '^/v1/search/?$', search_controller),
    ('GET', '^/v1/read/(?P<uid>.+)?$', read_controller),
]


@wsgify
def router(req):
    """Dispatch request to controllers."""
    split_path_info = req.path_info.split('/')
    assert not split_path_info[0], split_path_info
    for methods, regex, app, vars in routes:
        if methods is None or req.method in methods:
            match = regex.match(req.path_info)
            if match is not None:
                if getattr(req, 'urlvars', None) is None:
                    req.urlvars = {}
                req.urlvars.update(dict(
                    (name,
                     value.decode('utf-8') if value is not None else None)
                    for name, value in match.groupdict().iteritems()
                ))
                req.urlvars.update(vars)
                req.script_name += req.path_info[:match.end()]
                req.path_info = req.path_info[match.end():]
                return req.get_response(app)
    return status_map[404]()


def main():
    global imap_account
    global routes

    if conf is None:
        return 1
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    for routing in routings:
        methods, regex, app = routing[:3]
        if isinstance(methods, six.string_types):
            methods = (methods,)
        vars = routing[3] if len(routing) >= 4 else {}
        routes.append((methods, re.compile(regex), app, vars))
        log.info('Route {} openned'.format(regex[1:-1]))

    try:
        imap_account = imap_cli.connect(**conf)

        httpd = simple_server.make_server('127.0.0.1', 8000, router)
        log.info('Serving on http://127.0.0.1:8000')
        httpd.serve_forever()
    except KeyboardInterrupt:
        log.info('Interupt by user, exiting')

    return 0

if __name__ == '__main__':
    sys.exit(main())
