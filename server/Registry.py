import logging
logger = logging.getLogger(__name__)

class Registry(object):
    def __init__(self):
        self._classes = {}
    
    def __call__(self, name, clas=None):
        if clas == None:
            try:
                return self._classes[name]
            except KeyError as e:
                logger.error('Cant load class %s: %s', name, e)
        else:
            clas.registry = self
            self._classes[name] = clas
            return clas
