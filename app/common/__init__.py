import os
import sys
import yaml
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
    except Exception as ex:
        log("Error loading config: %s: %s" % (config_file, str(ex)))
        err = True

    return config, err


base_project_list_url = os.environ.get("GETUP_API_URL", "http://api.getup.svc:8080").strip('/') + '/api/v1/project/'
try:
    getup_api_username = os.environ["GETUP_API_USERNAME"]
    getup_api_password = os.environ["GETUP_API_PASSWORD"]
except KeyError as ex:
    log("Missing environment variable:", ex)
    sys.exit(1)

def get_project(name):
    project_url = base_project_list_url + name + '/'
    auth = (getup_api_username, getup_api_password)

    res = requests.get(project_url, auth=auth, params={"status":"active"}, allow_redirects=True)

    if not res.ok:
        return None, res
    return res.json(), res


def getup_api_create_project(name, owner)
    data = {'owner':owner, 'name':name, 'family':'default'}
    log('Creating Project "%s"' % data)

    res = requests.post(base_project_list_url, auth=auth, data=data, params={'sync':True})

    if not res.ok:
        return None, res
    return res.json(), res
