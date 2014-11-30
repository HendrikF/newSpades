import math
from shared.Map import FACES

def radians(deg):
    return deg*0.01745329251994329577 #deg*PI/180

def correct(x):
    return 0 if abs(x) <= 0.000001 else x

class Player(object):
    def __init__(self, sounds, username=''):
        self.username = username
        
        # Dynamic
        self.velocity = [0, 0]
        self.dy = 0
        self.position = (0, 2, 0)
        self.orientation = [90, 0]
        self.crouching = False
        self.health = 100
        self.respawning = False
        self.respawnTime = 0
        self.jumpCount = 0
        
        # Static
        self._speed = 5
        self.maxFallSpeed = 50
        self.gravity = 20
        self.jumpHeight = 2.2
        self.jumpSpeed = math.sqrt(2*self.gravity*self.jumpHeight)
        self._height = 3
        self.armLength = 5
        self.maxHealth = 100
        self.maxRespawnTime = 5
        self.maxJumpCount = 1
        self.sounds = sounds
    
    @property
    def height(self):
        return self._height if not self.crouching else self._height-1
    
    @property
    def eyePosition(self):
        x, y, z = self.position
        return (x, y+self.height, z) # should be 2.5 but you cannot build the block in eye-height ??
    
    @property
    def speed(self):
        return self._speed
    
    def damage(self, dmg):
        if not self.respawning:
            self.health -= dmg
            if self.health > self.maxHealth:
                self.health = self.maxHealth
            if self.health <= 0:
                self.health = 0
                self.respawning = True
                self.respawnTime = self.maxRespawnTime
                self.sounds.play("death")
                #self.position = (0, 2, 0)
                #self.orientation = [90, 0]
            
    def respawn(self, time):
        if not self.respawning:
            return
        self.respawnTime -= time
        if self.respawnTime < 0:
            self.position = (0, 2, 0)
            self.orientation = [90, 0]
            self.dy = 0 # without this the player instantly dies if his corpse never hit the ground
            self.health = self.maxHealth
            self.respawning = False
    
    def jump(self):
        if self.jumpCount < self.maxJumpCount:
            self.dy = self.jumpSpeed
            self.sounds.play("jump")
            self.jumpCount += 1
    
    def move(self, time, map):
        x, y, z = self.position
        dx, dz = self.getMotionVector()
        d = self.speed * time
        dx, dz = dx*d, dz*d
        # GRAVITY
        self.dy -= time * self.gravity
        self.dy = max(self.dy, -self.maxFallSpeed)
        dy = self.dy * time
        # COLLIDE
        self.position = self._collide((x+dx, y+dy, z+dz), map)
        # DAMAGE
        self._boundaryDamage(time, map)
    
    def _boundaryDamage(self, time, map):
        x, y, z = self.position
        if  x < map.border_x[0] or x > map.border_x[1] or y < map.border_y[0] or y > map.border_y[1] or z < map.border_z[0] or z > map.border_z[1]:
            self.damage(map.border_dps*time)
    
    def _collide(self, position, map):
        """Checks if the player is colliding with any blocks in the world and returns its position"""
        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall grass. If >= .5, you'll fall through the ground.
        pad = 0.25
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
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        # You are colliding with the ground or ceiling
                        # get fall damage
                        if self.dy < -15: # ca 5 blocks falling
                            self.damage((-self.dy-15)*3) # maxFallSpeed = 50 --> (50 - 15)*3 = 35*3 = 105 -> dead
                            self.sounds.play("fallhurt")
                        elif self.dy < -7:
                            self.sounds.play("land")
                        
                        # stop falling / rising.
                        self.dy = 0
                        # reset jumps
                        self.jumpCount = 0
                    break
        return tuple(p)
    
    def getMotionVector(self):
        if any(self.velocity):
            x = self.orientation[0]
            x_angle = math.radians(x + math.degrees(math.atan2(self.velocity[0], self.velocity[1])))
            dx = math.cos(x_angle)
            dz = math.sin(x_angle)
        else:
            return (0, 0)
        return (correct(dx), correct(dz))
    
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
        return (correct(dx), correct(dy), correct(dz))
    
    def __repr__(self):
        return '<Player ({}) at (x{}, y{}, z{})>'.format(self.username, *self.position)
