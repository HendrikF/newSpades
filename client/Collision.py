
from Vector import *

class Collision(object):
    def lookAtBlock(player, map):
        x, y, z = player.position.getTuple()
        z += player.getEyeHeight()
        dx, dy, dz = player.getWorldVector(Vector(1, 0, 0)).getTuple()
        i = 0
        m = 8
        while map.getBlock(round(x), round(y), round(z)) == False and i < 4 * m:
            i += 1
            x += dx/m
            y += dy/m
            z += dz/m
            if x < 0 or x > map.len_x or y < 0 or y > map.len_y:
                return False
        if map.getBlock(round(x), round(y), round(z)) == False:
            return False
        else:
            return [round(Vector(x, y, z)), round(Vector(x-dx/m, y-dy/m, z-dz/m))]
            
