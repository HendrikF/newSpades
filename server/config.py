"""
Loads the config file and can be imported by modules needing the config.

Values are stored in the global 'config' dict.
I recommend to read values with config.get(key, default) to avoid KeyErrors.
"""
import json
import os

import logging
logger = logging.getLogger()

configname = 'config.txt'
config = {
    'scripts': []
}
if not os.path.isfile(configname):
    try:
        with open(configname, 'w') as f:
            json.dump(config, f, sort_keys=True, indent=2)
    except IOError as e:
        logger.warning('Cant write configfile %s: %s', configname, e)
else:
    try:
        with open(configname) as f:
            config.update(json.load(f))
    except ValueError as e:
        logger.error('Syntax error in config detected: %s', e)
    except IOError as e:
        logger.warning('Cant read configfile %s: %s', configname, e)
