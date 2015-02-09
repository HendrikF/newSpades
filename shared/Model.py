import pyglet
from pyglet.gl import *
import os
import struct

import logging
logger = logging.getLogger(__name__)

FACES = [
    ( 0, 1, 0),
    ( 0,-1, 0),
    (-1, 0, 0),
    ( 1, 0, 0),
    ( 0, 0, 1),
    ( 0, 0,-1),
]

class Model(object):
    def __init__(self, scale=0.1, offset=(0,0,0), progressbar=None):
        self.blocks = {}
        self._blocks = {}
        self.batch = pyglet.graphics.Batch()
        self.scale = scale
        self.offset = offset
        self.progressbar = progressbar
    
    @property
    def size(self):
        return len(self.blocks)
    
    def addBlock(self, pos, color, cn=True):
        self.blocks[pos] = color
        x, y, z = pos
        vertex_data = self.cubeVertices(x, y, z)
        color_data = self.vertexColors(x, y, z, vertex_data)
        self._blocks[pos] = self.batch.add(24, GL_QUADS, None,
            ('v3f/static', vertex_data),
            ('c3f/static', color_data)
        )
        if cn:
            self.checkNeighbors(pos)
    
    def removeBlock(self, pos, cn=True):
        del self.blocks[pos]
        self._blocks[pos].delete()
        del self._blocks[pos]
        if cn:
            # cn avoids 'infinite' recursion
            self.checkNeighbors(pos)
    
    def contains(self, pos):
        return (pos in self.blocks)
    
    def draw(self, pitch=0):
        glPushMatrix()
        glScalef(self.scale, self.scale, self.scale)
        glTranslatef(self.offset[0], self.offset[1], self.offset[2])
        if pitch != 0:
            glRotatef(pitch, 0, 0, 1)
        self.batch.draw()
        glPopMatrix()
    
    def checkNeighbors(self, position):
        x, y, z = position
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx==dy==dz==0:
                        continue
                    pos = (x + dx, y + dy, z + dz)
                    if pos in self.blocks:
                        self.updateBlock(pos)
    
    def exposed(self, position):
        """Returns whether a block must be rendered (True when not covered on all 6 sides)"""
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.blocks:
                return True
        return False
    
    def updateBlock(self, pos):
        color = self.blocks[pos]
        self.removeBlock(pos, cn=False)     # cn to avoid infinite recursion!!
        self.addBlock(pos, color, cn=False)
    
    def cubeVertices(self, x, y, z, d=0.5):
        """Returns a list of all vertices of the block at (x, y, z)"""
        return [
            x-d, y+d, z-d,   x-d, y+d, z+d,   x+d, y+d, z+d,   x+d, y+d, z-d, # top
            x-d, y-d, z-d,   x+d, y-d, z-d,   x+d, y-d, z+d,   x-d, y-d, z+d, # bottom
            x-d, y-d, z-d,   x-d, y-d, z+d,   x-d, y+d, z+d,   x-d, y+d, z-d, # front
            x+d, y-d, z+d,   x+d, y-d, z-d,   x+d, y+d, z-d,   x+d, y+d, z+d, # back
            x-d, y-d, z+d,   x+d, y-d, z+d,   x+d, y+d, z+d,   x-d, y+d, z+d, # right
            x+d, y-d, z-d,   x-d, y-d, z-d,   x-d, y+d, z-d,   x+d, y+d, z-d, # left
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
                (x-0.5, y+0.5, z+0.5), 
                (x-0.5, y+0.5, z-0.5), 
                (x+0.5, y+0.5, z-0.5), 
                (x+0.5, y+0.5, z+0.5)
            ],
            [ # bottom
                (x-0.5, y-0.5, z+0.5), 
                (x-0.5, y-0.5, z-0.5), 
                (x+0.5, y-0.5, z-0.5), 
                (x+0.5, y-0.5, z+0.5)
            ],
            [ # front
                (x-0.5, y-0.5, z+0.5), 
                (x-0.5, y-0.5, z-0.5), 
                (x-0.5, y+0.5, z-0.5), 
                (x-0.5, y+0.5, z+0.5)
            ],
            [ # back
                (x+0.5, y-0.5, z+0.5), 
                (x+0.5, y-0.5, z-0.5), 
                (x+0.5, y+0.5, z-0.5), 
                (x+0.5, y+0.5, z+0.5)
            ],
            [ # right
                (x+0.5, y-0.5, z+0.5), 
                (x-0.5, y-0.5, z+0.5), 
                (x-0.5, y+0.5, z+0.5), 
                (x+0.5, y+0.5, z+0.5)
            ],
            [ # left
                (x+0.5, y-0.5, z-0.5), 
                (x-0.5, y-0.5, z-0.5), 
                (x-0.5, y+0.5, z-0.5), 
                (x+0.5, y+0.5, z-0.5)
            ]
        ]
        return sum([0 if pos in self.blocks else 0.25 for pos in m[f]])
    
    def vertexColors(self, x, y, z, vertex_data):
        """For each vertex look which lightlevel it has and modify its color"""
        r, g, b = self.blocks[(x, y, z)]
        color_data = []
        for i in range(24): # len(vertex_data) / 3
            ll = self.getLightLevel(vertex_data[i*3:i*3+3], i//4)
            color_data.extend((r*ll, g*ll, b*ll))
        return color_data
    
    def save(self, fn):
        with open(fn, 'wb') as f:
            for (x, y, z), (r, g, b) in self.blocks.items():
                f.write(struct.pack('!lllfff', int(x), int(y), int(z), r, g, b))
    
    def clear(self):
        self.blocks = {}
        for vertex in self._blocks.values():
            vertex.delete()
        self._blocks = {}
    
    def load(self, fn, progressbar=None):
        # (this adds always a total of 1 to the progressbar)
        # size of file must be a multiple of !lllfff (xyzrgb)
        filesize = os.stat(fn).st_size
        size = struct.calcsize('!lllfff')
        if filesize % size != 0:
            logger.error("Cant't read file '%s': Size of file (%s) isn't a multiple of one entry (%s)", fn, filesize, size)
            raise TypeError("Cant't read file '%s': Size of file (%s) isn't a multiple of one entry (%s)" % (fn, filesize, size))
        self.clear()
        if self.progressbar:
            step = size / filesize
        with open(fn, 'rb') as f:
            while True:
                data = f.read(size)
                if not data:
                    break
                x, y, z, r, g, b = struct.unpack('!lllfff', data)
                self.addBlock((x, y, z), (r, g, b))
                if self.progressbar:
                    self.progressbar.step(step)
                    self.progressbar.update()
        # makes it possible to do m=Model().load(...)
        return self
