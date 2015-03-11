import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
import math
import os, sys
from shared.BaseWindow import BaseWindow
from shared.Model import Model
from shared.ColorPicker import ColorPicker
from shared.CommandLine import CommandLine

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
        self.helpText = pyglet.text.HTMLLabel("""
            <h1>Model Editor - NewSpades</h1>
                <h2>Loading of files</h2>
                    <p>Give the filename as the first command line option</p>
                <h2>Keys</h2>
                    <p>WASD: Move
                    <br>Left Shift: Move Down
                    <br>Space: Move Up
                    <br>Arrows: Select Color
                    <br>F11: Toggle Fullscreen
                    <br>ESC: Release mouse/Exit Fullscreen/Quit Editor
                    <br>T: Turn Command line on
                    <br>C: Output selected color to command line (in 0..1 and 0..255 range)
                    <br>H: Toggle this help text</p>
                <h2>Command line commands</h2>
                    <p>/save &lt;modelname&gt; (Always overwrites existing files)
                    <br>/color 255 255 255 (Sets colorpicker to this color)
                    <br>/replace 255 255 255 (Replaces selected color with this color)</p>
            """, x=50, width=self.width-100, y=-20, multiline=True, anchor_y='top')
        self.helpText.font_name = 'Ubuntu'
        self.keys = {
            'FWD': key.W,
            'BWD': key.S,
            'LEFT': key.A,
            'RIGHT': key.D,
            'UP': key.SPACE,
            'DOWN': key.LSHIFT,
            'FULLSCREEN': key.F11,
            'CP-R': key.RIGHT,
            'CP-L': key.LEFT,
            'CP-U': key.UP,
            'CP-D': key.DOWN,
            'CHAT': key.T
        }
        pyglet.resource.path = ['shared/resources']
        pyglet.resource.reindex()
        self.crosshair = pyglet.sprite.Sprite(pyglet.resource.image('crosshair.png'))
        pyglet.resource.add_font('Ubuntu-R.ttf')
        self.farplane = 600
        self.displayHelp = False
        
        self.velocity = [0, 0]
        self.dy = 0
        self.position = (0, 4, 0)
        self.orientation = [90, 0]
        self.armLength = 100
        
        self.model = Model(scale=1)
        self.model.addBlock((0,0,0), (0,0,0))
        
        self.colorPicker = ColorPicker()
        self.command = CommandLine(10, 50, self.width*0.9, self.handleCommands)
    
    def start(self):
        if len(sys.argv) > 1:
            fn = sys.argv[1]
            self.model.load(fn)
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
        
        if self.command.active:
            self.command.draw()
    
    def draw3d(self):
        self.gluLookAt(self.position, self.orientation)
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
    
    def gluLookAt(self, position, orientation):
        """Performs the same as gluLookAt, but it has no issues when looking up or down... (nothing was rendered then)"""
        # Haven't really thought about what this actually does :)
        x, y = orientation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = position
        glTranslatef(-x, -y, -z)
    
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
        if self.command.active:
            return self.command.on_mouse_press(x, y, button, modifiers)
        block, previous = self.getBlocksLookingAt(self.position, self.getSightVector(), self.armLength)
        if button == mouse.RIGHT:
            if previous:
                self.model.addBlock(previous, self.colorPicker.getRGB())
        elif button == mouse.LEFT and block and self.model.size > 1:
            self.model.removeBlock(block)
        elif button == mouse.MIDDLE and block:
            self.colorPicker.setRGB(self.model.blocks[block])
    
    def handleMouseScroll(self, x, y, dx, dy):
        if self.command.active:
            self.command.on_mouse_scroll(x, y, dx, dy)
    
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
            return True
        if press:
            if symbol == key.H:
                self.displayHelp = not self.displayHelp
            elif symbol == key.C:
                c = self.colorPicker.getRGB()
                print('(R, G, B):', c)
                print('(R, G, B):', (c[0]*255, c[1]*255, c[2]*255))
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
    
    def handleCommands(self, text):
        if text.startswith('/save'):
            text = text[5:].strip()
            text = text+'.nsmdl'
            try:
                os.remove(text)
                self.helpLabel.text = 'overwriting '+text
            except OSError:
                pass
            self.model.save(text)
        elif text.startswith('/color'):
            r, g, b = text[6:].strip().split()
            text = (int(r)/255, int(g)/255, int(b)/255)
            self.colorPicker.setRGB(text)
        elif text.startswith('/replace'):
            try:
                r, g, b = text[8:].strip().split()
                targetColor = (int(r)/255, int(g)/255, int(b)/255)
            except Exception as e:
                print('Cant replace color:', e)
            else:
                oldColor = self.colorPicker.getRGB()
                d = 1/255
                for pos, col in self.model.blocks.items():
                    if (abs(col[0]-oldColor[0]) < d and
                            abs(col[1]-oldColor[1]) < d and
                            abs(col[2]-oldColor[2]) < d):
                        self.model.removeBlock(pos, cn=False)
                        self.model.addBlock(pos, targetColor, cn=False)
    
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
