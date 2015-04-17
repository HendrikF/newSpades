from pyglet.gl import *
from shared.Player import Player
from math import sin

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
        self.angleLeg = lambda: sin(self.animationTime)*30
        self.animationSpeed = 5
        self.animationTime = 0
    
    def updateFromMessage(self, msg):
        self.interpolateTo((msg.x, msg.y, msg.z))
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
            dx = self.dx,
            dz = self.dz,
            yaw = self.yaw,
            pitch = self.pitch,
            crouching = self.crouching,
            )
    
    def interpolateTo(self, pos):
        distance = (pos[0]-self.position[0])**2 + (pos[1]-self.position[1])**2 + (pos[2]-self.position[2])**2
        if distance >= 0.09: #0.3**2
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
        moving = any((self._dx, self._dz))
        for name, part in self.model.items():
            if name in ('head', 'arms', 'tool'):
                part.draw(pitch=self.pitch)
            elif name == 'legl' and moving:
                part.draw(pitch=self.angleLeg())
            elif name == 'legr' and moving:
                part.draw(pitch=-self.angleLeg())
            else:
                part.draw()
        glPopMatrix()
    
    def playSound(self, name):
        self.sounds.play(name)
    
    def update(self, time, map):
        self.animationTime += time * self.animationSpeed
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
