import math

class Connection(object):
    def __init__(self, events, server, peer):
        self.events = events
        self.server = server
        self.peer = peer
        self.player = None
        
        self.sendMap()
        self.sendAssets()
    
    @property
    def active(self):
        return self.player is not None
    
    def invoke(self, name, *args, **kw):
        self.events.invoke(name, self, *args, **kw)
    
    def sendMap(self):
        data = self.server.map.exportBytes()
        msg = self.peer.endpoint.messageFactory.getByName('Map')(data=data)
        self.peer.send(msg)
    
    def sendAssets(self):
        Msg = self.peer.endpoint.messageFactory.getByName('Asset')
        for name, data in self.server.assetManager.assets.items():
            self.peer.send(Msg(name=name, data=data))
    
    def update(self, dt):
        try:
            self.player.update(dt)
        except AttributeError:
            pass
    
    def updatePhysics(self, dt):
        try:
            self.player.updatePhysics(dt)
        except AttributeError:
            pass
    
    def onDisconnect(self):
        pass
    
    def receivedMessage(self, msg):
        if msg == 'Join':
            self.receivedJoin(msg)
        
        elif msg == 'PlayerUpdate':
            self.receivedPlayerUpdate(msg)
        
        elif msg == 'BlockBuild':
            self.receivedBlockBuild((msg.x, msg.y, msg.z), (msg.r, msg.g, msg.b))
        
        elif msg == 'BlockBreak':
            self.receivedBlockBreak((msg.x, msg.y, msg.z))
    
    def receivedJoin(self, msg):
        pass
    
    def receivedPlayerUpdate(self, msg):
        pass
    
    def receivedBlockBuild(self, position, color):
        self.server.map.addBlock(position, color)
    
    def receivedBlockBreak(self, position):
        self.server.map.removeBlock(position)
    
    """def onJoin(self, msg, peer):
        username = msg.username
        # free username
        if self.players.get(username) is None:
            logger.info('Player %s joined', username)
            # tell the others that this player joined
            self.send(msg, exclude=[peer.id])
            logger.warning('--Broadcasting join of %s', username)
            # tell him which players are already here
            for p in self.players.itervalues():
                peer.send(self.server._server.messageFactory.getByName('JoinMsg')(username=p.username))
                logger.warning('--Sending %s existence of %s', username, p.username)
            self.players[(peer, peer.id, username)] = ServerPlayer(peer, username)
            
        else:
            logger.warning('Received JoinMsg for existent Player! %s %s - Disconnecting him!', peer, msg)
            peer.disconnect()"""
