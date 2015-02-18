import logging
_logger = logging.getLogger(__name__)

# Because of pythons module handling this acts like a singleton

_classes = {}

def _loadDefaults():
    from server.Server import Server
    add('Server', Server)
    from server.ServerPlayer import ServerPlayer
    add('ServerPlayer', ServerPlayer)

_loadDefaults()

def get(name):
    try:
        return _classes[name]
    except KeyError as e:
        _logger.error('Cant load class %s: %s', name, e)

def add(name, clas):
    _classes[name] = clas
