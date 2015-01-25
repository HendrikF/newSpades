import time
import threading
from transmitter.general import Client
from shared import Messages
from client.RemotePlayer import RemotePlayer

import logging
logger = logging.getLogger(__name__)

class Networking(object):
    def __init__(self, window):
        self._client = Client()
        Messages.registerMessages(self._client.messageFactory)
        self._client.onMessage.attach(self.onMessage)
        self.window = window
        self.running = True
        self.thread = None
    
    def onMessage(self, msg, peer):
        logger.debug('Recieved Message: %s', msg)
        if self._client.messageFactory.is_a(msg, 'JoinMsg'):
            self.window.otherPlayers[msg.username] = RemotePlayer(self.window.model, self.window.sounds, username=msg.username)
        elif self._client.messageFactory.is_a(msg, 'PlayerUpdateMsg'):
            if msg.username == self.window.player.username:
                self.window.player.updateFromMsg(msg)
            else:
                try:
                    self.window.otherPlayers[msg.username].updateFromMsg(msg)
                except KeyError:
                    logger.error('Unknown username (peer: %s) : %s', msg)
        elif self._client.messageFactory.is_a(msg, 'LeaveMsg'):
            self.window.otherPlayers.pop(msg.username)
        else:
            logger.error('Unknown Message from peer %s: %s', peer, msg)
    
    def connect(self, host, port):
        self._client.connect(host, port)
        self._client.start()
    
    def loop(self):
        while self.running:
            self._client.update()
            time.sleep(0.001)
        self._client.stop()
    
    def start(self, username=''):
        if self.thread is None or not self.thread.isAlive():
            self.running = True
            self.thread = threading.Thread(target=self.loop)
            self.thread.daemon = True
            self.thread.start()
            self.window.player.username = username
            msg = Messages.JoinMsg()
            msg.username = username
            self.send(msg)
    
    def stop(self):
        self.running = False
    
    def send(self, msg):
        self._client.send(msg)
