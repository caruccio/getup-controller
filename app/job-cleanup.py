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

    state = json.load(sys.stdin)
    metadata = state.get('object',{}).get('metadata',{})
    finalizers = metadata.get('finalizers', [])

    if not finalizers:
        return

    if 'orphan' in finalizers:
        log("Removing finalizer from Job {}/{}: 'orphan'".format(metadata['namespace'], metadata['name']))
        finalizers = [ f for f in finalizers if f != 'orphan' ]

    state['object']['metadata']['finalizers'] = finalizers
    sys.stdout.write(json.dumps(state))
    sys.stdout.flush()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("%s", e)
        sys.exit(1)
