from threading import Thread
import shared.logging
from shared import Messages
from server.BasicServer import BasicServer
from server.ServerPlayer import ServerPlayer
from server.Connection import Connection
from shared.Map import Map
from server.AssetManager import AssetManager

from server import config

import logging
logger = logging.getLogger(__name__)

class NewSpadesServer(BasicServer):
    def __init__(self, events):
        self.events = events
        addr = (
            config.get('host', ''),
            config.get('port', 55555)
        )
        super().__init__(addr)
        self._server.messageFactory.add(*Messages.messages)
        self.commandThread = Thread(target=self.consoleCommands)
        self.commandThread.daemon = True
        
        self.connections = {}
        self.map = None
        
        self.assetManager = AssetManager()
    
    def invoke(self, name, *args, **kw):
        self.events.invoke(name, self, *args, **kw)
    
    def start(self):
        self.commandThread.start()
        self.loadMap('map.nsmap')
        self.loadAssets()
        super().start()
    
    def loadMap(self, filename):
        self.map = Map()
        with open(filename, 'rb') as f:
            self.map.importBytes(f.read())
    
    def loadAssets(self):
        self.assetManager.load('assets')
    
    def consoleCommands(self):
        self.running = True
        while self.running:
            try:
                c = input(': ')
            except EOFError:
                self.running = False
                print('')
            else:
                if c == 'exit':
                    self.running = False
                elif c == 'help':
                    print('Available Commands: help, exit, log {DEBUG|INFO|WARNING|ERROR|CRITICAL}')
                elif c.startswith('log '):
                    c = c[4:].strip()
                    shared.logging.setLogLevel(c)
    
    def onConnect(self, peer):
        self.connections[peer] = Connection(self.events, self, peer)
    
    def onDisconnect(self, peer):
        try:
            connection = self.connections.pop(peer)
        except KeyError:
            pass
        else:
            connection.onDisconnect()
    
    def onTimeout(self, *args, **kw):
        self.onDisconnect(*args, **kw)
    
    def onMessage(self, msg, peer):
        self.connections[peer].receivedMessage(msg)
    
    def update(self, dt):
        for connection in self.connections.values():
            connection.update(dt)
    
    def updatePhysics(self, dt):
        for connection in self.connections.values():
            connection.updatePhysics(dt)
    
    def updateNetwork(self, dt):
        pass
