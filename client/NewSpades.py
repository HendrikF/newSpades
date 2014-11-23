from client.BaseWindow import BaseWindow
from shared.Map import Map
from shared.Player import Player
from pyglet.gl import *
from pyglet.window import key

import logging
logger = logging.getLogger(__name__)

class NewSpades(BaseWindow):
    ##################
    # General stuff
    def __init__(self, *args, **kw):
        self.label = pyglet.text.Label('', font_name='Ubuntu', font_size=10,
            x=10, y=self.height, anchor_x='left', anchor_y='top',
            color=(0, 0, 0, 255))
        # label must be set, because init can trigger on_resize, which uses label
        super(NewSpades, self).__init__(*args, **kw)
        self.map = Map(maxFPS=self.maxFPS, farplane=self.farplane)
        self.player = Player()
        self.keys = {
            "FWD": key.W,
            "BWD": key.S,
            "LEFT": key.A,
            "RIGHT": key.D,
            "JUMP": key.SPACE,
            "CROUCH": key.LSHIFT,
            "FULLSCREEN": key.F11
        }
    
    def start(self):
        self.map.load()
        super(NewSpades, self).start()
    
    ###############
    # Rendering
    
    def draw2d(self):
        x, y, z = self.player.position
        self.label.text = '%02d (%.2f, %.2f, %.2f)' % (
            pyglet.clock.get_fps(), x, y, z)
        self.label.draw()
    
    def draw3d(self):
        x, y, z = self.player.eyePosition
        dx, dy, dz = self.player.getSightVector()
        gluLookAt(
            x,      y,      z,
            x+dx,   y+dy,   z+dz,
            0,      1,      0
        )
        self.map.draw()
        self.map.drawBlockLookingAt(self.player.eyePosition, self.player.getSightVector(), self.player.armLength)
    
    def onResize(self, width, height):
        self.label.y = height
    
    def update(self, dt):
        self.map.update(self.player.position)
    
    ##############
    # Physics
    
    def updatePhysics(self, dt):
        self.player.move(dt)
    
    #########################
    # Client Interaction
    
    def handleMousePress(self, x, y, button, modifiers):
        pass
    
    def handleMouseMove(self, dx, dy):
        m = 0.1
        self.player.orientation[0] += dx * m
        self.player.orientation[1] += dy * m
        if self.player.orientation[0] < 0:
            self.player.orientation[0] += 360
        elif self.player.orientation[0] >= 360:
            self.player.orientation[0] -= 360
        if self.player.orientation[1] < -90:
            self.player.orientation[1] = -90
        elif self.player.orientation[1] > 90:
            self.player.orientation[1] = 90
    
    def handleKeyboard(self, symbol, modifiers, press):
        if symbol == key.ESCAPE:
            self.close()
        
        if press:
            if symbol == self.keys["FWD"]:
                self.player.velocity[0] -= 1
            elif symbol == self.keys["BWD"]:
                self.player.velocity[0] += 1
            elif symbol == self.keys["LEFT"]:
                self.player.velocity[1] -= 1
            elif symbol == self.keys["RIGHT"]:
                self.player.velocity[1] += 1
            elif symbol == self.keys["JUMP"]:
                self.player.dy += 1
            elif symbol == self.keys["CROUCH"]:
                self.player.dy -= 1
            elif symbol == self.keys["FULLSCREEN"]:
                self.set_fullscreen(not self.fullscreen)
        
        else: #not press / release
            if symbol == self.keys["FWD"]:
                self.player.velocity[0] += 1
            elif symbol == self.keys["BWD"]:
                self.player.velocity[0] -= 1
            elif symbol == self.keys["LEFT"]:
                self.player.velocity[1] += 1
            elif symbol == self.keys["RIGHT"]:
                self.player.velocity[1] -= 1
            elif symbol == self.keys["JUMP"]:
                self.player.dy -= 1
            elif symbol == self.keys["CROUCH"]:
                self.player.dy += 1
