import pyglet
from pyglet.gl import *

from shared.Model import Model

import logging
logger = logging.getLogger(__name__)

class DrawableModel(Model):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._blocks = {}
        self.batch = pyglet.graphics.Batch()
    
    def addBlock(self, position, color, cn=True):
        super().addBlock(position, color)
        x, y, z = position
        vertex_data = self.cubeVertices(x, y, z)
        color_data = self.vertexColors(x, y, z, vertex_data)
        self._blocks[position] = self.batch.add(24, GL_QUADS, None,
            ('v3f/static', vertex_data),
            ('c3f/static', color_data)
        )
        if cn:
            self.checkNeighbors(position)
    
    def removeBlock(self, position, cn=True):
        super().removeBlock(position)
        self._blocks[position].delete()
        del self._blocks[position]
        if cn:
            # cn avoids 'infinite' recursion
            self.checkNeighbors(position)
    
    def draw(self, pitch=0):
        glPushMatrix()
        glScalef(self.scale, self.scale, self.scale)
        glTranslatef(self.offset[0], self.offset[1], self.offset[2])
        if pitch != 0:
            glRotatef(pitch, 0, 0, 1)
        glTranslatef(self.offset2[0], self.offset2[1], self.offset2[2])
        glScalef(self.scale2, self.scale2, self.scale2)
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
        for dx, dy, dz in self.FACES:
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
            j = i // 4
            #ll = self.getLightLevel(vertex_data[i*3:i*3+3], j)
            ll = 0.9 if j in (0, 1) else 1 if j in (2, 3) else 1.1
            color_data.extend((r*ll, g*ll, b*ll))
        return color_data
