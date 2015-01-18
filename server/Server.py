import time
import threading
import transmitter.general
from shared import Messages

import logging
logger = logging.getLogger(__name__)

class Server(object):
    def __init__(self, registry):
        self.registry = registry
        self.addr = ''
        self.port = 55555
        self.players = []
        self.time_update = 1
        self.time_network = 1
        self.commandThread = None
        self.running = True
    
    def start(self):
        self.commandThread = threading.Thread(target=self.consoleCommands)
        self.commandThread.daemon = True
        self.commandThread.start()
        self._server = transmitter.general.Server()
        Messages.registerMessages(self._server.messageFactory)
        self._server.onConnect.attach(self.onConnect)
        self._server.onMessage.attach(self.onMessage)
        self._server.onDisconnect.attach(self.onDisconnect)
        self._server.bind(self.addr, self.port)
        self._server.start()
        self.loop()
    
    def loop(self):
        self.running = True
        t = time.time()
        self.last_update = t
        self.last_network = t
        while self.running:
            wait = True
            # Physics
            t = time.time()
            if t - self.last_update >= self.time_update:
                self.update(t - self.last_update)
                self.last_update = t
                wait = False
            # Networking
            # (Take time again, because update could take long)
            t = time.time()
            if t - self.last_network >= self.time_network:
                self.updateNetwork(t - self.last_network)
                self.last_network = t
                wait = False
            # Update transmitter-Server
            self._server.update()
            if wait:
                time.sleep(min(self.time_update, self.time_network))
    
    def update(self, delta):
        pass
    
    def updateNetwork(self, delta):
        pass
    
    def onConnect(self, peer):
        logger.info('Client connected: %s', peer.addr)
        #msg = Messages.JoinMsg()
        #self.broadcastMessage(msg)
        #msg = Messages.PlayerUpdateMsg()
        #msg.posy = 2
        #msg.velx = 1
        #self.broadcastMessage(msg)
    
    def onDisconnect(self, peer):
        logger.info('Client disconnected: %s', peer.addr)
    
    def onMessage(self, msg, peer):
        logger.info('Recieved Message from %s: %s', peer.addr, msg)
    
    def broadcastMessage(self, msg):
        self._server.send(msg)
            
    def consoleCommands(self):
        while self.running:
            c = input(": ")
            if c == "exit":
                self.running = False
            elif c == "help":
                print('Available Commands: help, exit')
