import pygame
from math import sin, cos, radians
from random import randrange
from Player import *
from Renderer import *
from Map import *

class NewSpades(object):
    def __init__(self):
        self.fullscreen = False
        #self.fullscreen = True
        self.screen = (1000, 750)
        self.title = "NewSpades"
        self.max_fps = 60
        
        self.running = True
        self.clock = pygame.time.Clock()
        
        self.player = Player("_debuguser_")
        
        self.renderer = Renderer(self)
        
        self.keys = {
            "FWD": pygame.K_w,
            "BWD": pygame.K_s,
            "LEFT": pygame.K_a,
            "RIGHT": pygame.K_d,
            "JUMP": pygame.K_SPACE,
            "CROUCH": pygame.K_LSHIFT
        }
    
    def start(self):
        options = pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE
        if self.fullscreen:
            options |= pygame.FULLSCREEN
        pygame.init()
        self.display = pygame.display.set_mode(self.screen, options, 16)
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        self.map = Map(self.loadMap())
        self.player.position.z = self.map.getZ(0, 0)+self.player.eyeHeight()
        
        self.renderer.start()
        
        self.loop()
    
    def loadMap(self):
        f = open("map.map")
        import json
        data = json.load(f)
        f.close()
        return data
    
    def loop(self):
        while self.running == True:
            self.clock.tick(self.max_fps)
            pygame.display.set_caption("{} - FPS: {:.3f}".format(self.title, self.clock.get_fps()))
            self.handleEvents()
            self.update()
            self.renderer.render()
            pygame.display.flip()
        pygame.quit()
    
    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handleKeyboard(1, event)
            elif event.type == pygame.KEYUP:
                self.handleKeyboard(0, event)
            elif event.type == pygame.MOUSEMOTION:
                self.handleMouse(event)
    
    def handleKeyboard(self, action, ev):
        if ev.key == pygame.K_ESCAPE:
            self.running = False
        
        if action == 1:
            if ev.key == self.keys["FWD"]:
                self.player.velocity[0] = 1
            elif ev.key == self.keys["BWD"]:
                self.player.velocity[0] = -1
            elif ev.key == self.keys["LEFT"]:
                self.player.velocity[1] = 1
            elif ev.key == self.keys["RIGHT"]:
                self.player.velocity[1] = -1
            #elif ev.key == self.keys["JUMP"]:
            #    self.player.velocity[2] = 1
            elif ev.key == self.keys["CROUCH"]:
                self.player.crouching = True
        
        elif action == 0:
            if ev.key == self.keys["FWD"]:
                self.player.velocity[0] = 0
            elif ev.key == self.keys["BWD"]:
                self.player.velocity[0] = 0
            elif ev.key == self.keys["LEFT"]:
                self.player.velocity[1] = 0
            elif ev.key == self.keys["RIGHT"]:
                self.player.velocity[1] = 0
            #elif ev.key == self.keys["JUMP"]:
            #    self.player.velocity[2] = 0
            elif ev.key == self.keys["CROUCH"]:
                self.player.crouching = False
    
    def handleMouse(self, event):
        if event.pos == event.rel:
            return
        
        yaw = -event.rel[0]/10
        pitch = event.rel[1]/10
        
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
        if float(self.player.velocity) != 0:
            time = self.clock.get_time()
            self.player.position += (
                self.player.getVectorFromOrientation( self.player.velocity ).update(z=0)
                    .getUnitVector( self.player.speed )
                + self.player.velocity.update(x=0, y=0)
            ) * (time/1000)
            if self.player.position.x > self.map.len_x-1:
                self.player.position.x = self.map.len_x-1
            elif self.player.position.x < 0:
                self.player.position.x = 0
            
            if self.player.position.y > self.map.len_y-1:
                self.player.position.y = self.map.len_y-1
            elif self.player.position.y < 0:
                self.player.position.y = 0
            
            if self.player.position.z > self.map.len_z-1:
                self.player.position.z = self.map.len_z-1
            elif self.player.position.z < 0:
                self.player.position.z = 0
