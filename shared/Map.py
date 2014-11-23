from random import randrange
from math import ceil
from collections import deque
import random
import time
import math
from pyglet.gl import *

import logging
logger = logging.getLogger(__name__)

SECTOR_SIZE = 16

def cubeVerticies(x, y, z):
    """Returns a list of all verticies of the block at (x, y, z)"""
    return [
        x-0.5, y  , z-0.5, x-0.5, y  , z+0.5, x+0.5, y  , z+0.5, x+0.5, y  , z-0.5, # top
        x-0.5, y-1, z-0.5, x+0.5, y-1, z-0.5, x+0.5, y-1, z+0.5, x-0.5, y-1, z+0.5, # bottom
        x-0.5, y-1, z-0.5, x-0.5, y-1, z+0.5, x-0.5, y  , z+0.5, x-0.5, y  , z-0.5, # left
        x+0.5, y-1, z+0.5, x+0.5, y-1, z-0.5, x+0.5, y  , z-0.5, x+0.5, y  , z+0.5, # right
        x-0.5, y-1, z+0.5, x+0.5, y-1, z+0.5, x+0.5, y  , z+0.5, x-0.5, y  , z+0.5, # front
        x+0.5, y-1, z-0.5, x-0.5, y-1, z-0.5, x-0.5, y  , z-0.5, x+0.5, y  , z-0.5, # back
    ]

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
    
    def load(self):
        self._load()
    
    def _load(self):
        for x in range(0, 50):
            for z in range(0, 50):
                    self.addBlock((x, 0, z), (0, 1, 0), immediate=False)
    
    def exposed(self, position):
        """Returns whether a block must be rendered (True when not covered on all 6 sides)"""
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False
    
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
    
    def check_neighbors(self, position):
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
    
    def showBlock(self, position, immediate=True):
        color = self.world[position]
        self.shown[position] = color
        if immediate:
            self._showBlock(position, color)
        else:
            self._enqueue(self._showBlock, position, color)
    
    def _showBlock(self, position, color):
        x, y, z = position
        vertex_data = cubeVerticies(x, y, z)
        color_data = list(color)
        self._shown[position] = self.batch.add(24, GL_QUADS, None,
            ('v3f/static', vertex_data),
            ('c3f/static', color_data*24)
        )
    
    def hideBlock(self, position, immediate=True):
        self.shown.pop(position)
        if immediate:
            self._hideBlock(position)
        else:
            self._enqueue(self._hideBlock, position)
    
    def _hideBlock(self, position):
        self._shown.pop(position).delete()
    
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
