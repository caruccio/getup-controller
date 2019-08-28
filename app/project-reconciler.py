#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import errno
import json
import yaml
import logging
import requests


def log(*vargs, **kwargs):
    print(file=sys.stderr, *vargs, **kwargs)


def load_config():
    config_file = os.environ.get("CONTROLLER_CONFIG", "/config/controller.yaml")
    config = {}
    err = False

    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as cf:
                config = yaml.safe_load(cf)
#                log('Loaded config from', config_file)
    except Exception as ex:
        log("Error loading config: %s: %s" % (config_file, str(ex)))
        err = True

    return config, err


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

    project_list_url = os.environ["GETUP_API_URL"].strip('/') + '/api/v1/project/'
    project_url = project_list_url + name + '/'
    auth = (os.environ["GETUP_API_USERNAME"], os.environ["GETUP_API_PASSWORD"])

    res = requests.get(project_url, auth=auth, params={"status":"active"}, allow_redirects=True)
    project = res.json()

    if res.status_code == 200:
        if project['owner'] == owner:
            log('Project "%s" already owned by "%s".' % (name, owner))
        else:
            log('Conflict: project "%s" owned by "%s", but namespace says it should be owned by "%s"' % (name, project['owner'], owner))
        return

    if res.status_code == 404:
        data = {'owner':owner, 'name':name, 'family':'default'}
        log('Will create project with "%s"' % data)
        res = requests.post(project_list_url, auth=auth, data=data, params={'sync':True})
        log('Project create "%s" returned: %s %s' % (name, res.status_code, res.reason))

        if not res.ok:
            log('Error creating billing Project:', res.text)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("%s", e)
        sys.exit(1)
