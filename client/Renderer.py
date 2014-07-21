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
        lookat = self.player.position + orientation
        position = self.player.position
        if self.player.crouching:
            lookat -= Vector(0, 0, 1)
            position -= Vector(0, 0, 1)
        up = self.player.getVectorFromOrientation(Vector(0, 0, 1))
        gluLookAt(
            *(lookat.getList() + position.getList() + up.getList())
        )
    
    def render(self):
        self.reset()
        
        self.renderMap()
    
    def renderMap(self):
        for x, y, z, color in self.map.getBlocks():
            glColor(*color)
            self.renderQuader(x, y, z)
    
    def renderQuader(self, x, y, z):
        edges = self.getEdges(x, y, z)
        self.renderQuadrat(edges[1], edges[5], edges[8], edges[4])
        self.renderQuadrat(edges[2], edges[6], edges[5], edges[1])
        self.renderQuadrat(edges[3], edges[7], edges[6], edges[2])
        self.renderQuadrat(edges[4], edges[8], edges[7], edges[3])
        self.renderQuadrat(edges[1], edges[2], edges[3], edges[4])
        self.renderQuadrat(edges[5], edges[6], edges[7], edges[8])
    
    def getEdges(self, x, y, z):
        return [
            None,
            (x-0.5, y+0.5, z),
            (x+0.5, y+0.5, z),
            (x+0.5, y-0.5, z),
            (x-0.5, y-0.5, z),
            (x-0.5, y+0.5, z-1),
            (x+0.5, y+0.5, z-1),
            (x+0.5, y-0.5, z-1),
            (x-0.5, y-0.5, z-1)
        ]
    
    def renderQuadrat(self, p1, p2, p3, p4):
        glBegin(GL_QUADS)
        glVertex3f(*p1)
        glVertex3f(*p2)
        glVertex3f(*p3)
        glVertex3f(*p4)
        glEnd()
