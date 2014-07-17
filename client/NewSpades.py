import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from math import sin, cos, radians
from random import randrange
from Player import *
from Vector import *

class NewSpades(object):
    def __init__(self):
        self.fullscreen = False
        self.screen = (1000, 750)
        self.title = "NewSpades"
        self.max_fps = 60   
        self.farplane = 150
        
        self.background = [0.5, 0.5, 0.75, 0]
        
        self.running = True
        
        self.clock = pygame.time.Clock()
        
        self.player = Player("_debuguser_")
        
        self.map = []
    
    def start(self):
        options = pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE
        if self.fullscreen:
            options |= pygame.FULLSCREEN
        pygame.init()
        self.display = pygame.display.set_mode(self.screen, options, 16)
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        pygame.key.set_repeat(3, 40)
        
        self.generateMap()
        
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
        
        self.loop()
    
    # DEBUG
    def generateMap(self):
        self.map = []
        for x in range(5):
            self.map.append([])
            for y in range(7):
                self.map[x].append([])
                for z in range(6-y):
                    self.map[x][y].append((z <= 6-y))
    
    def loop(self):
        while self.running == True:
            self.clock.tick(self.max_fps)
            pygame.display.set_caption("{} - FPS: {:.1f}".format(self.title, self.clock.get_fps()))
            self.handleEvents()
            self.update()
            self.render()
    
    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handleKeyboard(event)
            elif event.type == pygame.MOUSEMOTION:
                self.handleMouse(event)
    
    def handleKeyboard(self, event):
        if event.key == pygame.K_ESCAPE:
            self.running = False
        
        elif event.key == pygame.K_a:
            self.player.position[0] += self.player.velocity[0]
        elif event.key == pygame.K_d:
            self.player.position[0] -= self.player.velocity[0]
        
        elif event.key == pygame.K_w:
            self.player.position[1] -= self.player.velocity[1]
        elif event.key == pygame.K_s:
            self.player.position[1] += self.player.velocity[1]
        
        elif event.key == pygame.K_q:
            self.player.position[2] -= self.player.velocity[2]
        elif event.key == pygame.K_e:
            self.player.position[2] += self.player.velocity[2]
    
    def handleMouse(self, event):
        # When Game starts
        if event.pos == event.rel:
            return
        
        yaw = event.rel[0]/10
        pitch = -event.rel[1]/10
        
        self.player.orientation[0] += yaw
        self.player.orientation[1] += pitch
        if self.player.orientation[0] < 0:
            self.player.orientation[0] += 360
        elif self.player.orientation[0] >= 360:
            self.player.orientation[0] -= 360
        if self.player.orientation[1] < -90:
            self.player.orientation[1] = -90
        elif self.player.orientation[1] > 90:
            self.player.orientation[1] = 90
    
    def update(self):
        pass
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(*self.background)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluPerspective(45, 1, 1, self.farplane)
        """gluLookAt(
            sin(radians(self.player.orientation[0])), 
            sin(radians(self.player.orientation[1])), 
            cos(radians(self.player.orientation[0]))*cos(radians(self.player.orientation[1])), 
            0, 0, 0, 
            0, 1, 0)"""
        orientation = self.player.getVectorFromOrientation(Vector(1, 0, 0))
        orientation.z *= -1
        lookat = self.player.position + orientation
        up = self.player.getVectorFromOrientation(Vector(0, 0, 1))
        gluLookAt(
            lookat[0], lookat[1], lookat[2], 
            self.player.position[0], self.player.position[1], self.player.position[2], 
            up[0], up[1], up[2]
        )
        
        glPushMatrix()
        #glTranslatef(-self.player.position[0], -self.player.position[1], -self.player.position[2])
        
        glColor(0, 0, 1)
        self.renderQuadrat((0,0,-1), (0,20,-1), (20,20,-1), (20,0,-1))
        
        self.renderMap()
        
        glPopMatrix()
        
        pygame.display.flip()
    
    def renderMap(self):
        glColor(0, 1, 0)
        # x  - Counter
        # x_ - Value
        for x, x_ in enumerate(self.map):
            for y, y_ in enumerate(x_):
                for z, z_ in enumerate(y_):
                    if z_ != True:
                        continue
                    self.renderQuader(x, y, z)
    
    def renderQuader(self, x, y, z):
        def getEdges(x, y, z):
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
        edges = getEdges(x, y, z)
        self.renderQuadrat(edges[1], edges[5], edges[8], edges[4])
        self.renderQuadrat(edges[2], edges[6], edges[5], edges[1])
        self.renderQuadrat(edges[3], edges[7], edges[6], edges[2])
        self.renderQuadrat(edges[4], edges[8], edges[7], edges[3])
        self.renderQuadrat(edges[1], edges[2], edges[3], edges[4])
        self.renderQuadrat(edges[5], edges[6], edges[7], edges[8])
    
    def renderQuadrat(self, p1, p2, p3, p4):
        glBegin(GL_QUADS)
        glVertex3f(*p1)
        glVertex3f(*p2)
        glVertex3f(*p3)
        glVertex3f(*p4)
        glEnd()











