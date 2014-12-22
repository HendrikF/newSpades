from pyglet.text.layout import TextLayout
from pyglet.text.document import FormattedDocument
from pyglet.text import decode_attributed
from pyglet.graphics import Batch

class GuiManager(object):
    def __init__(self):
        self.batch = Batch()
        self.labels = {}
    
    def _add(self, _id, **kw):
        self.labels[_id] = Label(self.batch, **kw)
    
    def update(self, _id, **kw):
        if _id in self.labels:
            self.labels[_id].update(**kw)
        else:
            self._add(_id, **kw)
    
    def delete(self, _id):
        if _id in self.labels:
            self.labels.pop(_id).delete()
    
    def draw(self):
        self.batch.draw()
    
class Label(object):
    def __init__(self, batch, **kw):
        self.layout = TextLayout(FormattedDocument(), multiline=True, batch=batch)
        self.update(**kw)
    
    def update(self, text=None, x=None, y=None, anchor_x=None, anchor_y=None):
        if text is not None:
            self.layout.document = decode_attributed(attributedText)
        if x is not None:
            self.layout.x = x
        if y is not None:
            self.layout.y = y
        if anchor_x is not None:
            self.layout.anchor_x = anchor_x
        if anchor_y is not None:
            self.layout.anchor_y = anchor_y
    
    def delete(self):
        self.layout.delete()