from random import randrange

class Map(object):
    def __init__(self, data):
        self.data = data
        self.len_x = len(data)
        self.len_y = len(data[0])
        self.len_z = len(data[0][0])
    
    """ Returns an iterator over all Blockfaces """
    def getFaces(self):
        for x, x_ in enumerate(self.data):
            for y, y_ in enumerate(x_):
                for z, color in enumerate(y_):
                    if color == False:
                        continue
                    for face in self.getVisibleBlockFaces(x, y, z):
                        yield (face, color)
    
    """ Returns only visible faces of a block """
    def getVisibleBlockFaces(self, x, y, z):
        result = []
        e = [
            None,
            (x-0.5, y+0.5, z),
            (x-0.5, y-0.5, z),
            (x+0.5, y-0.5, z),
            (x+0.5, y+0.5, z),
            (x-0.5, y+0.5, z-1),
            (x-0.5, y-0.5, z-1),
            (x+0.5, y-0.5, z-1),
            (x+0.5, y+0.5, z-1)
        ]
        if self.getBlock(x, y, z+1) == False:
            result.append((e[1], e[4], e[3], e[2]))
        if self.getBlock(x-1, y, z) == False:
            result.append((e[5], e[1], e[2], e[6]))
        if self.getBlock(x, y-1, z) == False:
            result.append((e[6], e[2], e[3], e[7]))
        if self.getBlock(x+1, y, z) == False:
            result.append((e[7], e[3], e[4], e[8]))
        if self.getBlock(x, y+1, z) == False:
            result.append((e[8], e[4], e[1], e[5]))
        if not z == 0 and self.getBlock(x, y, z-1) == False:
            result.append((e[8], e[5], e[6], e[7]))
        return result
    
    def getBlock(self, x, y, z):
        if z >= self.len_z or z < 0:
            return False
        return self.data[x % self.len_x][y % self.len_y][z]
    
    def getBlockCenter(self, x, y, z):
        x = round(x)
        y = round(y)
        z = round(z)
        if self.getBlock(x, y, z) != False:
            return Vector(x, y, z-0.5)
        return False
    
    def setBlock(self, x, y, z, color):
        if x < 0 or x >= self.len_x or y < 0 or y >= self.len_y or z < 0 or z >= self.len_z:
            return False
        def rand(a=0, var=50):
            return min(max(round(a+randrange(-var, var)/1000, 3), 0), 1)
        if color != False:
            for i, c in enumerate(color):
                color[i] = rand(c, 100)
        self.data[x][y][z] = color
        return True
    
    def getZ(self, x, y, zp=None):
        if zp is None:
            zp = self.len_z
        for z in range(zp-1, -1, -1):
            if self.getBlock(x, y, z) != False:
                return z
        return 0
    
    """
        Edges:
        
           4-------3              Z
          /|      /|              |  X
         / |     / |              | /
        1-------2  |              |/
        |  8----|--7        Y-----O--
        | /     | /              /|
        |/      |/
        5-------6

        Faces / Sides:
        
           o-------o
          /| 1    /|
         / |     / |4
        o-------o  |
       5|  o----|--o
        | /  6  | /
        |/      |/ 3
        o-------o
            2
        
        1 top
        2 front
        3 right
        4 back
        5 left
        6 bottom
        
    """
