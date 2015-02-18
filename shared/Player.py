import math
from shared.Map import FACES

def radians(deg):
    return deg*0.01745329251994329577 #deg*PI/180

def degrees(rad):
    return rad/0.01745329251994329577 #deg/PI/180

def correct(x):
    return 0 if abs(x) <= 0.000001 else x

class Player(object):
    def __init__(self, username=''):
        self.username = username
        
        self._dx = 0
        self._dy = 0
        self._dz = 0
        self.position = (0, 2, 0)
        self._yaw   = 90
        self._pitch = 0
        self._crouching = False
        
        self._speed = 5
        self._maxFallSpeed = 50
        self._gravity = 20
        self._height = 3
        self._armLength = 5
    
    @property
    def dx(self):
        return self._dx
    @dx.setter
    def dx(self, v):
        self._dx = v
    
    @property
    def dy(self):
        return self._dy
    @dy.setter
    def dy(self, v):
        self._dy = v
    
    @property
    def dz(self):
        return self._dz
    @dz.setter
    def dz(self, v):
        self._dz = v
    
    @property
    def yaw(self):
        return self._yaw
    @yaw.setter
    def yaw(self, v):
        self._yaw = v
    
    @property
    def pitch(self):
        return self._pitch
    @pitch.setter
    def pitch(self, v):
        self._pitch = v
    
    @property
    def crouching(self):
        return self._crouching
    @crouching.setter
    def crouching(self, v):
        self._crouching = v
    
    @property
    def speed(self):
        return self._speed if not self.crouching else self._speed*0.7
    
    @property
    def maxFallSpeed(self):
        return self._maxFallSpeed
    @maxFallSpeed.setter
    def maxFallSpeed(self, v):
        self._maxFallSpeed = v
    
    @property
    def gravity(self):
        return self._gravity
    @gravity.setter
    def gravity(self, v):
        self._gravity = v
    
    @property
    def height(self):
        return self._height if not self.crouching else self._height-1
    
    @property
    def armLength(self):
        return self._armLength
    @armLength.setter
    def armLength(self, v):
        self._armLength = v
    
    @property
    def eyePosition(self):
        x, y, z = self.position
        return (x, y+self.height-1, z) # should be 2.5 but you cannot build the block in eye-height ??
    
    def jump(self):
        # TODO: Tell server
        pass
    
    def update(self, time, map):
        """Updates the players fallspeed and its position"""
        x, y, z = self.position
        dx, dz = self.calcMovement(time)
        self.dy = self.calcFallSpeed(time)
        dy = self.dy * time
        self.position = self.calcCollision((x+dx, y+dy, z+dz), map)
    
    def calcMovement(self, time):
        """Return the current vector of horizontal movement (dx, dz)"""
        dx, dz = self.getMotionVector()
        d = self.speed * time
        return dx*d, dz*d
    
    def calcFallSpeed(self, time):
        """Returns the accelerated fallspeed of the player"""
        return max(self.dy - self.gravity * time, -self.maxFallSpeed)
    
    def calcCollision(self, position, map):
        return self._collide(position, map)
    
    def _collide(self, position, map):
        """Checks if the player is colliding with any blocks in the world and returns its position.
        This resets the fallspeed of the player when necessary!"""
        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall grass. If >= .5, you'll fall through the ground.
        pad = 0
        p = list(position)
        np = (round(p[0]), round(p[1]), round(p[2]))
        for face in FACES:  # check all surrounding blocks
            for i in range(3):  # check each dimension independently
                if not face[i]:
                    continue
                # How much overlap you have with this dimension.
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue
                for dy in range(self.height):  # check each height
                    op = list(np)
                    op[1] += dy
                    op[i] += face[i]
                    if tuple(op) not in map.world:
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, 1, 0) or face == (0, -1, 0):
                        # You are colliding with the ground or ceiling
                        # stop falling / rising.
                        self.dy = 0
                    break
        return tuple(p)
    
    def getMotionVector(self):
        """Returns the motion vector in world coordinates"""
        if any((self.dx, self.dz)):
            x = radians(self.yaw - 90)
            x += math.atan2(self.dz, self.dx)
            dx = math.cos(x)
            dz = math.sin(x)
        else:
            return (0, 0)
        return (correct(dx), correct(dz))
    
    def getSightVector(self):
        """Returns the vector the player is looking along"""
        yawMin90Rad = radians(self.yaw - 90)
        pitchRad = radians(self.pitch)
        m = math.cos(pitchRad)
        dy = math.sin(pitchRad)
        dx = math.cos(yawMin90Rad) * m
        dz = math.sin(yawMin90Rad) * m
        return (correct(dx), correct(dy), correct(dz))
    
    def playSound(self, name):
        pass
    
    def __repr__(self):
        return '<{} ({}) at (x{}, y{}, z{})>'.format(self.__class__.__name__, self.username, *self.position)
