import pyglet
from pyglet.gl import *

class CommandLine(object):
    def __init__(self, x, y, width, callback):
        self.document = pyglet.text.document.UnformattedDocument()
        font = self.document.get_font()
        height = font.ascent - font.descent
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self.batch = pyglet.graphics.Batch()
        self.document.push_handlers(self.on_insert_text)
        self.document.set_style(0, 0, dict(font_name='Ubuntu'))
        self.layout = pyglet.text.layout.IncrementalTextLayout(self.document, width, height, batch=self.batch)
        self.layout.x = x
        self.layout.y = y
        self.caret = pyglet.text.caret.Caret(self.layout, batch=self.batch)
        self.active = False
        self.callback = callback
        # when cmdLine is opened, a key is pressed and will reach us, so we have to ignore this once
        self.charToIgnore = ''
        self.boxPadding = 3
        self.boxVertexList = None
        self.updateBox()
    
    def on_insert_text(self, start, text):
        if len(text) != 1:
            return
        if ord(text) == 10: # Enter
            content = self.document.text.replace(chr(10), '')
            if len(content) > 0:
                self.callback(content)
            self.clear()
            self.deactivate()
    
    def clear(self):
        self.document.text = ''
    
    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, v):
        self._x = v
        self.layout.x = v
        self.updateBox()
    
    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, v):
        self._y = v
        self.layout.y = v
        self.updateBox()
    
    @property
    def width(self):
        return self._width
    @width.setter
    def width(self, v):
        self._width = v
        self.layout.width = v
        self.updateBox()
    
    @property
    def height(self):
        return self._heigth
    @height.setter
    def height(self, v):
        self._height = v
        self.layout.height = v
        self.updateBox()
    
    @property
    def text(self):
        return self.document.text
    
    def draw(self):
        if self.active:
            self.batch.draw()
    
    def updateBox(self):
        if self.boxVertexList != None:
            self.boxVertexList.delete()
        x, y, w, h = self._x, self._y, self._width, self._height
        x, y, w, h = x-self.boxPadding, y-self.boxPadding, w+2*self.boxPadding, h+2*self.boxPadding
        self.boxVertexList = self.batch.add(5, GL_LINE_STRIP, None, 
            ('v2f/static', [x,y, x+w,y, x+w,y+h, x,y+h, x,y]), 
            ('c3f/static', [0,0,0, 0,0,0, 0,0,0, 0,0,0, 0,0,0])
        )
    
    def activate(self, charToIgnore=''):
        self.active = True
        self.charToIgnore = charToIgnore
    
    def deactivate(self):
        self.active = False
    
    def on_text(self, text):
        if self.active:
            if text == self.charToIgnore:
                self.charToIgnore = ''
            else:
                self.caret.on_text(text)
    
    def on_text_motion(self, motion, select=False):
        if self.active:
            self.caret.on_text_motion(motion, select)
    
    def on_text_motion_select(self, motion):
        if self.active:
            self.caret.on_text_motion_select(motion)
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.active:
            self.caret.on_mouse_scroll(x, y, scroll_x, scroll_y)
    
    def on_mouse_press(self, x, y, button, modifiers):
        if self.active:
            self.caret.on_mouse_press(x, y, button, modifiers)
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.active:
            self.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
    
    """def on_activate(self):
        if self.active:
            self.caret.on_activate()
    
    def on_deactivate(self):
        if self.active:
            self.caret.on_deactivate()"""
