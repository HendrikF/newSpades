from shared.Player import Player

class ServerPlayer(Player):
    """When some properties of this class get updated, a Message is sent to the client"""
    def __init__(self, peer, *args, **kw):
        self.peer = peer
        
        super().__init__(*args, **kw)
        
        self.health = 100
        self.respawnTime = 0
        
        self.maxHealth = 100
        self.maxRespawnTime = 5
    
    def updateFromMessage(self, msg):
        self.dx = msg.dx
        self.dy = msg.dy
        self.dz = msg.dz
        self.yaw = msg.yaw
        self.pitch = msg.pitch
        self.crouching = msg.crouching
    
    def getUpdateMessage(self, Msg):
        x, y, z = self.position
        return Msg(
            username = self.username,
            x = x,
            y = y,
            z = z,
            dx = self.dx,
            dy = self.dy,
            dz = self.dz,
            yaw = self.yaw,
            pitch = self.pitch,
            crouching = self.crouching,
            )
    
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
