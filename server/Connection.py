class Connection(object):
    def __init__(self, server, peer):
        self.server = server
        self.peer = peer
    
    def onDisconnect(self):
        pass
    
    def receivedMessage(self, msg):
        if msg == 'JoinMsg':
            self.receivedJoin(msg.username)
        
        elif msg == 'PlayerUpdate':
            # peer is only allowed to update his own player !
            player = self.players.get(peer)
            if player:
                player.updateFromMessage(msg)
            else:
                logger.warning('Peer is no Player but sent PlayerUpdate: %s - %s', peer, msg)
        
        elif msg == 'BlockBuildMsg':
            self.receivedBlockBuild((msg.x, msg.y, msg.z), (msg.r, msg.g, msg.b))
            self.server.send(msg, exclude=[peer.id])
        
        elif msg == 'BlockBreakMsg':
            self.receivedBlockBreak((msg.x, msg.y, msg.z))
            self.server.send(msg, exclude=[peer.id])
    
    def receivedJoin(self, username):
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
