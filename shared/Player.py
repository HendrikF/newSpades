import math

def radians(deg):
    return deg*0.01745329251994329577 #deg*PI/180

class Player(object):
    def __init__(self, username=''):
        self.username = username
        
        self.velocity = [0, 0]
        self.dy = 0
        self.position = (0, 0, 0)
        self.orientation = [90, 0]
        self._speed = 5
        self.armLength = 5
    
    def getHeight(self):
        return self.height-1 if self.crouching else self.height
    
    @property
    def eyePosition(self):
        x, y, z = self.position
        return (x, y+2.5, z)
    
    @property
    def speed(self):
        return self._speed
    
    def move(self, time):
        x, y, z = self.position
        dx, dz = self.getMotionVector()
        dy = self.dy
        d = self.speed * time
        dx, dy, dz = dx*d, dy*d, dz*d
        self.position = x+dx, y+dy, z+dz
    
    def getMotionVector(self):
        if any(self.velocity):
            x = self.orientation[0]
            x_angle = math.radians(x + math.degrees(math.atan2(self.velocity[0], self.velocity[1])))
            dx = math.cos(x_angle)
            dz = math.sin(x_angle)
        else:
            return (0, 0)
        return (dx, dz)
    
    def getSightVector(self):
        x, y = self.orientation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return (dx, dy, dz)
    
    def __repr__(self):
        return '<Player ({}) at (x{}, y{}, z{})>'.format(self.username, *self.position)
