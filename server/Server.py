import time
import threading
import transmitter.general
from server import registry
from shared import Messages
from shared.Map import Map
import shared.logging

import logging
logger = logging.getLogger(__name__)

class Server(object):
    def __init__(self):
        self.addr = ('', 55555)
        self.players = {}
        self.time_update = 0.01
        self.time_network = 1
        self.commandThread = None
        self.running = True
    
    def start(self):
        self.commandThread = threading.Thread(target=self.consoleCommands)
        self.commandThread.daemon = True
        self.commandThread.start()
        self.map = Map()
        self.map.load()
        self._server = transmitter.general.Server()
        self._server.messageFactory.add(*Messages.messages)
        self._server.onConnect.attach(self.onConnect)
        self._server.onMessage.attach(self.onMessage)
        self._server.onDisconnect.attach(self.onDisconnect)
        self._server.onTimeout.attach(self.onTimeout)
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
                time.sleep(0.001)
    
    def update(self, delta):
        for player in self.players.values():
            player.update(delta, self.map)
    
    def updateNetwork(self, delta):
        for player in self.players.values():
            self._server.send(Messages.CompleteUpdate(
                username=player.username,
                x=player.position[0],
                y=player.position[1],
                z=player.position[2],
                dx=player.dx,
                dy=player.dy,
                dz=player.dz,
                yaw=player.yaw,
                pitch=player.pitch,
                crouching=player.crouching))
    
    def onConnect(self, peer):
        logger.info('Client connected: %s', peer)
    
    def onDisconnect(self, peer):
        logger.info('Client disconnected: %s', peer)
        player = self.getPlayerFromPeer(peer)
        if player:
            self.players.pop(player.username)
            self._server.send(Messages.LeaveMsg(username=player.username))
    
    def onTimeout(self, *args, **kw):
        self.onDisconnect(*args, **kw)
    
    def onMessage(self, msg, peer):
        logger.debug('Recieved Message from peer %s: %s', peer, msg)
        
        print('peers:', self._server.peers)
        print('players:', self.players)
        
        if msg == 'JoinMsg':
            if msg.username not in self.players:
                logger.info('Player %s joined', msg.username)
                ServerPlayer = registry.get('ServerPlayer')
                player = ServerPlayer(peer, username=msg.username)
                # tell the others that this player joined
                self._server.send(msg, exclude=[peer.id])
                logger.warning('Broadcasting join of %s', msg.username)
                # tell him which players are already there
                for p in self.players.values():
                    peer.send(Messages.JoinMsg(username=p.username))
                    logger.warning('Sending %s existence of %s', msg.username, p.username)
                self.players[msg.username] = player
                
            else:
                logger.warning('Received JoinMsg for existent Player! %s %s - Disconnecting him!', peer, msg)
                peer.disconnect()
        
        elif msg == 'Update':
            # peer is only allowed to update his own player !
            player = self.getPlayerFromPeer(peer)
            if player:
                player.applyUpdate(msg.key, msg.value)
            else:
                logger.warning('Peer is no Player but sent PlayerUpdate: %s - %s', peer, msg)
        
        elif msg == 'BlockBuildMsg':
            self._server.send(msg, exclude=[peer.id])
        
        elif msg == 'BlockBreakMsg':
            self._server.send(msg, exclude=[peer.id])
        
        elif msg == 'CompleteUpdate':
            pass
            # we dont accept CompleteUpdates from clients
            # with this elif we simply avoid the following warning
        
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
