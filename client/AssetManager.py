class AssetManager:
    def __init__(self):
        self.assets = {}
    
    def add(self, name, data):
        self.assets[name] = data
