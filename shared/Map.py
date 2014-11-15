from random import randrange
from Vector import *
from math import ceil

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
        if self.getBlock(Vector(x, y, z+1)) == False:
            result.append((e[1], e[4], e[3], e[2]))
        if self.getBlock(Vector(x-1, y, z)) == False:
            result.append((e[1], e[2], e[6], e[5]))
        if self.getBlock(Vector(x, y-1, z)) == False:
            result.append((e[2], e[3], e[7], e[6]))
        if self.getBlock(Vector(x+1, y, z)) == False:
            result.append((e[3], e[4], e[8], e[7]))
        if self.getBlock(Vector(x, y+1, z)) == False:
            result.append((e[4], e[1], e[5], e[8]))
        if not z == 0 and self.getBlock(Vector(x, y, z-1)) == False:
            result.append((e[5], e[6], e[7], e[8]))
        return result
    
    def getAllBlockFaces(self, x, y, z):
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
        result.append((e[1], e[4], e[3], e[2]))
        result.append((e[5], e[1], e[2], e[6]))
        result.append((e[6], e[2], e[3], e[7]))
        result.append((e[7], e[3], e[4], e[8]))
        result.append((e[8], e[4], e[1], e[5]))
        result.append((e[8], e[5], e[6], e[7]))
        return result
    
    def getBlock(self, vector):
        x, y, z = vector
        if not self.validCoordinates(vector):
            return False
        return self.data[x][y][z]
    
    def setBlock(self, vector, color):
        x, y, z = vector
        if not self.validCoordinates(vector):
            return False
        def rand(a=0, var=100):
            return min(max(round(a+randrange(-var, var)/1000, 3), 0), 1)
        if color != False:
            color = (rand(color[0]), rand(color[1]), rand(color[2]))
        self.data[x][y][z] = color
        return True
    
    def getZ(self, x, y, zp=None):
        if zp is None:
            zp = self.len_z
        for z in range(zp-1, -1, -1):
            if self.getBlock(round(Vector(x, y, z))) != False:
                return z
        return 0
    
    def validCoordinates(self, v):
        return not (
            v.x < 0 or 
            v.x >= self.len_x or 
            v.y < 0 or 
            v.y >= self.len_y or 
            v.z < 0 or 
            v.z >= self.len_z
        )
    
    def getFreeWay(self, position1, position2, player):
        delta = position2 - position1
        pos = position2
        h = player.getHeight()
        m = ceil(float(delta))
        if m == 0:
            return position2
        for n in range(0, m+1):
            free = True
            for z in range(1, h+1):
                if self.getBlock(round(position1 + delta/m*n + Vector(0, 0, z))) != False:
                    free = False
                    break
            if player.velocity_z == 0 and not free:
                free = True
                for z in range(2, h+2):
                    if self.getBlock(round(position1 + delta/m*n + Vector(0, 0, z))) != False:
                        free = False
                        break
            if not free:
                pos = position1 + delta/m*(n-1)
                break
        return pos
    
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
