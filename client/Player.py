from Vector import *
from math import radians, sin, cos

class Player(object):
    def __init__(self, username):
        self.username = username
        
        self.velocity = Vector(1,1,1)
        self.position = Vector(0, 0, 0)
        #                yaw pitch roll
        self.orientation = [0, 0, 0]
    
    def getVectorFromOrientation(self, vector):
        x, y, z = vector.getTuple()
        a, b, c = self.orientation
        a, b, c = radians(a), radians(b), radians(c)
        x = cos(a)*cos(b)*x + (cos(a)*sin(b)*sin(c) - sin(a)*cos(c))*y + (cos(a)*sin(b)*cos(c) + sin(a)*sin(c))*z
        y = sin(a)*cos(b)*x + (sin(a)*sin(b)*sin(c) + cos(a)*cos(c))*y + (sin(a)*sin(b)*cos(c) - cos(a)*sin(c))*z
        z = (-sin(b))    *x +  cos(b)*sin(c)                        *y +  cos(b)*cos(c)                        *z
        return Vector(x, y, z)
    
    """def getVectorFromOrientation(self, vector):
        x, y, z = vector.getTuple()
        a, b, c = self.orientation
        a, b, c = radians(a), radians(b), radians(c)
        # Transponierte Matrix von oben
        x = cos(a)*cos(b)                         *x + sin(a)*cos(b)                         *y + (-sin(b))    *z
        y = (cos(a)*sin(b)*sin(c) - sin(a)*cos(c))*x + (cos(a)*cos(c) + sin(a)*sin(b)*sin(c))*y + cos(b)*sin(c)*z
        z = (cos(a)*sin(b)*cos(c) + sin(a)*sin(c))*x + (sin(a)*sin(b)*cos(c) - cos(a)*sin(c))*y + cos(b)*cos(c)*z
        return self.position + Vector(x, y, z)"""
    