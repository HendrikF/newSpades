import time
import threading
import transmitter.general
from shared import Messages
from server import registry
import shared.logging

import logging
logger = logging.getLogger(__name__)

class Server(object):
    def __init__(self):
        self.addr = ''
        self.port = 55555
        self.players = {}
        self.time_update = 0.01
        self.time_network = 0.05
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
        for player in self.players.values():
            self._server.send(player.getUpdateMsg(), exclude=[player.peer.id])
    
    def onConnect(self, peer):
        logger.info('Client connected: %s', peer)
    
    def onDisconnect(self, peer):
        logger.info('Client disconnected: %s', peer)
        player = self.getPlayerFromPeer(peer)
        if player:
            self.players.pop(player.username)
            self._server.send(Messages.LeaveMsg(username=player.username))
    
    def onMessage(self, msg, peer):
        logger.debug('Recieved Message from peer %s: %s', peer, msg)
        
        if self._server.messageFactory.is_a(msg, 'JoinMsg'):
            if msg.username not in self.players:
                ServerPlayer = registry.get('ServerPlayer')
                self.players[msg.username] = ServerPlayer(peer, username=msg.username)
                # tell the others that this player joined
                self._server.send(msg, exclude=[peer.id])
                # tell him which players are already there
                for player in self.players.values():
                    if player.peer.id == peer.id:
                        continue
                    self._server.sendTo(peer.id, Messages.JoinMsg(username=player.username))
            else:
                logger.warning('Received JoinMsg for existent Player! %s %s - Disconnecting him!', peer, msg)
                peer.stop()
        
        elif self._server.messageFactory.is_a(msg, 'PlayerUpdateMsg'):
            # peer is only allowed to update his own player !
            player = self.getPlayerFromPeer(peer)
            if player:
                player.updateFromMsg(msg)
            else:
                logger.warning('Peer is no Player but sent PlayerUpdate: %s - %s', peer, msg)
        
        elif self._server.messageFactory.is_a(msg, 'BlockBuildMsg'):
            self._server.send(msg, exclude=[peer.id])
        
        elif self._server.messageFactory.is_a(msg, 'BlockBreakMsg'):
            self._server.send(msg, exclude=[peer.id])
        
        else:
            logger.warning('Unknown Message: %s', msg)
    
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
    
    def getPlayerFromPeer(self, peer):
        for player in self.players.values():
            if player.peer.id == peer.id:
                return player
        return False
