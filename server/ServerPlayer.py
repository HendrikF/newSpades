from shared.Player import Player

class ServerPlayer(Player):
    """Extends shared.Player.Player by applyBoundaryDamage() and peer"""
    def __init__(self, peer, *args, **kw):
        super(ServerPlayer, self).__init__(*args, **kw)
        self.peer = peer
    
    def update(self, time, map):
        super(ServerPlayer, self).update(time, map)
        self.applyBoundaryDamage(time, map)
    
    def applyBoundaryDamage(self, time, map):
        if map.border_dps == 0:
            return
        x, y, z = self.position
        if  map.border_x[0] > x > map.border_x[1] or \
            map.border_y[0] > y > map.border_y[1] or \
            map.border_z[0] > z > map.border_z[1]:
            self.damage(map.border_dps*time)
