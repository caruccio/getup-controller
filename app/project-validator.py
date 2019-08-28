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


def print_response(allowed, reason='', code=200):
	res = {
		"allowed": allowed,
		"status": {
			"code": code,
			"reason": reason
		}
	}

	json.dump(res, sys.stdout)


def load_config():
	config_file = os.environ.get("CONTROLLER_CONFIG", "/config/controller.yaml")
	config = {}
	err = False

	try:
		if os.path.exists(config_file):
			with open(config_file, 'r') as cf:
				config = yaml.safe_load(cf)
#				log('Loaded config from', config_file)
	except Exception as ex:
		log("Error loading config: %s: %s" % (config_file, str(ex)))
		err = True

	return config, err


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
		log("Namespace ignored")
		print_response(True)
		return

	owner = annotations.get('getup.io/owner') or annotations.get('openshift.io/requester')

	if owner is None:
		allowed = False
		reason = "Missing ownership annotation: either \"getup.io/owner\" or \"openshift.io/requester\" must be supplied."
	elif config.get('username_type') == 'email' and '@' not in owner:
		allowed = False
		reason = "Invalid annotation: owner must be an email address."

	log("{}: {}".format(reason, name))

	print_response(allowed, reason)


if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		logging.exception("%s", e)
		sys.exit(1)
