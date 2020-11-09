import itertools
import os
import json
from controllers import log

def reconcile(state, config, *args):
    metadata = state.get('object',{}).get('metadata',{})
    annotations = metadata.get('annotations',{})
    labels = metadata.get('labels',{})
    name = metadata.get('name')
    uid = metadata.get('uid')
    taints = state.get('object',{}).get('spec',{}).get('taints', [])

    # copy label to annotation
    for prefix_name, value in labels.items():
        if not prefix_name.startswith('annotation.getup.io/'):
            continue
        _, name = prefix_name.split('/')
        if not name:
            continue
        log('Added annotation: {}={}'.format(name, value))
        annotations[name] = value

    # copy annotation to label
    for prefix_name, value in annotations.items():
        if not prefix_name.startswith('label.getup.io/'):
            continue
        _, name = prefix_name.split('/')
        if not name:
            continue
        log('Added label: {}={}'.format(name, value))
        labels[name] = value

    # taint from labels or annotations
    for prefix_name, value in itertools.chain(labels.items(), annotations.items()):
        if not prefix_name.startswith('taint.getup.io/'):
            continue
        _, name = prefix_name.split('/')
        if not name:
            continue
        try:
            taint = json.loads(value)
        except json.decoder.JSONDecodeError:
            tmp = value.split(':')
            taint = {
                'key': name,
                'value': tmp[0],
                'effect': tmp[1] if len(tmp) > 1 else os.environ.get('DEFAULT_NODE_TAINT_EFFECT', 'NoSchedule'),
            }

        found = False
        for t in taints:
            if t['effect'] == taint['effect'] and t['key'] == taint['key'] and t['value'] == taint['value']:
                found = True
                break
        if found:
            continue
        log('Added taint: {}'.format(taint))
        taints.append(taint)

    state['object']['spec']['taints'] = taints
    state['object']['metadata']['annotations'] = annotations
    state['object']['metadata']['labels'] = labels

    return state
