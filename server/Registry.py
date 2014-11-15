class Registry(object):
    def __init__(self):
        self._classes = {}
    
    def __call__(self, name, clas=None):
        if clas == None:
            return self._classes[name]
        else:
            self._classes[name] = clas
            return clas
