from pyglet.text.layout import TextLayout
from pyglet.text.document import FormattedDocument
from pyglet.text import decode_attributed
from pyglet.graphics import Batch

class GuiManager(object):
    LEFT    = 'left'
    RIGHT   = 'right'
    CENTER  = 'center'
    TOP     = 'top'
    BASELINE= 'baseline'
    BOTTOM  = 'bottom'
    
    def __init__(self, window):
        self.window = window
        self.batch = Batch()
        self.labels = {}
    
    def update(self, _id, **kw):
        if _id in self.labels:
            self.labels[_id].update(**kw)
        else:
            self.labels[_id] = Label(self, **kw)
    
    def delete(self, _id):
        if _id in self.labels:
            self.labels.pop(_id).delete()
    
    def draw(self):
        self.batch.draw()

class Label(object):
    def __init__(self, gui, **kw):
        self.gui = gui
        self.layout = TextLayout(FormattedDocument(), multiline=True, width=600, batch=self.gui.batch)
        self.update(**kw)
    
    def update(self, text=None, x=None, y=None, anchor_x=None, anchor_y=None):
        """x and y range from 0 to 1 (part of width or height)"""
        if text is not None:
            self.layout.document = decode_attributed(text)
        if x is not None:
            self.layout.x = x * self.gui.window.width
        if y is not None:
            self.layout.y = y * self.gui.window.height
        if anchor_x is not None:
            self.layout.anchor_x = anchor_x
        if anchor_y is not None:
            self.layout.anchor_y = anchor_y
    
    def delete(self):
        self.layout.delete()
