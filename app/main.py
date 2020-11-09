#!/usr/bin/env python

import os
import sys
import yaml
import json
import logging
import importlib
from controllers import log


def load_config(controller_name, controller_type):
    config = {}
    config_file = os.environ.get("CONTROLLER_CONFIG_{}".format(controller_name.upper()), "/config/{}-{}.yaml".format(controller_name, controller_type))

    try:
        with open(config_file, 'r') as cf:
            config = yaml.safe_load(cf)
    except FileNotFoundError as ex:
        pass
    except Exception as ex:
        log("Error loading config[%s:%s]: %s: %s" % (controller_name, controller_type, config_file, str(ex)))
        sys.exit(1)

    return config

if __name__ == "__main__":
    try:
        controller_name, controller_type, *args = *sys.argv[1:3], *sys.argv[3:]
    except ValueError as ex:
        log("Invalid parameters: Usage: %s [controller-name] [controller-type]" % sys.argv[0])
        log("Invalid parameters: Got %s" % sys.argv)
        sys.exit(1)

    try:
        controller = importlib.import_module('controllers.{}'.format(controller_name))
        func = getattr(controller, controller_type)

        config = load_config(controller_name, controller_type)
        state = json.load(sys.stdin)

        result = func(state, config, *args)

        if result is not None:
            print(json.dumps(result))

        sys.stdout.flush()
        sys.stderr.flush()
    except Exception as e:
        log("Error executing controller: %s:%s" % (controller_name, controller_type))
        logging.exception("%s", e)
        sys.exit(1)
