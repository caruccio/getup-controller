#!/usr/bin/env python

import sys
import json
from flatten_dict import flatten as _flatten

try:
    data = json.load(sys.stdin)['object']
    results = json.load(open(sys.argv[1], "r"))['results']
except Exception as e:
    print("No valid tests found")
    sys.exit(0)

def flatten(d):
    return _flatten(d, reducer='dot', keep_empty_types=(dict,), enumerate_types=(list,))

data = flatten(data)
ok = True
for r in [ flatten(i) for i in results ]:
    for k, v in r.items():
        if k not in data:
            print(f'{k} not found')
            ok = False

sys.exit(0 if ok else 1)
