from shared.BaseWindow import BaseWindow
from shared.Map import Map
from shared.Player import Player
from pyglet.gl import *
from pyglet.window import key, mouse
from shared.ColorPicker import ColorPicker

import logging
logger = logging.getLogger(__name__)

class NewSpades(BaseWindow):
    ##################
    # General stuff
    def __init__(self, *args, **kw):
        super(NewSpades, self).__init__(*args, **kw)
        self.label = pyglet.text.Label('', font_name='Ubuntu', font_size=10,
            x=10, y=self.height, anchor_x='left', anchor_y='top',
            color=(0, 0, 0, 255))
        self.map = Map(maxFPS=self.maxFPS, farplane=self.farplane)
        self.player = Player()
        self.keys = {
            "FWD": key.W,
            "BWD": key.S,
            "LEFT": key.A,
            "RIGHT": key.D,
            "JUMP": key.SPACE,
            "CROUCH": key.LSHIFT,
            "FULLSCREEN": key.F11,
            "CP-R": key.RIGHT,
            "CP-L": key.LEFT,
            "CP-U": key.UP,
            "CP-D": key.DOWN
        }
        pyglet.resource.path = ['client/resources', 'shared/resources']
        pyglet.resource.reindex()
        self.crosshair = pyglet.sprite.Sprite(pyglet.resource.image('crosshair.png'))
        
        self.colorPicker = ColorPicker()
    
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
        self.crosshair.draw()
        
        glPushMatrix()
        glTranslatef(self.width-self.colorPicker.width, 0, 0)
        self.colorPicker.draw()
        glPopMatrix()
    
    def draw3d(self):
        x, y, z = self.player.eyePosition
        dx, dy, dz = self.player.getSightVector()
        gluLookAt(
            x,      y-0.5,      z,     # the -0.5 are for the same fix as Player.eyeHeight
            x+dx,   y+dy-0.5,   z+dz,  #
            0,      1,          0
        )
        self.map.draw()
        self.map.drawBlockLookingAt(self.player.eyePosition, self.player.getSightVector(), self.player.armLength)
    
    def onResize(self, width, height):
        self.label.y = height
        self.crosshair.x = (width-self.crosshair.width)/2
        self.crosshair.y = (height-self.crosshair.height)/2
    
    def update(self, dt):
        self.map.update(self.player.position)
    
    ##############
    # Physics
    
    def updatePhysics(self, dt):
        self.player.move(dt, self.map)
    
    #########################
    # Client Interaction
    
    def handleMousePress(self, x, y, button, modifiers):
        block, previous = self.map.getBlocksLookingAt(self.player.eyePosition, self.player.getSightVector(), self.player.armLength)
        if button == mouse.RIGHT:
            if previous:
                self.map.addBlock(previous, self.colorPicker.getRGB())
        elif button == mouse.LEFT and block:
            self.map.removeBlock(block)
    
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
        if press:
            if symbol == key.ESCAPE:
                self.set_fullscreen(False)
                if self.exclusive:
                    self.set_exclusive_mouse(False)
                else:
                    self.close()
            elif symbol == self.keys["FWD"]:
                self.player.velocity[0] -= 1
            elif symbol == self.keys["BWD"]:
                self.player.velocity[0] += 1
            elif symbol == self.keys["LEFT"]:
                self.player.velocity[1] -= 1
            elif symbol == self.keys["RIGHT"]:
                self.player.velocity[1] += 1
            elif symbol == self.keys["JUMP"]:
                self.player.jump()
            elif symbol == self.keys["CROUCH"]:
                self.player.crouching = True
            elif symbol == self.keys["FULLSCREEN"]:
                self.set_fullscreen(not self.fullscreen)
            elif symbol == self.keys["CP-R"]:
                self.colorPicker.input(x=1)
            elif symbol == self.keys["CP-L"]:
                self.colorPicker.input(x=-1)
            elif symbol == self.keys["CP-U"]:
                self.colorPicker.input(y=1)
            elif symbol == self.keys["CP-D"]:
                self.colorPicker.input(y=-1)
        
        else: #not press / release
            if symbol == self.keys["FWD"]:
                self.player.velocity[0] += 1
            elif symbol == self.keys["BWD"]:
                self.player.velocity[0] -= 1
            elif symbol == self.keys["LEFT"]:
                self.player.velocity[1] += 1
            elif symbol == self.keys["RIGHT"]:
                self.player.velocity[1] -= 1
            elif symbol == self.keys["CROUCH"]:
                self.player.crouching = False
