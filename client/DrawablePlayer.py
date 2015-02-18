from pyglet.gl import *
from shared.Player import Player

import logging
logger = logging.getLogger(__name__)

class DrawablePlayer(Player):
    """Extends shared.Player.Player by model, draw(), sounds and playSound()"""
    def __init__(self, model, sounds, *args, **kw):
        self.model = model
        self.sounds = sounds
        
        super().__init__(*args, **kw)
        
        self.positionToInterpolateTo = (0, 0, 0)
        self.interpolationTime = 0.2
        self.interpolating = 0
    
    def applyUpdate(self, key, value):
        setattr(self, key, value)
    
    def updateFromMsg(self, msg):
        # dont use properties -> faster
        self.interpolateTo((msg.x, msg.y, msg.z))
        self._dx = msg.dx
        self._dy = msg.dy
        self._dz = msg.dz
        self._yaw = msg.yaw
        self._pitch = msg.pitch
        self._crouching = msg.crouching
    
    def interpolateTo(self, pos):
        distance = (pos[0]-self.position[0])**2 + (pos[1]-self.position[1])**2 + (pos[2]-self.position[2])**2
        if distance >= 0.3**2:
            logger.info('Interpolating positions of %s', self)
            self.positionToInterpolateTo = pos
            self.interpolating = self.interpolationTime
        else:
            self.position = pos
    
    def draw(self):
        glPushMatrix()
        x, y, z = self.position
        glTranslatef(x, y-1, z)
        # -(self.yaw-90)
        glRotatef(90-self.yaw, 0, 1, 0)
        for name, part in self.model.items():
            if name == 'head':
                part.draw(pitch=self.pitch)
            else:
                part.draw()
        glPopMatrix()
    
    def playSound(self, name):
        self.sounds.play(name)
    
    def update(self, time, map):
        if self.interpolating > 0:
            # get coordinates
            x, y, z = self.position
            r, s, t = self.positionToInterpolateTo
            # we move the interpolation target by our orientation to smooth it
            dx, dz = self.calcMovement(time)
            r, t = r + dx, t + dz
            dt = self.interpolating / time
            # calc distance to interpolate
            # divide this distance in dt parts
            # in each frame we will move the player by one part
            dx = (r - x) / dt
            dy = (s - y) / dt
            dz = (t - z) / dt
            self.position = (x+dx, y+dy, z+dz)
            # we are done with this part
            self.interpolating -= time
        # dont stop movin even if we interpolate to smooth it
        super().update(time, map)
