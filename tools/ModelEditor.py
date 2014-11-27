from shared.BaseWindow import BaseWindow
from pyglet.gl import *
from pyglet.window import key, mouse
import math
from shared.Model import Model
from shared.ColorPicker import ColorPicker

import logging
logger = logging.getLogger(__name__)

class ModelEditor(BaseWindow):
    ##################
    # General stuff
    def __init__(self, *args, **kw):
        super(ModelEditor, self).__init__(*args, **kw)
        self.fpsLabel = pyglet.text.Label('', font_name='Ubuntu', font_size=10,
            x=0, y=0, anchor_x='left', anchor_y='top',
            color=(0, 0, 0, 255))
        self.helpLabel = pyglet.text.Label('Press H for help', font_name='Ubuntu', font_size=10,
            x=0, y=0, anchor_x='left', anchor_y='bottom',
            color=(200, 0, 0, 255))
        self.helpText = pyglet.text.HTMLLabel('<h1>Model Editor - NewSpades</h1><h2>Keys</h2><p>WASD: Move<br>Left Shift: Move Down<br>Space: Move Up<br>Arrows: Select Color<br>F11: Toggle Fullscreen<br>ESC: Release mouse/Exit Fullscreen/Quit Editor<br>H: Toggle this help text</p>', x=50, width=800, multiline=True, anchor_y='top')
        self.helpText.font_name = 'Ubuntu'
        self.keys = {
            "FWD": key.W,
            "BWD": key.S,
            "LEFT": key.A,
            "RIGHT": key.D,
            "UP": key.SPACE,
            "DOWN": key.LSHIFT,
            "FULLSCREEN": key.F11,
            "CP-R": key.RIGHT,
            "CP-L": key.LEFT,
            "CP-U": key.UP,
            "CP-D": key.DOWN
        }
        pyglet.resource.path = ['shared/resources']
        pyglet.resource.reindex()
        self.crosshair = pyglet.sprite.Sprite(pyglet.resource.image('crosshair.png'))
        self.farplane = 600
        self.displayHelp = False
        
        self.velocity = [0, 0]
        self.dy = 0
        self.position = (0, 4, 0)
        self.orientation = [90, 0]
        self.armLength = 100
        
        self.model = Model()
        self.model.addBlock((0,0,0), (0,0,0))
        
        self.colorPicker = ColorPicker()
    
    def start(self):
        #self.model.load('model.nsmdl')
        super(ModelEditor, self).start()
    
    ###############
    # Rendering
    
    def draw2d(self):
        x, y, z = self.position
        self.fpsLabel.text = '%02d (%.2f, %.2f, %.2f)' % (
            pyglet.clock.get_fps(), x, y, z)
        
        glPushMatrix()
        glTranslatef(0, self.height, 0)
        self.fpsLabel.draw()
        if self.displayHelp:
            self.helpText.draw()
        glPopMatrix()
        
        self.crosshair.draw()
        
        glPushMatrix()
        glTranslatef(self.width-self.colorPicker.width, 0, 0)
        self.colorPicker.draw()
        glPopMatrix()
        
        self.helpLabel.draw()
    
    def draw3d(self):
        x, y, z = self.position
        dx, dy, dz = self.getSightVector()
        gluLookAt(
            x,      y,      z,     # the -0.5 are for the same fix as Player.eyeHeight
            x+dx,   y+dy,   z+dz,  #
            0,      1,          0
        )
        glLineWidth(3)
        glBegin(GL_LINES)
        glColor3f(0.8,0,0)
        glVertex3f(-1, 0, 0)
        glVertex3f( 1000, 0, 0)
        glEnd()
        glBegin(GL_LINES)
        glColor3f(0,0.8,0)
        glVertex3f(0, -1, 0)
        glVertex3f(0,  1000, 0)
        glEnd()
        glBegin(GL_LINES)
        glColor3f(0,0,0.8)
        glVertex3f(0, 0, -1)
        glVertex3f(0, 0,  1000)
        glEnd()
        self.model.draw()
    
    def onResize(self, width, height):
        self.crosshair.x = (width-self.crosshair.width)/2
        self.crosshair.y = (height-self.crosshair.height)/2
    
    def update(self, dt):
        speed = 10
        d = speed*dt
        x, y, z = self.position
        dx, dz = self.getMotionVector()
        dy = self.dy
        self.position = x+dx*d, y+dy*d, z+dz*d
    
    ##############
    # Physics
    
    def updatePhysics(self, dt):
        pass
    
    #########################
    # Client Interaction
    
    def handleMousePress(self, x, y, button, modifiers):
        block, previous = self.getBlocksLookingAt(self.position, self.getSightVector(), self.armLength)
        if button == mouse.RIGHT:
            if previous:
                self.model.addBlock(previous, self.colorPicker.getRGB())
        elif button == mouse.LEFT and block and self.model.size > 1:
            self.model.removeBlock(block)
    
    def handleMouseMove(self, dx, dy):
        m = 0.1
        self.orientation[0] += dx * m
        self.orientation[1] += dy * m
        if self.orientation[0] < 0:
            self.orientation[0] += 360
        elif self.orientation[0] >= 360:
            self.orientation[0] -= 360
        if self.orientation[1] < -90:
            self.orientation[1] = -90
        elif self.orientation[1] > 90:
            self.orientation[1] = 90
    
    def handleKeyboard(self, symbol, modifiers, press):
        if press:
            if symbol == key.ESCAPE:
                self.set_fullscreen(False)
                if self.exclusive:
                    self.set_exclusive_mouse(False)
                else:
                    self.close()
            elif symbol == key.H:
                self.displayHelp = not self.displayHelp
            elif symbol == self.keys["FWD"]:
                self.velocity[0] -= 1
            elif symbol == self.keys["BWD"]:
                self.velocity[0] += 1
            elif symbol == self.keys["LEFT"]:
                self.velocity[1] -= 1
            elif symbol == self.keys["RIGHT"]:
                self.velocity[1] += 1
            elif symbol == self.keys["UP"]:
                self.dy += 1
            elif symbol == self.keys["DOWN"]:
                self.dy -= 1
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
            
            #if symbol == key.S and modifiers&key.MOD_CTRL:
            #    self.model.save('model.nsmdl')
        
        else: #not press / release
            if symbol == self.keys["FWD"]:
                self.velocity[0] += 1
            elif symbol == self.keys["BWD"]:
                self.velocity[0] -= 1
            elif symbol == self.keys["LEFT"]:
                self.velocity[1] += 1
            elif symbol == self.keys["RIGHT"]:
                self.velocity[1] -= 1
            elif symbol == self.keys["UP"]:
                self.dy -= 1
            elif symbol == self.keys["DOWN"]:
                self.dy += 1
    
    ###################
    # Stuff
    
    def getSightVector(self):
        x, y = self.orientation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return (dx, dy, dz)
    
    def getMotionVector(self):
        if any(self.velocity):
            x = self.orientation[0]
            x_angle = math.radians(x + math.degrees(math.atan2(self.velocity[0], self.velocity[1])))
            dx = math.cos(x_angle)
            dz = math.sin(x_angle)
        else:
            return (0, 0)
        return (dx, dz)
    
    def getBlocksLookingAt(self, position, vector, maxDistance):
        """Returns which blocks the player is looking at"""
        m = 100
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in range(maxDistance * m):
            key = (round(x), round(y), round(z))
            if key != previous and self.model.contains(key):
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None
