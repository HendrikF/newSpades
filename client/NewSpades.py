import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
from shared.BaseWindow import BaseWindow
from shared.Map import Map
from shared.Player import Player
from shared.ColorPicker import ColorPicker
from client.Sounds import Sounds
from shared.CommandLine import CommandLine
from client.Networking import Networking
from client.GuiManager import GuiManager
from shared.Model import Model
from shared import Messages
import math
import time

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
        self.deathScreen = pyglet.text.Label('YOU DIED!', font_name='Ubuntu', font_size=50,
            x=self.width/2, y=self.height*3/4, anchor_x='center', anchor_y='center',
            color=(255, 0, 0, 255))
        self.healthLabel = pyglet.text.Label('100', font_name='Ubuntu', font_size=10,
            x=self.width/2, y=10, anchor_x='center', anchor_y='bottom',
            color=(0, 0, 0, 255))
        self.respawnTimeLabel = pyglet.text.Label('', font_name='Ubuntu', font_size=20,
            x=self.width/2, y=self.height/4, anchor_x='center', anchor_y='center',
            color=(255, 0, 0, 255))
            
        self.sounds = Sounds()
        
        self.map = Map(maxFPS=self.maxFPS, farplane=self.farplane)
        
        self.model = Model().load('model.nsmdl')
        self.player = Player(self.model, username='local', sounds=self.sounds)
        
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
            "CP-D": key.DOWN,
            "CHAT": key.T
        }
        pyglet.resource.path = ['client/resources', 'shared/resources']
        pyglet.resource.reindex()
        self.crosshair = pyglet.sprite.Sprite(pyglet.resource.image('crosshair.png'))
        
        self.colorPicker = ColorPicker()
        
        self.cheat = False
        self.command = CommandLine(10, 50, 500, self.handleCommands)
        self.push_handlers(self.command)
        
        self.otherPlayers = {}
        self.network = Networking(self)
        self.last_network_update = 0
        self.time_network_update = 0.050
        
        self.gui = GuiManager()
    
    def start(self):
        self.map.load()
        super(NewSpades, self).start()
        self.network.stop()
    
    ###############
    # Rendering
    
    def draw2d(self):
        x, y, z = self.player.position
        yaw, pitch = self.player.orientation
        vx, vz = self.player.velocity
        self.label.text = '%02d (%.2f, %.2f, %.2f) (%.2f, %.2f) (%.2f, %.2f)' % (
            pyglet.clock.get_fps(), x, y, z, yaw, pitch, vx, vz)
        self.label.draw()
        self.crosshair.draw()
        
        self.healthLabel.text = '%d' % (self.player.health)
        self.healthLabel.draw()
        
        if self.player.respawning:
            self.deathScreen.draw()
            self.respawnTimeLabel.text = '%d' % (self.player.respawnTime+1) # +1 so it does not display 0 as respawn time for a second
            self.respawnTimeLabel.draw()
        else:
            glPushMatrix()
            glTranslatef(self.width-self.colorPicker.width, 0, 0)
            self.colorPicker.draw()
            glPopMatrix()
        
        self.command.draw()
        
        # Minimap is too buggy / ugly :(
        #glPushMatrix()
        #glTranslatef(self.width-100, self.height-100, 0)
        #self.map.drawMinimap()
        #glPopMatrix()
        
        self.gui.draw()
    
    def draw3d(self):
        if not self.player.respawning:
            self.gluLookAt(self.player.eyePosition, self.player.orientation)
            #self.gluLookAt((4, 20, 4), [135, -90])
            self.map.draw()
            self.map.drawBlockLookingAt(self.player.eyePosition, self.player.getSightVector(), self.player.armLength)
            for player in self.otherPlayers.values():
                player.draw()
    
    def gluLookAt(self, position, orientation):
        """Performs the same as gluLookAt, but it has no issues when looking up or down... (nothing was rendered then)"""
        x, y = orientation
        glRotatef(-y, 1, 0, 0)
        glRotatef(x, 0, 1, 0)
        x, y, z = position
        glTranslatef(-x, -y+0.5, -z)
    
    def onResize(self, width, height):
        self.label.y = height
        self.crosshair.x = (width-self.crosshair.width)/2
        self.crosshair.y = (height-self.crosshair.height)/2
        self.deathScreen.x = self.width/2
        self.deathScreen.y = self.height*3/4
        self.healthLabel.x = self.width/2
        self.respawnTimeLabel.x = self.width/2
        self.respawnTimeLabel.y=self.height/4
    
    def update(self, dt):
        self.map.update(self.player.position)
        if time.time() - self.last_network_update >= self.time_network_update:
            msg = self.player.getUpdateMsg()
            self.network.send(msg)
            self.last_network_update = time.time()
    
    ##############
    # Physics
    
    def updatePhysics(self, dt):
        self.player.move(dt, self.map)
        self.player.respawn(dt)
        for player in self.otherPlayers.values():
            player.move(dt, self.map)
    
    #########################
    # Client Interaction
    
    def handleMousePress(self, x, y, button, modifiers):
        if not self.player.respawning:
            block, previous = self.map.getBlocksLookingAt(self.player.eyePosition, self.player.getSightVector(), self.player.armLength)
            if button == mouse.RIGHT:
                if previous:
                    self.map.addBlock(previous, self.colorPicker.getRGB())
                    self.sounds.play("build")
            elif button == mouse.LEFT and block:
                self.map.removeBlock(block)
                self.sounds.play("build")
            elif button == mouse.MIDDLE and block:
                self.colorPicker.setRGB(self.map.world[block])
    
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
        if press and symbol == key.ESCAPE:
            if self.command.active:
                self.command.deactivate()
            elif self.fullscreen:
                self.set_fullscreen(False)
            elif self.exclusive:
                self.set_exclusive_mouse(False)
            else:
                self.close()
        if not self.command.active:
            if press:
                if symbol == self.keys["FWD"]:
                    self.player.velocity[0] += 1
                elif symbol == self.keys["BWD"]:
                    self.player.velocity[0] -= 1
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
                elif symbol == self.keys["CHAT"]:
                    self.command.activate(chr(symbol))
            
            else: #not press / release
                if symbol == self.keys["FWD"]:
                    self.player.velocity[0] = 0
                elif symbol == self.keys["BWD"]:
                    self.player.velocity[0] = 0
                elif symbol == self.keys["LEFT"]:
                    self.player.velocity[1] = 0
                elif symbol == self.keys["RIGHT"]:
                    self.player.velocity[1] = 0
                elif symbol == self.keys["CROUCH"]:
                    self.player.crouching = False
                
    def handleCommands(self, c):
        if c.startswith("/"):
            c = c[1:].strip()
            if c == "cheat":
                self.cheat = not self.cheat
            elif c.startswith("jump "):
                if self.cheat:
                    try:
                        c = int(c[5:])
                    except:
                        return
                    self.player.maxJumpCount = c
            elif c == "kill":
                self.player.damage(self.player.maxHealth*2)
            elif c.startswith("damage "):
                if self.cheat:
                    try:
                        c = int(c[7:])
                    except:
                        return
                    self.player.damage(c)
            elif c.startswith("connect "):
                c = c[8:]
                c = c.split()
                self.network.connect(c[0], c[1])
                self.network.start(c[2] if len(c)>2 else '')
            elif c.startswith('c '):
                c = c[2:]
                self.network.connect('localhost', 55555)
                self.network.start(c)
            elif c == "disconnect":
                self.network.stop()
