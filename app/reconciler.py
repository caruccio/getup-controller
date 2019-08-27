#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import errno
import json
import logging
import requests

def log(*vargs, **kwargs):
	print(file=sys.stderr, *vargs, **kwargs)

def main():
	state = json.load(sys.stdin)
	name = state.get('object',{}).get('metadata',{}).get('name')
	owner = state.get('object',{}).get('metadata',{}).get('annotations',{}).get('getup.io/owner')

	log(state)
	if not owner:
		log("Project %s has no getup.io/owner annotation" % name)
		return

	log('Project "%s" owner sould be "%s"' % (name, owner))

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
			log(res.text)

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		logging.exception("%s", e)
		sys.exit(1)
