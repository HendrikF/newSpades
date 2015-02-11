from client.DrawablePlayer import DrawablePlayer
from shared import Messages

class ControllablePlayer(DrawablePlayer):
    """When updated, it sends the updates to the server"""
    def __init__(self, endpoint, *args, **kw):
        self.endpoint = endpoint
        
        super().__init__(*args, **kw)
    
    def applyUpdate(self, key, value):
        """When server sends updates, dont use the public API, which would contact the server (recursion)"""
        if key in ('dx', 'dy', 'dz', 'yaw', 'pitch'):
            return
        setattr(self, '_'+key, value)
    
    def updateFromMsg(self, msg):
        self.position = (msg.x, msg.y, msg.z)
        self.dy = msg.dy
        self._crouching = msg.crouching
    
    # User input (dx, dz, yaw, pitch, crouching) is sent to server, when updated
    # => We use properties to catch the updates
    
    @property
    def dx(self):
        return self._dx
    @dx.setter
    def dx(self, v):
        if v != self._dx:
            self.sendUpdate('dx', v)
        self._dx = v
    
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
    
    def sendUpdate(self, key, value):
        self.endpoint.send(Messages.Update(key=key, value=value))
