import legume
import time
import threading
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
        self.commandThread.start()
        self._server = legume.Server()
        self._server.OnConnectRequest += self.connectHandler
        self._server.OnMessage += self.messageHandler
        self._server.OnDisconnect += self.disconnectHandler
        self._server.listen((self.addr, self.port))
        self.loop()
    
    def loop(self):
        self.running = True
        self.last_update = 0
        self.last_network = 0
        while self.running:
            # Physics
            t = time.time()
            if t - self.last_update >= self.time_update:
                self.update(t - self.last_update)
                self.last_update = t
                t = time.time()
            # Networking
            if t - self.last_network >= self.time_network:
                self.updateNetwork(t - self.last_network)
                self.last_network = t
            # Update legume-Server
            self._server.update()
            time.sleep(0.001)
    
    def update(self, delta):
        pass
    
    def updateNetwork(self, delta):
        pass
    
    def connectHandler(self, sender, args):
        logger.info('Client connected: %s', sender.address)
    
    def disconnectHandler(self, sender, args):
        logger.info('Client disconnected: %s', sender.address)
    
    def messageHandler(self, sender, msg):
        logger.debug('Recieved Message from %s: %s', sender.address, msg)
    
    def broadcastMessage(self, msg, reliable=False):
        if not reliable:
            self._server.send_message_to_all(msg)
        else:
            self._server.send_reliable_message_to_all(msg)
            
    def consoleCommands(self):
        while self.running:
            c = input(": ")
            if c == "exit":
                self.running = False
