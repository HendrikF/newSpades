from threading import Thread
import shared.logging
from shared import Messages
from server.BasicServer import BasicServer
from server.types import MultikeyDict
from server.ServerPlayer import ServerPlayer
from server.Connection import Connection
from shared.Map import Map

from server import config

import logging
logger = logging.getLogger(__name__)

class NewSpadesServer(BasicServer):
    def __init__(self, *args):
        super().__init__(*args)
        self.addr = (
            config.get('host', ''),
            config.get('port', 55555)
        )
        self._server.messageFactory.add(*Messages.messages)
        self.commandThread = Thread(target=self.consoleCommands)
        self.commandThread.daemon = True
        
        self.connections = {}
        self.map = Map()
    
    def start(self):
        self.commandThread.start()
        self.map.load()
        super().start()
    
    def consoleCommands(self):
        self.running = True
        while self.running:
            try:
                c = input(': ')
            except EOFError:
                self.running = False
            else:
                if c == 'exit':
                    self.running = False
                elif c == 'help':
                    print('Available Commands: help, exit, log {DEBUG|INFO|WARNING|ERROR|CRITICAL}')
                elif c.startswith('log '):
                    c = c[4:].strip()
                    shared.logging.setLogLevel(c)
    
    def onConnect(self, peer):
        self.connections[peer] = Connection(self, peer)
    
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
