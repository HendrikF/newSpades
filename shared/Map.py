import logging
logger = logging.getLogger(__name__)

FACES = [
    ( 0, 1, 0), # UP
    ( 0,-1, 0), # DOWN
    (-1, 0, 0), # FRONT
    ( 1, 0, 0), # BACK
    ( 0, 0, 1), # RIGHT
    ( 0, 0,-1), # LEFT
]

class Map(object):
    """Map represents the world and provides methods for adding/removing blocks"""
    def __init__(self):
        # dict[(x, y, z)] = (r, g, b)
        self.world = {}
    
    def load(self):
        self._load()
    
    def _load(self):
        for x in range(0, 50):
            self.addBlock((x, 1, 0), (1, 1, 0), immediate=False)
            for z in range(0, 50):
                self.addBlock((x, 0, z), (0, 1, 0), immediate=False)
        self.addBlock((1, 0, 0), (1, 0, 0), immediate=False)
        self.addBlock((0, 1, 0), (0, 1, 0), immediate=False)
        self.addBlock((0, 0, 1), (0, 0, 1), immediate=False)
    
    def addBlock(self, position, color, immediate=True):
        """Adds a block to the map"""
        self.removeBlock(position)
        self.world[position] = color
    
    def removeBlock(self, position, immediate=True):
        """Removes a block from the map"""
        try:
            self.world.pop(position)
        except KeyError:
            pass
    
    def getBlocksLookingAt(self, position, vector, maxDistance):
        """Returns which blocks the player is looking at"""
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in range(maxDistance * m):
            key = (round(x), round(y), round(z))
            if key != previous and key in self.world:
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None
