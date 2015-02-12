from shared.Player import Player
from shared import Messages
import math

class ServerPlayer(Player):
    """When some properties of this class get updated, a Message is sent to the client"""
    def __init__(self, peer, *args, **kw):
        self.peer = peer
        
        super().__init__(*args, **kw)
        
        self.health = 100
        self.respawnTime = 0
        self.jumpSpeed = 0
        self.jumpHeight = 2.2 # Trigger calculation of jumpSpeed
        
        self.maxHealth = 100
        self.maxRespawnTime = 5
        self.jumpCount = 0
        self.maxJumpCount = 1
    
    def applyUpdate(self, key, value):
        """Here we use the public API to apply the updates, because
        we have to send the updates for THIS client to ALL clients"""
        setattr(self, key, value)
    
    # User properties are sent to clients when updated
    # => We use properties to catch the updates
    
    @property
    def dx(self):
        return self._dx
    @dx.setter
    def dx(self, v):
        if v != self._dx:
            self.sendUpdate('dx', v)
        self._dx = v
    
    # dy is not sent when updated, because of extreme network spam when accelerating !!
    
    @property
    def dz(self):
        return self._dz
    @dz.setter
    def dz(self, v):
        if v != self._dz:
            self.sendUpdate('dz', v)
        self._dz = v
    
    @property
    def yaw(self):
        return self._yaw
    @yaw.setter
    def yaw(self, v):
        if v < 0:       v += 360
        elif v >= 360:  v -= 360
        if v != self._yaw:
            self.sendUpdate('yaw', v)
        self._yaw = v
    
    @property
    def pitch(self):
        return self._pitch
    @pitch.setter
    def pitch(self, v):
        if v < -90:     v = -90
        elif v > 90:    v = 90
        if v != self._pitch:
            self.sendUpdate('pitch', v)
        self._pitch = v
    
    @property
    def crouching(self):
        return self._crouching
    @crouching.setter
    def crouching(self, v):
        if v != self._crouching:
            self.sendUpdate('crouching', v)
        self._crouching = v
    
    @Player.speed.setter
    def speed(self, v):
        if v != self._speed:
            self.sendUpdate('speed', v)
        self._speed = v
    
    @property
    def maxFallSpeed(self):
        return self._maxFallSpeed
    @maxFallSpeed.setter
    def maxFallSpeed(self, v):
        if v != self._maxFallSpeed:
            self.sendUpdate('maxFallSpeed', v)
        self._maxFallSpeed = v
    
    @Player.height.setter
    def height(self, v):
        if v != self._height:
            self.sendUpdate('height', v)
        self._height = v
    
    @property
    def armLength(self):
        return self._armLength
    @armLength.setter
    def armLength(self, v):
        if v != self._armLength:
            self.sendUpdate('armLength', v)
        self._armLength = v
    
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
        self.sendUpdate('gravity', v)
        self._gravity = v
        self._recalcJumpSpeed()
    
    def _recalcJumpSpeed(self):
        self.jumpSpeed = math.sqrt(2*self._gravity*self._jumpHeight)
    
    @property
    def respawning(self):
        return self.respawnTime > 0
    
    def damage(self, dmg):
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
                self.yaw = 90
                self.pitch = 0
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
        super().update(time, map)
        self.respawn(time)
        #self.applyBoundaryDamage(time, map)
    
    def applyBoundaryDamage(self, time, map):
        if map.border_dps == 0:
            return
        x, y, z = self.position
        if  map.border_x[0] > x > map.border_x[1] or \
            map.border_y[0] > y > map.border_y[1] or \
            map.border_z[0] > z > map.border_z[1]:
            self.damage(map.border_dps*time)
    
    def playSound(self, name):
        pass
    
    def sendUpdate(self, key, value):
        self.peer.endpoint.send(Messages.Update(username=self.username, key=key, value=value))
