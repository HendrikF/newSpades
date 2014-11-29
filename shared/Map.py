from random import randrange
from math import ceil
from collections import deque
import random
import time
import math
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

FACES = [
    ( 0, 1, 0),
    ( 0,-1, 0),
    (-1, 0, 0),
    ( 1, 0, 0),
    ( 0, 0, 1),
    ( 0, 0,-1),
]

class Map(object):
    """Map represents the world and provides methods for adding/removing blocks and rendering"""
    def __init__(self, maxFPS=60, farplane=100):
        self.maxFPS = maxFPS
        # helps calculating how many sectors are shown around the player
        self.farplane = farplane
        self.batch = pyglet.graphics.Batch()
        # dict[(x, y, z)] = (r, g, b)
        self.world = {}
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
        self.dimensions = (0, 0)
    
    def load(self):
        self._load()
        self.calculateDimensions()
    
    def _load(self):
        for x in range(0, 50):
            self.addBlock((x, 1, 0), (1, 1, 0), immediate=False)
            for z in range(0, 50):
                    self.addBlock((x, 0, z), (0, 1, 0), immediate=False)
    
    def calculateDimensions(self):
        # TODO calc negative boundaries!
        dx = 0
        dz = 0
        for x, y, z in self.world:
            dx = max(dx, x)
            dz = max(dz, z)
        self.dimensions = (dx+1, dz+1)
    
    ######################
    # Map modification
    
    def addBlock(self, position, color, immediate=True):
        """Adds a block to the map"""
        if position in self.world:
            self.removeBlock(position, immediate)
        self.world[position] = color
        self.sectors.setdefault(sectorize(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.showBlock(position)
            self.checkNeighbors(position)
    
    def removeBlock(self, position, immediate=True):
        """Removes a block from the map"""
        del self.world[position]
        self.sectors[sectorize(position)].remove(position)
        if immediate:
            if position in self.shown:
                self.hideBlock(position)
            self.checkNeighbors(position)
    
    ##############
    # Rendering
    
    def update(self, position):
        """Checks whether the player moved to an other sector"""
        self.process_queue()
        sector = sectorize(position)
        if sector != self.currentSector:
            self.changeSectors(self.currentSector, sector)
            if self.currentSector is None:
                self.process_entire_queue()
            self.currentSector = sector
    
    def draw(self):
        """Draws the map"""
        self.batch.draw()
    
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
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False
    
    def checkNeighbors(self, position):
        """Checks whether a new or removed block covers a neighbor and eventually hides/shows the neighbors"""
        x, y, z = position
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
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
                    #if dx==dy==0 or dx==dz==0 or dy==dz==0:
                    if dx==dy==dz==0:
                        continue
                    pos = (x + dx, y + dy, z + dz)
                    if pos in self.world:
                        self.updateBlock(pos)
    
    def showBlock(self, position, immediate=True):
        self.shown[position] = self.world[position] # color
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
        self.shown.pop(position)
        if immediate:
            self._hideBlock(position)
        else:
            self._enqueue(self._hideBlock, position)
    
    def _hideBlock(self, position):
        self._shown.pop(position).delete()
    
    def updateBlock(self, position):
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
        return sum([0.15 if pos in self.world else 0.25 for pos in m[f]])
    
    def vertexColors(self, x, y, z, vertex_data):
        """For each vertex look which lightlevel it has and modify its color"""
        r, g, b = self.world[(x, y, z)]
        color_data = []
        for i in range(24): # len(vertex_data) / 3
            ll = self.getLightLevel(vertex_data[i*3:i*3+3], i//4)
            color_data.extend((r*ll, g*ll, b*ll))
        return color_data

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
