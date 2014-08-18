
from Vector import *

class Collision(object):
    def lookAtBlock(player, map):
        x, y, z = player.getEyePosition()
        z += 0.5
        dx, dy, dz = player.getWorldVector(Vector(1, 0, 0))
        i = 0
        m = 10
        while map.getBlock(round(Vector(x, y, z))) == False and i < player.armLength * m:
            i += 1
            x += dx/m
            y += dy/m
            z += dz/m
            if not map.validCoordinates(round(Vector(x, y, z))) and not round(z)>=map.len_z:
                return False
        if map.getBlock(round(Vector(x, y, z))) == False:
            return False
        else:
            return (round(Vector(x, y, z)), round(Vector(x-dx/m, y-dy/m, z-dz/m)))
