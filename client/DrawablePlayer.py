from pyglet.gl import *
from shared.Player import Player

class DrawablePlayer(Player):
    """Extends shared.Player.Player by model, draw(), sounds and playSound()"""
    def __init__(self, model, sounds, *args, **kw):
        self.model = model
        self.sounds = sounds
        super().__init__(*args, **kw)
    
    def applyUpdate(self, key, value):
        setattr(self, key, value)
    
    def updateFromMsg(self, msg):
        self.position = (msg.x, msg.y, msg.z)
        self.dx = msg.dx
        self.dy = msg.dy
        self.dz = msg.dz
        self.yaw = msg.yaw
        self.pitch = msg.pitch
        self.crouching = msg.crouching
    
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
