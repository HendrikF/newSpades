"""
Loads the config file and can be imported by modules needing the config.

I recommend to read values with config.get(key, default) to avoid KeyErrors.
"""
import json
import os

import logging
_logger = logging.getLogger()

_configname = 'config.txt'
_config = {
    'scripts': []
}
if not os.path.isfile(_configname):
    try:
        with open(_configname, 'w') as f:
            json.dump(_config, f, sort_keys=True, indent=2)
    except IOError as e:
        _logger.warning('Cant write configfile %s: %s', _configname, e)
else:
    try:
        with open(_configname) as f:
            _config.update(json.load(f))
    except ValueError as e:
        _logger.error('Syntax error in config detected: %s', e)
    except IOError as e:
        _logger.warning('Cant read configfile %s: %s', _configname, e)

get = _config.get
