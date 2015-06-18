from collections import deque
import time
import copy
from shared.Map import Map
from pyglet.gl import *
import pyglet

import logging
logger = logging.getLogger(__name__)

SECTOR_SIZE = 16

def sectorize(position):
    """Returns the sector in which a block is located"""
    x, y, z = position
    x, z = x // SECTOR_SIZE, z // SECTOR_SIZE
    return (x, 0, z)

class DrawableMap(Map):
    """Extends shared.Map by rendering"""
    def __init__(self, maxFPS=60, farplane=100):
        self.maxFPS = maxFPS
        # helps calculating how many sectors are shown around the player
        self.farplane = farplane
        super().__init__()
        self.batch = pyglet.graphics.Batch()
        # all blocks which are shown at current position
        self.shown = {}
        # all verticies currently shown
        self._shown = {}
        # dict[(x, y, z)] = [(x, y, z), (x, y, z), ...] which blocks are in which sector
        self.sectors = {}
        # rotating list which blocks should next be shown/hidden
        self.queue = deque()
        # save position of player
        self.currentSector = None
        # MINIMAP
        self.mmColors = {}
        self.mmShown = set()
        self.mmBatch = pyglet.graphics.Batch()
        self.mmSize = (50, 50)
        self.mmResolution = 3
        self.mmPosition = (0, 0)
        
        self.receivedParts = []
        self.partsCount = 0
    
    """def load(self):
        for x in range(0, 50):
            self.addBlock((x, 1, 0), (1, 1, 0), immediate=False)
            for z in range(0, 50):
                self.addBlock((x, 0, z), (0, 1, 0), immediate=False)
        self.addBlock((1, 0, 0), (1, 0, 0), immediate=False)
        self.addBlock((0, 1, 0), (0, 1, 0), immediate=False)
        self.addBlock((0, 0, 1), (0, 0, 1), immediate=False)"""
    
    @property
    def active(self):
        return len(self.receivedParts) >= self.partsCount and self.partsCount > 0
    
    def receivedMapData(self, msg):
        msg = copy.deepcopy(msg)
        if msg == 'StartMapTransfer':
            self.partsCount = msg.parts
            msg.part = 0
            self.receivedParts.append(msg)
        elif msg == 'MapData':
            self.receivedParts.append(msg)
        if self.active:
            data = b''
            for part in sorted(self.receivedParts, key=lambda item: item.part):
                data += part.data
            self.importBytes(data)
        
    def addBlock(self, position, color, immediate=True):
        """Adds a block to the map"""
        super().addBlock(position, color)
        self.sectors.setdefault(sectorize(position), []).append(position)
        self.updateMinimap(position)
        if immediate:
            if self.exposed(position):
                self.showBlock(position)
            self.checkNeighbors(position)
    
    def removeBlock(self, position, immediate=True):
        """Removes a block from the map"""
        super().removeBlock(position)
        try:
            self.sectors[sectorize(position)].remove(position)
        except (KeyError, ValueError):
            pass
        self.updateMinimap(position)
        if immediate:
            if position in self.shown:
                self.hideBlock(position)
            self.checkNeighbors(position)
    
    ##############
    # Rendering
    
    def update(self, position):
        """Checks whether the player moved to an other sector"""
        x, y, z = position
        self.process_queue()
        sector = sectorize(position)
        if sector != self.currentSector:
            self.changeSectors(self.currentSector, sector)
            if self.currentSector is None:
                self.process_entire_queue()
            self.currentSector = sector
        self.moveMinimap(position)
    
    def draw(self):
        """Draws the map"""
        self.batch.draw()
    
    def drawBlockLookingAt(self, position, vector, maxDistance, width=2):
        block = self.getBlocksLookingAt(position, vector, maxDistance)[0]
        if block:
            x, y, z = block
            vertex_data = self.cubeVertices(x, y, z, 0.51)
            glColor3d(0, 0, 0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glLineWidth(width)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    ##################
    # Private stuff
    
    def exposed(self, position):
        """Returns whether a block must be rendered (True when not covered on all 6 sides)"""
        x, y, z = position
        for dx, dy, dz in self.FACES:
            if (x + dx, y + dy, z + dz) not in self.blocks:
                return True
        return False
    
    def checkNeighbors(self, position):
        """Checks whether a new or removed block covers a neighbor and eventually hides/shows the neighbors"""
        x, y, z = position
        for dx, dy, dz in self.FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.blocks:
                continue
            if self.exposed(key):
                if key not in self.shown:
                    self.showBlock(key)
            else:
                if key in self.shown:
                    self.hideBlock(key)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx==dy==dz==0:
                        continue
                    pos = (x + dx, y + dy, z + dz)
                    if pos in self.shown:
                        self.updateBlock(pos)
    
    def showBlock(self, position, immediate=True):
        self.shown[position] = self.blocks[position] # color
        if immediate:
            self._showBlock(position)
        else:
            self._enqueue(self._showBlock, position)
    
    def _showBlock(self, position):
        x, y, z = position
        vertex_data = self.cubeVertices(x, y, z)
        color_data = self.vertexColors(x, y, z, vertex_data)
        self._shown[position] = self.batch.add(24, GL_QUADS, None,
            ('v3f/static', vertex_data),
            ('c3f/static', color_data)
        )
    
    def hideBlock(self, position, immediate=True):
        try:
            self.shown.pop(position)
        except KeyError:
            pass
        if immediate:
            self._hideBlock(position)
        else:
            self._enqueue(self._hideBlock, position)
    
    def _hideBlock(self, position):
        try:
            self._shown.pop(position).delete()
        except KeyError:
            pass
    
    def updateBlock(self, position):
        """Call this to update the shadows of a block"""
        self.hideBlock(position)
        self.showBlock(position)
    
    def showSector(self, sector):
        for position in self.sectors.get(sector, []):
            if position not in self.shown and self.exposed(position):
                self.showBlock(position, False)
    
    def hideSector(self, sector):
        for position in self.sectors.get(sector, []):
            if position in self.shown:
                self.hideBlock(position, False)
    
    def changeSectors(self, before, after):
        """Calculates which sectors to show/hide when moving to an other sector"""
        before_set = set()
        after_set = set()
        pad = round(self.farplane/SECTOR_SIZE)
        for dx in range(-pad, pad + 1):
            for dz in range(-pad, pad + 1):
                if dx ** 2 + dz ** 2 > (pad + 1) ** 2:
                    continue
                if before:
                    x, y, z = before
                    before_set.add((x + dx, y, z + dz))
                if after:
                    x, y, z = after
                    after_set.add((x + dx, y, z + dz))
        show = after_set - before_set
        hide = before_set - after_set
        for sector in show:
            self.showSector(sector)
        for sector in hide:
            self.hideSector(sector)
    
    def _enqueue(self, func, *args):
        self.queue.append((func, args))
    
    def _dequeue(self):
        func, args = self.queue.popleft()
        func(*args)
    
    def process_queue(self):
        start = time.clock()
        while self.queue and time.clock() - start < 1 / self.maxFPS:
            self._dequeue()
    
    def process_entire_queue(self):
        while self.queue:
            self._dequeue()
    
    def cubeVertices(self, x, y, z, d=0.5):
        """Returns a list of all vertices of the block at (x, y, z)"""
        e = d-0.5 # 0
        f = d+0.5 # 1
        return [
            x-d, y+e, z-d,   x-d, y+e, z+d,   x+d, y+e, z+d,   x+d, y+e, z-d, # top
            x-d, y-f, z-d,   x+d, y-f, z-d,   x+d, y-f, z+d,   x-d, y-f, z+d, # bottom
            x-d, y-f, z-d,   x-d, y-f, z+d,   x-d, y+e, z+d,   x-d, y+e, z-d, # front
            x+d, y-f, z+d,   x+d, y-f, z-d,   x+d, y+e, z-d,   x+d, y+e, z+d, # back
            x-d, y-f, z+d,   x+d, y-f, z+d,   x+d, y+e, z+d,   x-d, y+e, z+d, # right
            x+d, y-f, z-d,   x-d, y-f, z-d,   x-d, y+e, z-d,   x+d, y+e, z-d, # left
        ]
    
    def getLightLevel(self, position, f):
        """Parameters are the coordinates of an edge and 0-5 for top, bottom, ..., left (see cubeVertices())
        Returns the lightlevel of a vertex depending on for which face it is drawn
        0    = 4 blocks covering vertex
        0.25 = 3
        0.5  = 2
        0.75 = 1
        1    = 0
        """
        x, y, z = position
        m = [
            [ # top
                (x-0.5, y+1, z+0.5), 
                (x-0.5, y+1, z-0.5), 
                (x+0.5, y+1, z-0.5), 
                (x+0.5, y+1, z+0.5)
            ],
            [ # bottom
                (x-0.5, y  , z+0.5), 
                (x-0.5, y  , z-0.5), 
                (x+0.5, y  , z-0.5), 
                (x+0.5, y  , z+0.5)
            ],
            [ # front
                (x-0.5, y  , z+0.5), 
                (x-0.5, y  , z-0.5), 
                (x-0.5, y+1, z-0.5), 
                (x-0.5, y+1, z+0.5)
            ],
            [ # back
                (x+0.5, y  , z+0.5), 
                (x+0.5, y  , z-0.5), 
                (x+0.5, y+1, z-0.5), 
                (x+0.5, y+1, z+0.5)
            ],
            [ # right
                (x+0.5, y  , z+0.5), 
                (x-0.5, y  , z+0.5), 
                (x-0.5, y+1, z+0.5), 
                (x+0.5, y+1, z+0.5)
            ],
            [ # left
                (x+0.5, y  , z-0.5), 
                (x-0.5, y  , z-0.5), 
                (x-0.5, y+1, z-0.5), 
                (x+0.5, y+1, z-0.5)
            ]
        ]
        return sum([0.15 if pos in self.blocks else 0.25 for pos in m[f]])
    
    def vertexColors(self, x, y, z, vertex_data):
        """For each vertex look which lightlevel it has and modify its color"""
        r, g, b = self.blocks[(x, y, z)]
        color_data = []
        for i in range(24): # len(vertex_data) / 3
            ll = self.getLightLevel(vertex_data[i*3:i*3+3], i//4)
            color_data.extend((r*ll, g*ll, b*ll))
        return color_data
    
    def getHighestBlocksColor(self, x, z):
        for y in range(30, -1, -1):
            if (x, y, z) in self.blocks:
                return self.blocks[(x, y, z)]
        return (0, 0, 0)
    
    def drawMinimap(self):
        x, y = self.mmPosition
        glPushMatrix()
        r = self.mmResolution
        glTranslatef(-r*x, -r*y, 0)
        self.mmBatch.draw()
        glPopMatrix()
    
    def moveMinimap(self, pos3):
        x, y, z = pos3
        x, z = int(round(x)), int(round(z))
        r = self.mmResolution
        size = (
            (self.mmSize[0]//2)//r, 
            (self.mmSize[1]//2)//r)
        new = set()
        for dx in range(-size[0], size[0]):
            for dy in range(-size[1], size[1]):
                new.add((z+dx, x+dy))
        show = new - self.mmShown
        hide = self.mmShown - new
        for pos in show:
            self.showBlockOnMinimap(pos)
        for pos in hide:
            self.hideBlockOnMinimap(pos)
        self.mmShown = new
        pos2 = (z, x)
        self.hideBlockOnMinimap(self.mmPosition)
        self.showBlockOnMinimap(self.mmPosition)
        self.hideBlockOnMinimap(pos2)
        self.showBlockOnMinimap(pos2, (1,0,0))
        self.mmPosition = pos2
    
    def showBlockOnMinimap(self, pos2, color=None):
        x, y = pos2
        c = self.getHighestBlocksColor(y, x) if color is None else color
        r = self.mmResolution
        self.mmColors[pos2] = self.mmBatch.add(4, GL_QUADS, None,
            ('v2f', [r*x,r*y, (r+1)*x,r*y, (r+1)*x,(r+1)*y, r*x,(r+1)*y]),
            ('c3f', c*4)
        )
    
    def hideBlockOnMinimap(self, pos2):
        if pos2 in self.mmColors:
            self.mmColors.pop(pos2).delete()
    
    def updateMinimap(self, pos3):
        x, y, z = pos3
        pos2 = (int(round(z)), int(round(x)))
        for i in range(2):
            if abs(pos2[i] - self.mmPosition[i]) > self.mmSize[i]/self.mmResolution/2:
                return
        self.hideBlockOnMinimap(pos2)
        self.showBlockOnMinimap(pos2)
        self.mmShown.add(pos2)

"""
    (x+d|y+e|z-d) o------------------o (x+d|y+e|z+d)                                
                 /.    (x|y|z)      /|                                              
                / .       X        / |                                              
               /  .               /  |                               Y              
(x-d|y+e|z-d) o------------------o (x-d|y+e|z+d)                   ^                
              |   .              |   |                             |    X           
              |   .              |   |                             |  ^             
              |   .              |   |                             | /              
              |   .              |   |                             |/               
              |   .              |   |                           --O--------> Z     
    (x+d|y-f|z-d) ...............|...o (x+d|y-f|z+d)              /|                
              |  .               |  /                                               
              | .                | /                                                
              |.                 |/                                                 
(x-d|y-f|z-d) o------------------o (x-d|y-f|z+d)                                    
    
    * cubeVertices() returns the faces ANTICLOCKWISE                                
    * the coordinate of the block lies on top of it in the middle                   

"""
