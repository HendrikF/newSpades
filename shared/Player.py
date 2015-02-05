import math
from shared.Map import FACES
from shared import Messages

def radians(deg):
    return deg*0.01745329251994329577 #deg*PI/180

def degrees(rad):
    return rad/0.01745329251994329577 #deg/PI/180

def correct(x):
    return 0 if abs(x) <= 0.000001 else x

class Player(object):
    def __init__(self, username=''):
        self.username = username
        
        # Dynamic
        self.velocity = [0, 0]
        self.dy = 0
        self.position = (0, 2, 0)
        self.orientation = [90, 0]
        self.crouching = False
        self.health = 100
        self.respawnTime = 0
        self.jumpCount = 0
        
        # Static
        self._speed = 5
        self.maxFallSpeed = 50
        self._gravity = 20
        self.jumpSpeed = 0
        self._jumpHeight = 0
        self.jumpHeight = 2.2 # Trigger calculation of jumpSpeed
        self._height = 3
        self.armLength = 5
        self.maxHealth = 100
        self.maxRespawnTime = 5
        self.maxJumpCount = 1
    
    @property
    def height(self):
        return self._height if not self.crouching else self._height-1
    
    @property
    def eyePosition(self):
        x, y, z = self.position
        return (x, y+self.height-1, z) # should be 2.5 but you cannot build the block in eye-height ??
    
    @property
    def speed(self):
        return self._speed if not self.crouching else self._speed*0.7
    
    @property
    def jumpHeight(self):
        return self._jumpHeight
    @jumpHeight.setter
    def jumpHeight(self, v):
        self._jumpHeight = v
        self._recalcJumpSpeed()
    
    @property
    def gravity(self):
        return self._gravity
    @gravity.setter
    def gravity(self, v):
        self._gravity = v
        self._recalcJumpSpeed()
    
    def _recalcJumpSpeed(self):
        self.jumpSpeed = math.sqrt(2*self._gravity*self._jumpHeight)
    
    @property
    def respawning(self):
        return self.respawnTime > 0
    
    def updateFromMsg(self, msg):
        if msg.username == self.username:
            self.position = (msg.posx, msg.posy, msg.posz)
            self.velocity = [msg.velx, msg.velz]
            self.dy = msg.vely
            self.crouching = msg.crouching
            self.orientation = [msg.yaw, msg.pitch]
    
    def getUpdateMsg(self):
        msg = Messages.PlayerUpdateMsg()
        msg.username = self.username
        msg.posx, msg.posy, msg.posz = self.position
        msg.velx, msg.velz = self.velocity
        msg.vely = self.dy
        msg.crouching = self.crouching
        msg.yaw, msg.pitch = self.orientation
        return msg
    
    def damage(self, dmg):
        if not self.respawning:
            self.health -= dmg
            if self.health > self.maxHealth:
                self.health = self.maxHealth
            if self.health <= 0:
                self.health = 0
                self.respawnTime = self.maxRespawnTime
                self.playSound("death")
    
    def respawn(self, time):
        if self.respawning:
            self.respawnTime -= time
            if not self.respawning:
                self.position = (0, 2, 0)
                self.orientation = [90, 0]
                self.dy = 0 # without this the player instantly dies if his corpse never hit the ground
                self.health = self.maxHealth
    
    def jump(self):
        if self.canJump:
            self.jumpCount += 1
            self._jump()
    
    @property
    def canJump(self):
        return not self.respawning and self.jumpCount < self.maxJumpCount and ((self.jumpCount==0 and self.dy==0) or self.jumpCount > 0)
    
    def _jump(self):
        self.dy = self.jumpSpeed
        self.playSound("jump")
    
    def update(self, time, map):
        x, y, z = self.position
        dx, dz = self.calcMovement(time)
        dy = self.calcGravity(time)
        self.position = self.calcCollision((x+dx, y+dy, z+dz), map)
        self.respawn(time)
    
    def calcMovement(self, time):
        dx, dz = self.getMotionVector()
        d = self.speed * time
        return dx*d, dz*d
    
    def calcGravity(self, time):
        self.dy -= time * self.gravity
        self.dy = max(self.dy, -self.maxFallSpeed)
        return self.dy * time
    
    def calcCollision(self, position, map):
        return self._collide(position, map)
    
    def _collide(self, position, map):
        """Checks if the player is colliding with any blocks in the world and returns its position"""
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
                        # get fall damage
                        if self.dy < -15: # ca 5 blocks falling
                            self.damage((-self.dy-15)*3) # maxFallSpeed = 50 --> (50 - 15)*3 = 35*3 = 105 -> dead
                            if not self.respawning:
                                self.playSound("fallhurt")
                        elif self.dy < -7:
                            if not self.respawning:
                                self.playSound("land")
                        if self.dy < 0:
                            # reset jumps if hitting ground
                            self.jumpCount = 0
                        # stop falling / rising.
                        self.dy = 0
                    break
        return tuple(p)
    
    def getMotionVector(self):
        """Returns the motion vector in world coordinates"""
        if any(self.velocity):
            x = radians(self.orientation[0] - 90)
            x += math.atan2(self.velocity[1], self.velocity[0])
            dx = math.cos(x)
            dz = math.sin(x)
        else:
            return (0, 0)
        return (correct(dx), correct(dz))
    
    def getSightVector(self):
        """Returns the vector the player is looking along"""
        x, y = self.orientation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(radians(y))
        dx = math.cos(radians(x - 90)) * m
        dz = math.sin(radians(x - 90)) * m
        return (correct(dx), correct(dy), correct(dz))
    
    def playSound(self, name):
        """To be implemented in the client (server would be too noisy :))"""
        pass
    
    def __repr__(self):
        return '<{} ({}) at (x{}, y{}, z{})>'.format(self.__class__.__name__, self.username, *self.position)
