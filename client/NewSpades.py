import pygame
from math import sin, cos, radians
import time
from shared.Player import *
from client.Renderer import *
from shared.Map import *
from shared.Collision import *
import threading
from shared import Messages
import legume

class NewSpades(object):
    def __init__(self):
        self.fullscreen = False
        #self.fullscreen = True
        self.screen = (1000, 750)
        self.title = "NewSpades"
        self.max_fps = 60
        
        self.running = True
        self.clock = pygame.time.Clock()
        
        self.player = Player("_debuguser_", network=False)
        self.players = []
        
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
        
        self._client = legume.Client()
        self._client.OnMessage += self.messageHandler
        self.host = 'localhost'
        self.port = 55555
        self.networkThread = None
        self.updatingNetwork = True
        self.lastNetworkUpdate = time.time()
        self.networkUpdateTime = 1
        
        self.debugsight = False
    
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
        
        self.connect()
        self.startUpdateNetwork()
        
        self.renderer.start()
        
        self.loop()
    
    def messageHandler(self, sender, msg):
        print('Message:')
        print(msg)
        if msg.MessageTypeID == Messages.JoinMsg.MessageTypeID:
            self.players.append(Player(msg.username.value))
        elif msg.MessageTypeID == Messages.PlayerUpdateMsg.MessageTypeID:
            player = self.getPlayerByName(msg.username.value)
            if player:
                player.position = Vector(msg.posx.value, msg.posy.value, msg.posz.value)
                player.velocity = Vector(msg.velx.value, msg.vely.value)
                player.velocity_z = msg.velz.value
                player.orientation = [msg.yaw.value, msg.pitch.value, msg.roll.value]
                player.crouching = msg.crouching.value
            else:
                print('Player not found: '+msg.username.value)
    
    def connect(self):
        self._client.connect((self.host, self.port))
    
    def startUpdateNetwork(self):
        self.networkThread = threading.Thread(target=self.updateNetwork)
        self.networkThread.start()
    
    def updateNetwork(self):
        while self.updatingNetwork:
            time.sleep(0.01)
            if time.time() - self.lastNetworkUpdate >= self.networkUpdateTime:
                self._client.update()
                if not self._client.connected: continue
                
                pum = Messages.PlayerUpdateMsg()
                pum.username.value = self.player.username
                pum.posx.value, pum.posy.value, pum.posz.value = self.player.position
                pum.velx.value, pum.vely.value, z = self.player.velocity
                pum.velz.value = self.player.velocity_z
                pum.yaw.value, pum.pitch.value, pum.roll.value = self.player.orientation
                pum.crouching.value = self.player.crouching
                self.sendMessage(pum)
                
                self.lastNetworkUpdate = time.time()
    
    def getPlayerByName(self, username):
        for player in self.players:
            if player.username == username:
                return player
        return False
    
    def sendMessage(self, msg, reliable=False):
        if not reliable:
            self._client.send_message(msg)
        else:
            self._client.send_reliable_message(msg)
    
    def loadMap(self):
        f = open("client/map.map")
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
        self.close()
    
    def close(self):
        pygame.quit()
        self._client.disconnect()
        self.updatingNetwork = False
    
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
            elif ev.key == pygame.K_k:
                self.debugsight = not self.debugsight
        
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
        
        self.player.move(time, self.map)
        
        for player in self.players:
            player.move(time, self.map)
