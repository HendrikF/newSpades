from Vector import *
from math import radians, sin, cos

class Player(object):
    def __init__(self, username):
        self.username = username
        
        self.velocity = Vector(0, 0, 0)
        # foot coordinates
        self.position = Vector(0, 0, 0)
        #                yaw pitch roll
        self.orientation = [0, 0, 0]
        self.speed = 5
        self.height = 3
        self.eyeHeight = self.height - 0.5
        self.crouching = False
        self.wantToCrouch = False
        self.fallSpeed = -15
        self.jumpSpeed = 10
        self.jumpTime = 0
        self.gravity = Vector(0, 0, -30)
        self.jumping = False
    
    def getWorldVector(self, vector):
        x, y, z = vector.getTuple()
        a, b, c = self.orientation
        a, b, c = radians(a), radians(b), radians(c)
        ca, cb, cc, sa, sb, sc = cos(a), cos(b), cos(c), sin(a), sin(b), sin(c)
        new_x = ca*cb*x + (ca*sb*sc - sa*cc)*y + (ca*sb*cc + sa*sc)*z
        new_y = sa*cb*x + (sa*sb*sc + ca*cc)*y + (sa*sb*cc - ca*sc)*z
        new_z = (-sb)*x +  cb*sc            *y +  cb*cc            *z
        return Vector(new_x, new_y, new_z)
    
    def getEyeHeight(self):
        return self.eyeHeight-1 if self.crouching else self.eyeHeight
    
    def getSpeed(self):
        return self.speed * (0.5 if self.crouching else 1)
    
    def getBlocksInWay(self, map, movement):
        ol = [(1,0), (0,1), (0,-1), (-1, 0)]
        l = []
        n = []
        b = []
        x = None
        y = None
        if movement.x > 0:
            l.append(ol[0])
            x, g = ol[0]
        elif movement.x < 0:
            l.append(ol[3])
            x, g = ol[3]
        if movement.y > 0:
            l.append(ol[1])
            g, y = ol[1]
        elif movement.y < 0:
            l.append(ol[2])
            g, y = ol[2]
        
        if x is not None and y is not None:
            l.append((x, y))
        
        g = map.getBlock(round(self.position.x), round(self.position.y), round(self.position.z)) != False
        
        for x, y in l:
            for z in range(1, 5):
                if map.getBlock(round(self.position.x+x), round(self.position.y+y), round(self.position.z+z)) != False:
                    b.append(True)
                else:
                    b.append(False)
            
            for z in range((2 if g and not (b[0] and not b[1] and ((b[2]) if self.crouching else (b[2] or b[3]))) else 1),(3 if self.crouching else 4)):
                if map.getBlock(round(self.position.x+x), round(self.position.y+y), round(self.position.z+z)) != False:
                    n.append((x, y))
                    break
            b = []
        return n
    
    def move(self, time, map):
        oldPos = self.position
        movement = (self.getWorldVector( self.velocity.update(z=0) ).update(z=0).getUnitVector( self.getSpeed() ) + Vector(0, 0, self.velocity.z)) * time
        biw = self.getBlocksInWay(map, movement)
        self.position += movement
        
        for x, y in biw:
            if abs((self.position.x*abs(x) + self.position.y*abs(y)) - (round(self.position.x*abs(x)+abs(x)*movement.x) + round(self.position.y*abs(y)+abs(y)*movement.y))) < 0.5 + 0.2*abs(x) + 0.2*abs(y):
                #print (self.position.x, self.position.y, x, y)
                if x != 0:
                    if round(self.position.x) != round(oldPos.x):
                        self.position.x = round(oldPos.x)+0.3*x
                    else:
                        self.position.x = round(self.position.x)+0.3*x
                else:
                    if round(self.position.y) != round(oldPos.y):
                        self.position.y = round(oldPos.y)+0.3*y
                    else:
                        self.position.y = round(self.position.y)+0.3*y
                #print ("-->", self.position.x, self.position.y)
                
        if movement.z > 0:
            if map.getBlock(round(self.position.x), round(self.position.y), round(self.position.z+(3 if self.crouching else 4))) != False:
                if abs(self.position.z - round(self.position.z+movement.z)) < 0.7:
                    self.position.z = round(self.position.z)+0.3
                    self.velocity.z = -1
        
        """
        success = True
        if map.getBlock(round(self.position.x), round(self.position.y), round(self.position.z+3)) != False and not self.crouching:
            success = False
        elif map.getBlock(round(self.position.x), round(self.position.y), round(self.position.z+2)) != False:
            success = False
            
        if not success:
            #direc = movement.getMainDirection()
            #if direc is not None:
            #    movement[direc] = 0
            #else:
            self.position = oldPos
            ns = self.getNeighborSides(map)
            if movement.x > 0:
                if ns[0]:
                    movement.x = 0
            elif movement.x < 0:
                if ns[3]:
                    movement.x = 0
            if movement.y > 0:
                if ns[1]:
                    movement.y = 0
            elif movement.y < 0:
                if ns[2]:
                    movement.y = 0
            self.position += movement
        """
        
        """if map.getBlock(round(self.position.x), round(self.position.y), round(self.position.z+1)) != False and self.jumping:
            self.position = oldPos
            return False"""
        
    """def fall(self, time, maxHeight):
        fallVector = Vector(0,0,-1) * self.fallSpeed * time
        if float(fallVector) > maxHeight:
            fallVetor = fallVector.getUnitVector(maxHeight)
        self.position += fallVector"""
            
