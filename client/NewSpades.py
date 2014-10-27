import pygame
from math import sin, cos, radians
from Player import *
from Renderer import *
from Map import *
from Collision import *

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
            "CROUCH": pygame.K_LSHIFT,
            "FULLSCREEN": pygame.K_F11,
            "SHOOT": 1,
            "SCOPE": 3,
            "GRENADE": 2
        }
        self.mouseSensitivity = 0.1
    
    def start(self):
        self.ratio = self.screen[0] / self.screen[1]
        options = pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE
        if self.fullscreen:
            options |= pygame.FULLSCREEN
        pygame.init()
        self.display = pygame.display.set_mode(self.screen, options)
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        self.map = Map(self.loadMap())
        self.player.position.z = self.map.getZ(0, 0)
        
        self.renderer.start()
        
        self.loop()
    
    def loadMap(self):
        f = open("map.map")
        import json
        data = json.load(f)
        f.close()
        return data
    
    def loop(self):
        while self.running:
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handleClick(event)
    
    def handleClick(self, ev):
        if ev.button == self.keys["SHOOT"]:
            block = Collision.lookAtBlock(self.player, self.map)
            if block != False:
                self.map.setBlock(block[0], False)
        elif ev.button == self.keys["SCOPE"]:
            block = Collision.lookAtBlock(self.player, self.map)
            if block != False:
                self.map.setBlock(block[1], (0, 0, 1))
    
    def handleKeyboard(self, action, ev):
        if ev.key == pygame.K_ESCAPE:
            self.running = False
        
        if action == 1:
            if ev.key == self.keys["FWD"]:
                self.player.keys["FWD"] = True
            elif ev.key == self.keys["BWD"]:
                self.player.keys["BWD"] = True
            elif ev.key == self.keys["LEFT"]:
                self.player.keys["LEFT"] = True
            elif ev.key == self.keys["RIGHT"]:
                self.player.keys["RIGHT"] = True
            elif ev.key == self.keys["JUMP"] and self.player.hasGround(self.map):
                self.player.velocity_z = self.player.jumpSpeed
                self.player.jumping = self.player.jumpTime
            elif ev.key == self.keys["CROUCH"]:
                self.player.crouching = True
                self.player.wantToCrouch = True
            elif ev.key == self.keys["FULLSCREEN"]:
                pygame.display.toggle_fullscreen()
        
        elif action == 0:
            if ev.key == self.keys["FWD"]:
                self.player.keys["FWD"] = False
            elif ev.key == self.keys["BWD"]:
                self.player.keys["BWD"] = False
            elif ev.key == self.keys["LEFT"]:
                self.player.keys["LEFT"] = False
            elif ev.key == self.keys["RIGHT"]:
                self.player.keys["RIGHT"] = False
            #elif ev.key == self.keys["JUMP"]:
            #    self.player.velocity[2] = 0
            elif ev.key == self.keys["CROUCH"]:
                if self.map.getBlock(round(self.player.position + Vector(0, 0, 3))) == False:
                    self.player.crouching = False
                self.player.wantToCrouch = False
    
    def handleMouse(self, event):
        if event.pos == event.rel:
            return
        
        yaw = -event.rel[0] * self.mouseSensitivity
        pitch = event.rel[1] * self.mouseSensitivity
        
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
        time = self.clock.tick(self.max_fps)
        pygame.display.set_caption("{} - delta: {}ms - FPS: {:.3f}".format(self.title, time, self.clock.get_fps()))
        
        time /= 1000
        
        if self.player.crouching == True and self.player.wantToCrouch == False and self.map.getBlock(round(self.player.position + Vector(0, 0, 3))) == False:
            self.player.crouching = False
        
        if self.player.jumping > 0:
            self.player.jumping -= time*1000
        elif self.player.hasGround(self.map) == False:
            self.player.velocity_z += self.player.gravity * time
            if self.player.velocity_z < self.player.fallSpeed:
                self.player.velocity_z = self.player.fallSpeed
        elif self.player.hasGround(self.map) == True:
            self.player.velocity_z = 0
            self.player.position.z = round(self.player.position.z)
        
        self.player.move(time, self.map)
        if self.player.position.x > self.map.len_x-1:
            self.player.position.x = self.map.len_x-1
        elif self.player.position.x < 0:
            self.player.position.x = 0
        
        if self.player.position.y > self.map.len_y-1:
            self.player.position.y = self.map.len_y-1
        elif self.player.position.y < 0:
            self.player.position.y = 0
        
        if self.player.position.z < 0:
            self.player.position.z = 0
        
        
        if self.map.getBlock(round(self.player.position)) != False and self.map.getBlock(round(self.player.position+Vector(0, 0, 1))) != False and self.map.getBlock(round(self.player.position+Vector(0, 0, 2))) == False:
            self.player.position.z = round(self.player.position.z+1)
