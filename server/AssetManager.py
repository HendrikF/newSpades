import os

class AssetManager:
    """ The AssetManager stores a dict (filename => binary content) of
        a folder, which can be sent to the client
    """
    def __init__(self):
        self.assets = {}
    
    def load(self, folder):
        for fn in os.listdir(folder):
            with open(folder + '/' + fn, 'rb') as f:
                data = f.read()
            self.assets[fn] = data
