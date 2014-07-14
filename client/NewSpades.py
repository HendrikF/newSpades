import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from math import sin, cos, radians

class NewSpades(object):
    def __init__(self):
        self.fullscreen = False
        self.screen = (1000, 750)
        self.title = "NewSpades"
        self.max_fps = 60
        self.farplane = 150
        
        self.background = [0.5, 0.5, 0.75, 0]
        
        self.running = True
        # Startposition [x,y,z]
        self.position = [0, 10, 0]
        # Blickrichtung [x,y]
        # x = y = 0 => geradeaus
        # 0 <= x <= 360 (361 => 1)
        # -90 <= y <= 90 (Begrenzung)
        self.orientation = [0, 0]
        self.step = 0.5
        self.clock = pygame.time.Clock()
    
    def start(self):
        options = pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE
        if self.fullscreen:
            options |= pygame.FULLSCREEN
        pygame.init()
        self.display = pygame.display.set_mode(self.screen, options, 16)
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        pygame.key.set_repeat(100, 20)
        
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
        self.loop()
    
    def loop(self):
        while self.running == True:
            self.clock.tick(self.max_fps)
            pygame.display.set_caption("{} - FPS: {:.1f}".format(self.title, self.clock.get_fps()))
            self.handleEvents()
            self.update()
            self.render()
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(*self.background)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluPerspective(45, 1, 1, self.farplane)
        gluLookAt(
            sin(radians(self.orientation[0])), 
            sin(radians(self.orientation[1])), 
            cos(radians(self.orientation[0]))*cos(radians(self.orientation[1])), 
            0, 0, 0, 
            0, 1, 0)
        
        glPushMatrix()
        
        glTranslatef(-self.position[0], -self.position[1], -self.position[2])
        
        glBegin(GL_QUADS)
        glColor(0, 0, 1)
        glVertex3f(-10, 0, 10)
        glVertex3f(10, 0, 10)
        glVertex3f(10, 0, -10)
        glVertex3f(-10, 0, -10)
        glEnd()
        
        glBegin(GL_QUADS)
        glColor(0, 1, 0)
        glVertex3f(-10, 1, 10)
        glVertex3f(10, 1, 10)
        glVertex3f(10, 1, -10)
        glVertex3f(-10, 1, -10)
        glEnd()
        
        glPopMatrix()
        
        pygame.display.flip()
        
    def update(self):
        pass
    
    def handleKeyboard(self, event):
        if event.key == pygame.K_ESCAPE:
            self.running = False
        if event.key == pygame.K_a:
            self.position[0] -= self.step
        if event.key == pygame.K_d:
            self.position[0] += self.step
            
        if event.key == pygame.K_w:
            self.position[2] -= self.step
        if event.key == pygame.K_s:
            self.position[2] += self.step
            
        if event.key == pygame.K_q:
            self.position[1] -= self.step
        if event.key == pygame.K_e:
            self.position[1] += self.step
    
    def handleMouse(self, event):
        self.orientation[0] -= event.rel[0]/10
        self.orientation[1] += event.rel[1]/10
        if self.orientation[0] < 0:
            self.orientation[0] += 360
        elif self.orientation[0] > 360:
            self.orientation[0] -= 360
        if self.orientation[1] < -90:
            self.orientation[1] = -90
        elif self.orientation[1] > 90:
            self.orientation[1] = 90
    
    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handleKeyboard(event)
            elif event.type == pygame.MOUSEMOTION:
                self.handleMouse(event)
    



