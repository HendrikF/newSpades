
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
    
    def hasGround(player, map):
        x, y, z = player.position.getTuple()
        rx, ry, rz = round(player.position).getTuple()
        
        if z-rz > 0.1:
            return False
        
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if map.getBlock(rx+dx, ry+dy, rz) != False and map.getBlock(rx+dx, ry+dy, rz+1) == False and map.getBlock(rx+dx, ry+dy, rz+2) == False and (map.getBlock(rx+dx, ry+dy, rz+3) == False or player.crouching):
                    #print("X:",ry+dx-x, "Y:",ry+dy-y)
                    if abs(rx+dx-x) < 0.7 and abs(ry+dy-y) < 0.7:
                        return True
        return False
