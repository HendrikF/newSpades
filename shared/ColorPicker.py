from pyglet.gl import *
import pyglet
import math

class ColorPicker(object):
    def __init__(self):
        self.width = 100
        self.height = 200
        
        self.cursor = 0
        self.batch = pyglet.graphics.Batch()
        self._vertexList = None
        self._colorVertexList = None
        self._cursorVertexList = None
        
        self.hue = 0
        self.saturation = 0.8
        self.value = 0.4
        
        self.initBatch()
        self.updateColor()
        self.updateCursor()
    
    def initBatch(self):
        w, h = self.width, self.height
        p = w/10
        q = (h-2*p)/6
        self._vertexList = self.batch.add(28, GL_QUADS, None, 
            ('v2f/static', [
                # Background
                0,h, 0,0, w,0, w,h, 
                # Hue
                p,h-p    , p,h-p-  q, 3*p,h-p-  q, 3*p,h-p, 
                p,h-p-  q, p,h-p-2*q, 3*p,h-p-2*q, 3*p,h-p-  q, 
                p,h-p-2*q, p,h-p-3*q, 3*p,h-p-3*q, 3*p,h-p-2*q, 
                p,h-p-3*q, p,h-p-4*q, 3*p,h-p-4*q, 3*p,h-p-3*q, 
                p,h-p-4*q, p,h-p-5*q, 3*p,h-p-5*q, 3*p,h-p-4*q, 
                p,h-p-5*q, p,p      , 3*p,p      , 3*p,h-p-5*q
            ]), 
            ('c3f/static', [
                # Background
                0.5,0.5,0.5, 0.5,0.5,0.5, 0.5,0.5,0.5, 0.5,0.5,0.5, 
                # Hue
                1,0,0, 1,1,0, 1,1,0, 1,0,0, 
                1,1,0, 0,1,0, 0,1,0, 1,1,0, 
                0,1,0, 0,1,1, 0,1,1, 0,1,0, 
                0,1,1, 0,0,1, 0,0,1, 0,1,1, 
                0,0,1, 1,0,1, 1,0,1, 0,0,1, 
                1,0,1, 1,0,0, 1,0,0, 1,0,1
            ])
        )
    
    def updateColor(self):
        w, h = self.width, self.height
        p = w/10
        
        Yhue = h-p-(h-3*p)*self.hue/360
        Ysat = 2*p+(h-3*p)*self.saturation
        Yval = 2*p+(h-3*p)*self.value
        
        Chue = self.getRGB(s=1, v=1)
        Csat = self.getRGB(v=1)
        C    = self.getRGB()
        
        if self._colorVertexList is not None:
            self._colorVertexList.delete()
        self._colorVertexList = self.batch.add(20, GL_QUADS, None, 
            ('v2f/static', [
                # Saturation
                4*p,h-p, 4*p,p, 6*p,p, 6*p,h-p, 
                # Value
                7*p,h-p, 7*p,p, 9*p,p, 9*p,h-p, 
                # H Slider
                0.6*p,Yhue, 0.6*p,Yhue-p, 3.4*p,Yhue-p, 3.4*p,Yhue, 
                # S Slider
                3.6*p,Ysat, 3.6*p,Ysat-p, 6.4*p,Ysat-p, 6.4*p,Ysat, 
                # V Slider
                6.6*p,Yval, 6.6*p,Yval-p, 9.4*p,Yval-p, 9.4*p,Yval
            ]), 
            ('c3f/static', [
                # Saturation
                Chue[0],Chue[1],Chue[2], 1,1,1, 1,1,1, Chue[0],Chue[1],Chue[2], 
                # Value
                Csat[0],Csat[1],Csat[2], 0,0,0, 0,0,0, Csat[0],Csat[1],Csat[2], 
                # H Slider
                Chue[0],Chue[1],Chue[2], Chue[0],Chue[1],Chue[2], Chue[0],Chue[1],Chue[2], Chue[0],Chue[1],Chue[2], 
                # S Slider
                Csat[0],Csat[1],Csat[2], Csat[0],Csat[1],Csat[2], Csat[0],Csat[1],Csat[2], Csat[0],Csat[1],Csat[2], 
                # V Slider
                C[0],C[1],C[2],          C[0],C[1],C[2],          C[0],C[1],C[2],          C[0],C[1],C[2]
            ])
        )
    
    def updateCursor(self):
        w, h = self.width, self.height
        p = w/10
        cur = self.cursor
        
        if self._cursorVertexList is not None:
            self._cursorVertexList.delete()
        self._cursorVertexList = self.batch.add(5, GL_LINE_STRIP, None, 
            ('v2f/static', [
                # Focus Indicator
                (0.5+cur*3)*p,h-0.5*p, (0.5+cur*3)*p,0.5*p, (3.5+cur*3)*p,0.5*p, (3.5+cur*3)*p,h-0.5*p, (0.5+cur*3)*p,h-0.5*p
            ]), 
            ('c3f/static', [
                # Focus Indicator
                1,1,1, 1,1,1, 1,1,1, 1,1,1, 1,1,1
            ])
        )
    
    def draw(self):
        glLineWidth(1)
        self.batch.draw()
    
    def input(self, x=None, y=None):
        if x is not None:
            self.cursor = (self.cursor + x) % 3
            self.updateCursor()
        if y is not None:
            if self.cursor == 0:
                self.hue -= y*6
                if self.hue < 0 or self.hue > 360:
                    self.hue = self.hue % 360
            elif self.cursor == 1:
                self.saturation += y/10
                self.saturation = min(max(0, self.saturation), 1)
            elif self.cursor == 2:
                self.value += y/10
                self.value = min(max(0, self.value), 1)
            self.updateColor()
    
    def getRGB(self, s=None, v=None):
        # https://de.wikipedia.org/wiki/HSV-Farbraum
        v = self.value      if v is None else v
        s = self.saturation if s is None else s
        if s == 0:
            return (v, v, v)
        h = math.floor(self.hue/60)
        f = self.hue/60 - h
        p = v * (1-s)
        q = v * (1-s*f)
        t = v * (1-s*(1-f))
        if h in (0,6):
            return (v, t, p)
        elif h == 1:
            return (q, v, p)
        elif h == 2:
            return (p, v, t)
        elif h == 3:
            return (p, q, v)
        elif h == 4:
            return (t, p, v)
        elif h == 5:
            return (v, p, q)
    
    def setRGB(self, color):
        # https://de.wikipedia.org/wiki/HSV-Farbraum
        r, g, b = color
        mx = max(r, g, b)
        mn = min(r, g, b)
        n = mx - mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = 60 * (    (g-b) / n)
        elif mx == g:
            h = 60 * (2 + (b-r) / n)
        elif mx == b:
            h = 60 * (4 + (r-g) / n)
        if h < 0:
            h += 360
        s = 0 if mx == 0 else n/mx
        v = mx
        self.hue = h
        self.saturation = s
        self.value = v
        self.updateColor()
