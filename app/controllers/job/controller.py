#!/usr/bin/env python

from __future__ import print_function
from controllers import log

def reconcile(state, config, *args):
    metadata = state.get('object',{}).get('metadata',{})
    finalizers = metadata.get('finalizers', [])

    if not finalizers:
        return

    if 'orphan' in finalizers:
        log("Removing finalizer from Job {}/{}: 'orphan'".format(metadata['namespace'], metadata['name']))
        finalizers = [ f for f in finalizers if f != 'orphan' ]

    state['object']['metadata']['finalizers'] = finalizers
    return state
