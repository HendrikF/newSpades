from Vector import *
from math import radians, sin, cos, atan

class Player(object):
    def __init__(self, username):
        self.username = username
        
        self.velocity = Vector(0, 0)
        self.velocity_z = 0
        self.keys = {
            "FWD": False,
            "BWD": False,
            "RIGHT": False,
            "LEFT": False
        }
        self.maxSpeed = 5
        # foot coordinates
        self.position = Vector(0, 0, 0)
        #                yaw pitch roll
        self.orientation = [0, 0, 0]
        self.speed = 5
        self.height = 3
        self.eyeHeight = self.height - 0.5
        self.crouching = False
        self.fallSpeed = -15
        self.jumpSpeed = 10
        self.jumpTime = 10
        self.gravity = -30
        self.jumping = 0
        self.armLength = 6
        self.radius = 0.3
    
    def getWorldVector(self, vector, x=None, y=None, z=None):
        vx, vy, vz = vector
        a, b, c = self.orientation
        a, b, c = radians(a), radians(b), radians(c)
        ca, cb, cc, sa, sb, sc = cos(a), cos(b), cos(c), sin(a), sin(b), sin(c)
        new_x = ca*cb*vx + (ca*sb*sc - sa*cc)*vy + (ca*sb*cc + sa*sc)*vz
        new_y = sa*cb*vx + (sa*sb*sc + ca*cc)*vy + (sa*sb*cc - ca*sc)*vz
        new_z = (-sb)*vx +  cb*sc            *vy +  cb*cc            *vz
        if x != None: new_x = x
        if y != None: new_y = y
        if z != None: new_z = z
        return Vector(new_x, new_y, new_z)
    
    def getEyeHeight(self):
        return self.eyeHeight-1 if self.crouching else self.eyeHeight
    
    def getEyePosition(self):
        return self.position + Vector(0, 0, self.getEyeHeight())
    
    def getSpeed(self):
        return self.speed*0.5 if self.crouching else self.speed
    
    def move(self, time):
        self.velocity = Vector()
        if self.keys["FWD"]: self.velocity.x += 1
        if self.keys["BWD"]: self.velocity.x -= 1
        if self.keys["RIGHT"]: self.velocity.y -= 1
        if self.keys["LEFT"]:  self.velocity.y += 1
        self.position += (self.getWorldVector( self.velocity, z=0 ).getUnitVector( self.getSpeed() ).add( z=self.velocity_z )) * time
    
    def hasGround(self, map):
        if map.getBlock(round(self.position)) != False:
            return True
        for fx in (-1, 0, 1):
            for fy in (-1, 0, 1):
                if fx==fy==0:
                    continue
                if map.getBlock(round(self.position + Vector(fx, fy))) == False:
                    continue
                dx = self.position.x - round(self.position.x+fx)
                dy = self.position.y - round(self.position.y+fy)
                if abs(dx)==abs(dy):
                    rb = sqrt(2)
                elif dx==0 or dy==0:
                    rb = 0.5
                else:
                    rb = 0.5/(sin(atan(dy/dx)%radians(45)))
                if sqrt(dx**2+dy**2)-rb-self.radius <= 0:
                    return True
        return False
