from .network import NetworkEndpoint

class Server(NetworkEndpoint):
    isServer = True

class Client(NetworkEndpoint):
    isClient = True
