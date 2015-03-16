import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
from shared.BaseWindow import BaseWindow
from client.ControllablePlayer import ControllablePlayer
from client.DrawablePlayer import DrawablePlayer
from client.ClientMap import ClientMap
from client.Sounds import Sounds
from shared.Model import Model
from shared.CommandLine import CommandLine
from shared.ColorPicker import ColorPicker
from client.GuiManager import GuiManager
from transmitter.general import Client
from shared import Messages
import math
import time

import logging
logger = logging.getLogger(__name__)

class NewSpades(BaseWindow):
    ##################
    # General stuff
    def __init__(self, progressbar=None, *args, **kw):
        super(NewSpades, self).__init__(*args, **kw)
        self.label = pyglet.text.Label('', font_name='Ubuntu', font_size=10,
            x=10, y=self.height, anchor_x='left', anchor_y='top',
            color=(0, 0, 0, 255))
        
        self.otherPlayers = {}
        
        self._client = Client()
        Messages.registerMessages(self._client.messageFactory)
        self._client.onMessage.attach(self.onMessage)
        self._client.onDisconnect.attach(self.onDisconnect)
        
        self.sounds = Sounds()
        
        self.map = ClientMap(maxFPS=self.maxFPS, farplane=self.farplane)
        
        self.model = {
            'head': Model(offset=(0, 22, 0.5)).load('client/models/head.nsmdl', progressbar=progressbar),
            'torso': Model(offset=(0, 12, 0)).load('client/models/torso.nsmdl', progressbar=progressbar),
            'arms': Model(offset=(0, 21, 0)).load('client/models/arms.nsmdl', progressbar=progressbar),
            'legl': Model(offset=(1, 12,-3)).load('client/models/leg.nsmdl', progressbar=progressbar),
            'legr': Model(offset=(1, 12, 3)).load('client/models/leg.nsmdl', progressbar=progressbar),
            'tool': Model(scale2=0.6, offset=(0, 21, 5), offset2=(9, -1, 0)).load('client/models/rifle.nsmdl', progressbar=progressbar)
        }
        self.player = ControllablePlayer(self._client, self.model, self.sounds, username='local')
        
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
        self.command = CommandLine(10, 50, self.width*0.9, self.handleCommands)
        
        self.gui = GuiManager(self)
    
    def start(self):
        self.map.load()
        super(NewSpades, self).start()
        self._client.stop()
    
    ###############
    # Rendering
    
    def draw2d(self):
        x, y, z = self.player.position
        yaw, pitch = self.player.yaw, self.player.pitch
        vx, vz = self.player.dx, self.player.dz
        self.label.text = '%02d (%.2f, %.2f, %.2f) (%.2f, %.2f) (%.2f, %.2f)' % (
            pyglet.clock.get_fps(), x, y, z, yaw, pitch, vx, vz)
        self.label.draw()
        self.crosshair.draw()
        
        glPushMatrix()
        glTranslatef(self.width-self.colorPicker.width, 0, 0)
        self.colorPicker.draw()
        glPopMatrix()
        
        if self.command.active:
            self.command.draw()
        
        # Minimap is too buggy / ugly :(
        #glPushMatrix()
        #glTranslatef(self.width-100, self.height-100, 0)
        #self.map.drawMinimap()
        #glPopMatrix()
        
        self.gui.draw()
    
    def draw3d(self):
        self.gluLookAt(self.player.eyePosition, (self.player.yaw, self.player.pitch))
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
    
    ##############
    # Physics
    
    def update(self, dt):
        self._client.update()
        self.map.update(self.player.position)
    
    def updatePhysics(self, dt):
        self.player.update(dt, self.map)
        for player in self.otherPlayers.values():
            player.update(dt, self.map)
    
    #########################
    # Client Interaction
    
    def handleMousePress(self, x, y, button, modifiers):
        if self.command.active:
            return self.command.on_mouse_press(x, y, button, modifiers)
        block, previous = self.map.getBlocksLookingAt(self.player.eyePosition, self.player.getSightVector(), self.player.armLength)
        if button == mouse.RIGHT and previous:
            color = self.colorPicker.getRGB()
            self.map.addBlock(previous, color)
            msg = Messages.BlockBuildMsg()
            msg.x, msg.y, msg.z = previous
            msg.r, msg.g, msg.b = color
            self._client.send(msg)
        elif button == mouse.LEFT and block:
            self.map.removeBlock(block)
            msg = Messages.BlockBreakMsg()
            msg.x, msg.y, msg.z = block
            self._client.send(msg)
        elif button == mouse.MIDDLE and block:
            self.colorPicker.setRGB(self.map.world[block])
    
    def handleMouseMove(self, dx, dy):
        m = 0.1
        self.player.yaw += dx * m
        self.player.pitch += dy * m
    
    def handleMouseScroll(self, x, y, dx, dy):
        print('Scroll {} {}'.format(dx, dy))
        if self.command.active:
            self.command.on_mouse_scroll(x, y, dx, dy)
    
    def handleKeyboard(self, symbol, modifiers, press):
        if press and symbol == key.ESCAPE:
            if self.command.active:
                self.command.active = False
            elif self.fullscreen:
                self.set_fullscreen(False)
            elif self.exclusive:
                self.set_exclusive_mouse(False)
            else:
                self.close()
        if self.command.active:
            return
        if press:
            if symbol == self.keys["FWD"]:
                self.player.dx += 1
            elif symbol == self.keys["BWD"]:
                self.player.dx -= 1
            elif symbol == self.keys["LEFT"]:
                self.player.dz -= 1
            elif symbol == self.keys["RIGHT"]:
                self.player.dz += 1
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
                self.player.dx = 0
            elif symbol == self.keys["BWD"]:
                self.player.dx = 0
            elif symbol == self.keys["LEFT"]:
                self.player.dz = 0
            elif symbol == self.keys["RIGHT"]:
                self.player.dz = 0
            elif symbol == self.keys["CROUCH"]:
                self.player.crouching = False
    
    def handleText(self, text):
        if self.command.active:
            self.command.on_text(text)
        else:
            if text == chr(self.keys["CHAT"]):
                self.command.active = True
    
    def handleTextMotion(self, motion, select):
        if self.command.active:
            self.command.on_text_motion(motion, select)
    
    def handleTextMotionSelect(self, motion):
        if self.command.active:
            self.command.on_text_motion_select(motion)
    
    def handleMouseDrag(self, x, y, dx, dy, buttons, modifiers):
        if self.command.active:
            self.command.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
                
    def handleCommands(self, c):
        if c.startswith("/"):
            c = c[1:].strip()
            if c.startswith("connect "):
                c = c[8:]
                c = c.split()
                self.connect(c[0], int(c[1]), username=(c[2] if len(c)>2 else ''))
            elif c.startswith('c '):
                c = c[2:]
                self.connect('localhost', 55555, username=c)
    
    #########################
    # Networking
    
    def onMessage(self, msg, peer):
        logger.debug('Received Message from peer %s: %s', peer, msg)
        if self._client.messageFactory.is_a(msg, 'JoinMsg'):
            if msg.username not in self.otherPlayers:
                self.otherPlayers[msg.username] = DrawablePlayer(self.model, self.sounds, username=msg.username)
            else:
                logger.warning('Received JoinMsg for existent Player! %s %s', peer, msg)
        elif self._client.messageFactory.is_a(msg, 'LeaveMsg'):
            self.otherPlayers.pop(msg.username)
        elif self._client.messageFactory.is_a(msg, 'Update'):
            if msg.username == self.player.username:
                player = self.player
            else:
                try:
                    player = self.otherPlayers[msg.username]
                except KeyError:
                    logger.warning('Update with unknown username from peer %s: %s', peer, msg)
                    return
            player.applyUpdate(msg.key, msg.value)
        elif self._client.messageFactory.is_a(msg, 'CompleteUpdate'):
            if msg.username == self.player.username:
                player = self.player
            else:
                try:
                    player = self.otherPlayers[msg.username]
                except KeyError:
                    logger.warning('CompleteUpdate with unknown username from peer %s: %s', peer, msg)
                    return
            player.updateFromMsg(msg)
        elif self._client.messageFactory.is_a(msg, 'BlockBuildMsg'):
            self.map.addBlock((msg.x, msg.y, msg.z), (msg.r, msg.g, msg.b))
        elif self._client.messageFactory.is_a(msg, 'BlockBreakMsg'):
            self.map.removeBlock((msg.x, msg.y, msg.z))
        else:
            logger.warning('Unknown Message from peer %s: %s', peer, msg)
    
    def onDisconnect(self, peer):
        logger.info('Disconnected from server!')
        self.gui.update(-1, text="{.align 'center'}{color (255,0,0,255)}{bold True}We're disconnected!", x=0.5, y=0.5, anchor_x=self.gui.CENTER, anchor_y=self.gui.CENTER)
    
    def connect(self, host, port, username=''):
        self._client.connect(host, port)
        self._client.start()
        self.player.username = username
        self._client.send(Messages.JoinMsg(username=username))
