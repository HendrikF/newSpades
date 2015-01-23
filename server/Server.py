import time
import threading
import transmitter.general
from shared import Messages
from shared.Player import Player
import shared.logging

import logging
logger = logging.getLogger(__name__)

class Server(object):
    def __init__(self, registry):
        self.registry = registry
        self.addr = ''
        self.port = 55555
        self.players = {}
        self.time_update = 0.01
        self.time_network = 0.1
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
            # Update transmitter-Server
            self._server.update()
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
            if wait:
                time.sleep(min(self.time_update, self.time_network))
    
    def update(self, delta):
        pass
    
    def updateNetwork(self, delta):
        for username, player in self.players.items():
            self._server.send(player.getUpdateMsg(), exclude=[player.peer.id])
    
    def onConnect(self, peer):
        logger.info('Client connected: %s', peer.addr)
    
    def onDisconnect(self, peer):
        logger.info('Client disconnected: %s', peer.addr)
        for username, player in self.players.items():
            if player.peer.id == peer.id:
                self.players.pop(username)
                msg = Messages.LeaveMsg()
                msg.username = username
                self._server.send(msg)
                break
    
    def onMessage(self, msg, peer):
        logger.info('Recieved Message: %s', msg)
        if self._server.messageFactory.is_a(msg, 'JoinMsg'):
            self.players[msg.username] = Player(None, username=msg.username)
            self.players[msg.username].peer = peer
            self._server.send(msg, exclude=[peer.id])
            for player in self.players.values():
                if player.peer.id == peer.id:
                    continue
                msg = Messages.JoinMsg()
                msg.username = player.username
                self._server.sendTo(peer.id, msg)
        elif self._server.messageFactory.is_a(msg, 'PlayerUpdateMsg'):
            try:
                self.players[msg.username].updateFromMsg(msg)
            except KeyError:
                logger.error('Unknown username: %s', msg)
        else:
            logger.error('Unknown Message: %s', msg)
    
    def consoleCommands(self):
        while self.running:
            c = input(": ")
            if c == "exit":
                self.running = False
            elif c == "help":
                print('Available Commands: help, exit')
            elif c.startswith('log '):
                c = c[4:].strip()
                shared.logging.setLogLevel(c)
