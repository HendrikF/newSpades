from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame
from Vector import *

class Renderer(object):
    def __init__(self, ns):
        self.ns = ns
        self.farplane = 150
        self.background = [0.5, 0.5, 0.75, 0]
    
    def start(self):
        self.map = self.ns.map
        self.player = self.ns.player
        
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
        #glEnable(GL_FOG)
        #glFogfv(GL_FOG_COLOR, (1, 1, 1, 0.9))
        #glFogf(GL_FOG_MODE, GL_LINEAR)
        #glFogf(GL_FOG_START, 20)
        #glFogf(GL_FOG_END, 25)
        
        #glEnable(GL_LIGHTING)
        #glEnable(GL_COLOR_MATERIAL)
        #glEnable(GL_LIGHT0)
        #glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1))
        #glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
        #glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
        #glLightfv(GL_LIGHT0, GL_POSITION, (0.0, 10.0, 0.0))
    
    def reset(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(*self.background)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluPerspective(45, 1, 1, self.farplane)
        
        orientation = self.player.getVectorFromOrientation(Vector(1, 0, 0))
        position = self.player.position
        lookat = position + orientation
        if self.player.crouching:
            position -= Vector(0, 0, 1)
        up = self.player.getVectorFromOrientation(Vector(0, 0, 1))
        gluLookAt(
            *(lookat.getList() + position.getList() + up.getList())
        )
    
    def render(self):
        self.reset()
        
        self.renderMap()
    
    def renderMap(self):
        for face, color in self.map.getFaces():
            glColor(color)
            self.renderQuadrat(*face)
    
    def renderQuadrat(self, p1, p2, p3, p4):
        glBegin(GL_QUADS)
        glVertex(*p1)
        glVertex(*p2)
        glVertex(*p3)
        glVertex(*p4)
        glEnd()
