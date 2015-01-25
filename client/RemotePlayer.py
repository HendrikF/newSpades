from pyglet.gl import *
from client.ClientPlayer import ClientPlayer

class RemotePlayer(ClientPlayer):
    """Removes calcGravity() and calcCollision() from client.ClientPlayer.ClientPlayer
    to give the server more control over collisions and save computation power."""
    def calcGravity(self, time):
        return 0
    
    def calcCollision(self, position, map):
        return position
