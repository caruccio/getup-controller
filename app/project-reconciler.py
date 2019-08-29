#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import json
import logging
from common import load_config, getup_api_get_project, getup_api_create_project


def main():
    config, err = load_config()
    if err:
        return

    ignore_namespaces = config.get('ignore_namespaces', ['default', 'kube-system'])
    state = json.load(sys.stdin)
    metadata = state.get('object',{}).get('metadata',{})
    annotations = metadata.get('annotations',{})

    name = metadata.get('name')

    if ignore_namespaces and name in ignore_namespaces:
        log("Namespace ignored:", name)
        return

    owner = annotations.get('getup.io/owner') or annotations.get('openshift.io/requester')

    if owner is None:
        log("Namespace %s is missing ownership annotation: either \"getup.io/owner\" or \"openshift.io/requester\" must be supplied." % name)
        return

    if config.get('username_type') == 'email' and '@' not in owner:
        log("Invalid annotation: owner must be an email address: %s" % owner)
        return

    log('Project "%s" owner should be "%s"' % (name, owner))

    project, res = getup_api_get_project(name):
    if project:
        if project['owner'] == owner:
            log('Project "%s" already owned by "%s".' % (name, owner))
        else:
            log('Conflict: project "%s" owned by "%s", but namespace says it should be owned by "%s"' % (name, project['owner'], owner))
        return

    project, res = getup_api_create_project(name, owner)
    if not res.ok:
        log('Error creating Project: %s: %s %s: %s' % (name, res.status_code, res.reason, res.text))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("%s", e)
        sys.exit(1)
