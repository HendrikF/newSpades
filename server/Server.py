import legume
import time
from shared import Messages

class Server(object):
    def __init__(self, registry):
        self.registry = registry
        self.addr = ''
        self.port = 55555
        self.players = []
        self.time_update = 1
        self.time_network = 1
    
    def start(self):
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
            if time.time() - self.last_update >= self.time_update:
                self.update(time.time() - self.last_update)
                self.last_update = time.time()
            # Networking
            if time.time() - self.last_network >= self.time_network:
                self.updateNetwork(time.time() - self.last_network)
                self.last_network = time.time()
            # Update legume-Server
            self._server.update()
            time.sleep(0.001)
    
    def update(self, delta):
        pass
    
    def updateNetwork(self, delta):
        pass
    
    def connectHandler(self, sender, args):
        print('Connect:')
        print(sender.address)
    
    def disconnectHandler(self, sender, args):
        print('Disconnect:')
        print(sender.address)
    
    def messageHandler(self, sender, msg):
        print('Message:')
        print(sender.address)
        print(msg)
    
    def broadcastMessage(self, msg, reliable=False):
        if not reliable:
            self._server.send_message_to_all(msg)
        else:
            self._server.send_reliable_message_to_all(msg)
