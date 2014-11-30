import legume
import time
import threading
from shared.Messages import Messages
from shared.Player import Player

class Networking(object):
    def __init__(self, window):
        self._client = legume.Client()
        self._client.OnMessage += self.on_message
        self.window = window
        self.running = True
        self.thread = None
        
    def on_message(self, sender, args):
        if legume.messages.message_factory.is_a(args, 'JoinMsg'):
            self.window.otherPlayers[args.username.value] = Player(username=args.username.value)
        elif legume.messages.message_factory.is_a(args, 'PlayerUpdateMsg'):
            if args.username.value == self.window.player.username:
                self.window.player.updateFromMsg(args)
            else:
                self.window.otherPlayers[args.username.value].updateFromMsg(args)
        else:
            print('Unknown Message: %s' % args)
            
    def connect(self, host, port):
        self._client.connect((host, port))
        
    def loop(self):
        while self.running:
            self._client.update()
            time.sleep(0.01)
            
    def start(self):
        self.thread = threading.Thread(target=self.loop)
        self.thread.start()
        
    def stop(self).
        self.running = False
        
        
