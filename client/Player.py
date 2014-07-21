from Vector import *
from math import radians, sin, cos

class Player(object):
    def __init__(self, username):
        self.username = username
        
        self.velocity = Vector(0, 0, 0)
        self.position = Vector(0, 0, 0)
        #                yaw pitch roll
        self.orientation = [180, 0, 0]
        self.speed = 10
        self.height = 3
        self.crouching = False
    
    def getVectorFromOrientation(self, vector):
        x, y, z = vector.getTuple()
        a, b, c = self.orientation
        a, b, c = radians(a), radians(b), radians(c)
        ca, cb, cc, sa, sb, sc = cos(a), cos(b), cos(c), sin(a), sin(b), sin(c)
        new_x = ca*cb*x + (ca*sb*sc - sa*cc)*y + (ca*sb*cc + sa*sc)*z
        new_y = sa*cb*x + (sa*sb*sc + ca*cc)*y + (sa*sb*cc - ca*sc)*z
        new_z = (-sb)*x +  cb*sc            *y +  cb*cc            *z
        return Vector(new_x, new_y, new_z)
