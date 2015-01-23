from pyglet.gl import *
import pyglet

class BaseWindow(pyglet.window.Window):
    def __init__(self, *args, **kw):
        super(BaseWindow, self).__init__(*args, **kw)
        self.exclusive = False
        self.maxFPS = 60
        self.farplane = 100
        self._bgColor = (0.5, 0.69, 1, 1)
        icon16 = pyglet.image.load('shared/resources/icon16.png')
        icon32 = pyglet.image.load('shared/resources/icon32.png')
        icon64 = pyglet.image.load('shared/resources/icon64.png')
        self.set_icon(icon16, icon32, icon64)
    
    def start(self):
        glClearColor(self._bgColor[0], self._bgColor[1], self._bgColor[2], self._bgColor[3])
        glEnable(GL_CULL_FACE)
        glEnable(GL_FOG)
        glFogfv(GL_FOG_COLOR, (GLfloat * 4)(*self._bgColor))
        glHint(GL_FOG_HINT, GL_DONT_CARE)
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_START, self.farplane/4)
        glFogf(GL_FOG_END, self.farplane)
        pyglet.clock.schedule_interval(self._update, 1 / self.maxFPS)
        pyglet.app.run()
    
    def set_exclusive_mouse(self, exclusive):
        super(BaseWindow, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive
    
    def _update(self, dt):
        self.update(dt)
        m = 10
        dt = min(dt, 0.2)
        for _ in range(m):
            self.updatePhysics(dt / m)
    
    def on_mouse_press(self, x, y, button, modifiers):
        if self.exclusive:
            self.handleMousePress(x, y, button, modifiers)
        else:
            self.set_exclusive_mouse(True)
    
    def on_mouse_motion(self, x, y, dx, dy):
        if self.exclusive:
            self.handleMouseMove(dx, dy)
    
    def on_key_press(self, symbol, modifiers):
        self.handleKeyboard(symbol, modifiers, True)
    
    def on_key_release(self, symbol, modifiers):
        self.handleKeyboard(symbol, modifiers, False)
    
    def set2d(self):
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    def set3d(self):
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, width / height, 0.1, self.farplane)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    def on_draw(self):
        self.clear()
        self.set3d()
        self.draw3d()
        self.set2d()
        self.draw2d()
    
    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        self.onResize(width, height)
    
    @property
    def bgColor(self):
        return self._bgColor
    @bgColor.setter
    def bgColor(self, c):
        self._bgColor = c
        glClearColor(self._bgColor[0], self._bgColor[1], self._bgColor[2], self._bgColor[3])
        glFogfv(GL_FOG_COLOR, (GLfloat * 4)(*self._bgColor))
    
    def draw2d(self):
        pass
    
    def draw3d(self):
        pass
    
    def update(self, dt):
        pass
    
    def updatePhysics(self, dt):
        pass
    
    def handleMousePress(self, x, y, button, modifiers):
        pass
    
    def handleMouseMove(self, dx, dy):
        pass
    
    def handleKeyboard(self, symbol, modifiers, press):
        pass
    
    def onResize(self, width, height):
        pass
