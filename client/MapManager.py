from client.DrawableMap import DrawableMap

class MapManager:
    def __init__(self, maxFPS=60, farplane=100):
        self.maxFPS = maxFPS
        self.farplane = farplane
    
    def fromBytes(self, data):
        return DrawableMap(self.maxFPS, self.farplane).importBytes(data)
