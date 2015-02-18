"""
Example script demonstrating how to write scripts.

Please add such a documentation to every script, so people know what it does.
"""
# Import config when needed
from server import config
# Import registry which contains all classes
from server import registry

# every script needs this method
def applyScript():
    # take the class you want to extend
    Server = registry.get('Server')
    # inherit from it
    class HelloServer(Server):
        def start(self, *args, **kw):
            print('Hello!')
            print('Currently these scripts are loaded:')
            # this way you can access the config
            print(config.get('scripts', []))
            # dont forget to call the original function
            super().start(*args, **kw)
    # put the class back
    registry.add('Server', HelloServer)
