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
            result.append((e[1], e[2], e[6], e[5]))
        if self.getBlock(x, y-1, z) == False:
            result.append((e[2], e[3], e[7], e[6]))
        if self.getBlock(x+1, y, z) == False:
            result.append((e[3], e[4], e[8], e[7]))
        if self.getBlock(x, y+1, z) == False:
            result.append((e[4], e[1], e[5], e[8]))
        if not z == 0 and self.getBlock(x, y, z-1) == False:
            result.append((e[5], e[6], e[7], e[8]))
        return result
    
    def getBlock(self, x, y, z):
        return self.data[x % self.len_x][y % self.len_y][z % self.len_z]
    
    def getZ(self, x, y):
        for z in range(self.len_z-1, -1, -1):
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
