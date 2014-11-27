from pyglet.gl import *

FACES = [
    ( 0, 1, 0),
    ( 0,-1, 0),
    (-1, 0, 0),
    ( 1, 0, 0),
    ( 0, 0, 1),
    ( 0, 0,-1),
]

class Model(object):
    def __init__(self):
        self.blocks = {}
        self._blocks = {}
        self.batch = pyglet.graphics.Batch()
    
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
            # cn avoids infinite recursion
            self.checkNeighbors(pos)
    
    def contains(self, pos):
        return (pos in self.blocks)
    
    def draw(self):
        self.batch.draw()
    
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
        return sum([0.15 if pos in self.blocks else 0.25 for pos in m[f]])
    
    def vertexColors(self, x, y, z, vertex_data):
        """For each vertex look which lightlevel it has and modify its color"""
        r, g, b = self.blocks[(x, y, z)]
        color_data = []
        for i in range(24): # len(vertex_data) / 3
            ll = self.getLightLevel(vertex_data[i*3:i*3+3], i//4)
            color_data.extend((r*ll, g*ll, b*ll))
        return color_data
