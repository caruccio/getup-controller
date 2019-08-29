#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import json
import logging
from common import log, load_config


def print_response(allowed, reason='', code=200):
    res = {
        "allowed": allowed,
        "status": {
            "code": code,
            "reason": reason
        }
    }

    json.dump(res, sys.stdout)


def main():
    allowed = True
    reason = "Namespace accepted"

    config, err = load_config()
    if err:
        print_response(True)
        return

    ignore_namespaces = config.get('ignore_namespaces', ['default', 'kube-system'])
    state = json.load(sys.stdin)
    metadata = state.get('object',{}).get('metadata',{})
    annotations = metadata.get('annotations',{})

    name = metadata.get('name')

    if ignore_namespaces and name in ignore_namespaces:
        log("Namespace ignored:", name)
        print_response(True)
        return

    owner = annotations.get('getup.io/owner') or annotations.get('openshift.io/requester')

    if owner is None:
        allowed = False
        reason = "Missing ownership annotation: either \"getup.io/owner\" or \"openshift.io/requester\" must be supplied."
    elif config.get('username_type') == 'email' and '@' not in owner:
        allowed = False
        reason = "Invalid annotation: owner must be an email address: %s" % owner

    log("{}: {}".format(reason, name))

    print_response(allowed, reason)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("%s", e)
        sys.exit(1)
