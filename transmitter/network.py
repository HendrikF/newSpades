from threading import Thread
import socket
from collections import deque
from .event import Event
from .messages import Message, MessageFactory
from .error import *
from .bytebuffer import ByteBuffer

import logging
logger = logging.getLogger(__name__)

class NetworkEndpoint(object):
    """A NetworkEndpoint is a flexible interface for a Server and Client."""
    
    isServer = False
    isClient = False
    
    def __init__(self, async=False):
        self.async = async
        self.accepting = False
        self.thread = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.peers = {}
        self._lastPeerID = 0
        self.host = ''
        self.port = None
        self.messageFactory = MessageFactory()
        self.receivedMessages = deque()
        self.onMessage = Event()
        self.onConnect = Event()
        self.onDisconnect = Event()
    
    def bind(self, host, port):
        if self.isServer:
            self.host = host
            self.port = port
            self.socket.bind((host, port))
            self.socket.listen(0)
    
    def connect(self, host, port):
        if self.isClient:
            self.host = host
            self.port = port
            self.socket.connect((host, port))
    
    def start(self):
        if self.isServer:
            self.thread = Thread(target=self._accept)
            self.thread.daemon = True
            self.thread.start()
        elif self.isClient:
            self._newPeer(self.socket)
    
    def stop(self):
        self.accepting = False
        for _id, peer in self.peers.items():
            peer.stop(pop=False)
        self.peers = {}
        self.socket.close()
    
    def update(self):
        """Call this method regularly in sync mode"""
        while len(self.receivedMessages) > 0:
            msg, peer = self.receivedMessages.popleft()
            if msg.msgID > 0:
                self.onMessage(msg, peer)
            else:
                if self.messageFactory.is_a(msg, 'TConnectMessage'):
                    self.onConnect(peer)
                elif self.messageFactory.is_a(msg, 'TDisconnectMessage'):
                    self.onDisconnect(peer)
    
    def send(self, message, exclude=[]):
        data = message.getBytes()
        for _id, peer in list(self.peers.items()):
            if _id not in exclude:
                peer.send(data)
    
    def sendTo(self, _id, message):
        try:
            self.peers[_id].send(message.getBytes())
        except KeyError:
            raise PeerNotFound("Can't send message '{}' to peer id '{}'".format(message, _id))
    
    def _accept(self):
        self.accepting = True
        while self.accepting:
            conn, addr = self.socket.accept()
            self._newPeer(conn, addr)
    
    def _newPeer(self, sock, addr=None):
        peer = NetworkPeer(self, self.nextPeerID, sock, addr)
        peer.start()
        self.peers[peer.id] = peer
        if self.async:
            self.onConnect(peer)
        else:
            msg = self.messageFactory.getByName('TConnectMessage')()
            self.receivedMessages.append((msg, peer))
    
    def msgReceived(self, msg, peer):
        # prevent system messages from entering system
        if msg.msgID > 0:
            if self.async:
                self.onMessage(msg, peer)
            else:
                self.receivedMessages.append((msg, peer))
    
    def _peerDisconnected(self, peer, pop=True):
        if pop:
            self.peers.pop(peer.id)
        if self.async:
            self.onDisconnect(peer)
        else:
            msg = self.messageFactory.getByName('TDisconnectMessage')()
            self.receivedMessages.append((msg, peer))
    
    def __repr__(self):
        x = ''
        if self.isServer:
            x += ' (server mode, {} peers{})'.format(len(self.peers), ', accepting' if self.accepting else '')
        if self.isClient:
            x += ' (client mode)'
        x += ' ({}, {})'.format(self.host, self.port)
        return '<NetworkEndpoint{}>'.format(x)
    
    @property
    def nextPeerID(self):
        self._lastPeerID += 1
        return self._lastPeerID

class NetworkPeer(object):
    """A NetworkPeer provides the ability to write and listen on sockets.
    The Server has one NetworkPeer for each connected Client.
    A Client has only one NetworkPeer for the Server."""
    def __init__(self, endpoint, _id, sock, addr=None):
        self.endpoint = endpoint
        self.id = _id
        self.socket = sock
        self.addr = addr
        self.thread = None
        self.active = False
        self.buffer = ByteBuffer()
    
    def start(self):
        self.thread = Thread(target=self._listen)
        self.thread.daemon = True
        self.thread.start()
        self.active = True
    
    def send(self, data):
        if self.active:
            try:
                return self.socket.send(data)
            except socket.error as e:
                logger.error("Can't write to socket of peer %s: %s", self, e)
                self.stop()
        return False
    
    def stop(self, pop=True):
        self.active = False
        self.socket.close()
        self.endpoint._peerDisconnected(self, pop)
    
    def _listen(self):
        while True:
            try:
                data = self.socket.recv(1024)
            except socket.error as e:
                logger.error('Connection reset to peer %s: %s', self, e)
                break
            if not data:
                break
            self.buffer.append(data)
            self._parseMessages()
        self.stop()
    
    def _parseMessages(self):
        while True:
            msg = self.endpoint.messageFactory.readMessage(self.buffer)
            if not msg:
                break
            self.endpoint.msgReceived(msg, self)
    
    def __repr__(self):
        return '<NetworkPeer id={} addr={} act={}>'.format(self.id, self.addr, self.active)
