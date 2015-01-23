class Event(object):
    def __init__(self):
        self.handlers = []
    
    def attach(self, func):
        self.handlers.append(func)
    
    def __call__(self, *args):
        for handler in self.handlers:
            handler(*args)
