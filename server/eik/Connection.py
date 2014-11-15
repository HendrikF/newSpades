
import socket
import threading
import json

class ClientListener(threading.Thread):
    
    def __init__(self, host, port, server):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.server = server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    def run(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        while True:
            if self.server.config["max_players"] > self.server.numberOfPlayers:
                self.conn, self.addr = self.socket.accept()
                self.addr, self.remotePort = self.addr
                client = ClientHandler(self.conn, self.addr, self.remotePort, self.server)
                client.setDaemon(True)
                client.start()
                self.server.players.append(client)
                client = None

class Team(object):
    def __init__(self, name, r, g, b, spectator):
        self.name = name
        self.r = r
        self.g = g
        self.b = b
        self.spectator = spectator
        self.players = []
    
    def joinPlayer(self, name):
        self.players.append(name)

class Player(object):
    def __init__(self):
        self.team = None
        self.name = None
        self.health = 100
        self.weapons = []
        self.kills = 0
        self.deaths = 0

class ClientHandler(threading.Thread, Player):
    serverLock = threading.Lock()
    
    def __init__(self, conn, addr, port, server):
        threading.Thread.__init__(self)
        Player.__init__(self)
        self.conn = conn
        self.addr = addr
        self.port = port
        self.server = server
        
    def run(self):
        print(self.addr, "connected! ("+str(self.port)+")")
        with ClientHandler.serverLock:
            self.server.numberOfPlayers += 1
        name = self.conn.recv(1024).decode()
        if name in self.server.getPlayerNames(self.server):
            self.conn.sendall("False".encode())
            self.conn.close()
            print(self.addr, "disconnected! ("+str(self.port)+")")
            with ClientHandler.serverLock:
                self.server.numberOfPlayers -= 1
        else:
            self.conn.sendall("True".encode())
            self.name = name
            self.conn.sendall(json.dumps(self.server.config["teams"]).encode())
            team_n = self.conn.recv(1024).decode()
            team = 0
            for i, t in enumerate(self.server.teams):
                #print(i, t.name)
                if t.name == team_n:
                    team = i
                    break
            #print(team)
            if team < 0 or team >= len(self.server.teams):
                self.team = 0
                self.server.teams[0].joinPlayer(self.name)
                team = 0
            elif self.server.teams[team].spectator:
                self.team = team
                self.server.teams[team].joinPlayer(self.name)
            else:
                if self.server.config["teambalance"] == 0:
                    self.team = team
                    self.server.teams[team].joinPlayer(self.name)
                else:
                    myT = len(self.server.teams[team].players)
                    bal = self.server.config["teambalance"]
                    i = 0
                    for t in self.server.teams:
                        if len(t.players)+bal < myT+1 or len(t.players)-bal > myT+1:
                            self.team = i
                            t.joinPlayer(self.name)
                            team = i
                            break
                        i += 1
                    if self.team is None:
                        self.team = team
                        self.server.teams[team].joinPlayer(self.name)
            print(self.name+" joined "+self.server.teams[self.team].name+"!")
            self.conn.sendall(self.server.teams[team].name.encode())
            """
            Do CLIENT-READER + CLIENT-WRITER
            """






