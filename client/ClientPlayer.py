from pyglet.gl import *
from shared.Player import Player

class ClientPlayer(Player):
    """Extends shared.Player.Player by model, draw(), sounds and playSound()"""
    def __init__(self, model, sounds, *args, **kw):
        super(ClientPlayer, self).__init__(*args, **kw)
        self.model = model
        self.sounds = sounds
    
    def draw(self):
        glPushMatrix()
        x, y, z = self.position
        glTranslatef(x, y-1, z)
        x, y = self.orientation
        x -= 90
        glRotatef(-x, 0, 1, 0)
        for name, part in self.model.items():
            if name == 'head':
                part.draw(pitch=y)
            else:
                part.draw()
        glPopMatrix()
    
    def playSound(self, name):
        self.sounds.play(name)
