import time
import transmitter.general
import shared.logging

import logging
logger = logging.getLogger(__name__)

class BasicServer(object):
    def __init__(self, addr=('', 55555)):
        self.addr = addr
        self.time_update = 0.01
        self.time_network = 0.1
        
        self._server = transmitter.general.Server()
        self._server.onConnect.attach(self.onConnect)
        self._server.onMessage.attach(self.onMessage)
        self._server.onDisconnect.attach(self.onDisconnect)
        self._server.onTimeout.attach(self.onTimeout)
    
    def start(self):
        self._server.bind(self.addr)
        self._server.start()
        self.loop()
    
    def loop(self):
        self.running = True
        t = time.time()
        self.last_update = t
        self.last_network = t
        while self.running:
            # Update transmitter-Server
            self._server.update()
            wait = True
            # Update
            t = time.time()
            if t - self.last_update >= self.time_update:
                wait = False
                dt = t - self.last_update
                self.update(dt)
                self.last_update = t
                # to prevent wrong physics because of slow pc
                # we make very small time steps
                m = 10
                dt = min(dt, 0.2) / m
                for _ in range(m):
                    self.updatePhysics(dt)
            # Networking
            # (Take time again, because update could take long)
            t = time.time()
            if t - self.last_network >= self.time_network:
                wait = False
                self.updateNetwork(t - self.last_network)
                self.last_network = t
            if wait:
                time.sleep(0.002)
    
    def send(self, *args, **kw):
        self._server.send(*args, **kw)
    
    def update(self, dt):
        pass
    
    def updatePhysics(self, dt):
        pass
    
    def updateNetwork(self, dt):
        pass
    
    def onConnect(self, peer):
        pass
    
    def onDisconnect(self, peer):
        pass
    
    def onTimeout(self, *args, **kw):
        pass
    
    def onMessage(self, msg, peer):
        pass
