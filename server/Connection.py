
import socket
import threading

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
			self.conn, self.addr = self.socket.accept()
			self.addr, self.remotePort = self.addr
			client = ClientHandler(self.conn, self.addr, self.remotePort, self.server)
			client.setDaemon(True)
			client.start()
			self.server.players.append(client)
			client = None
		
		

class ClientHandler(threading.Thread):
	serverLock = threading.Lock()
	
	def __init__(self, conn, addr, port, server):
		threading.Thread.__init__(self)
		self.conn = conn
		self.addr = addr
		self.port = port
		self.server = server
		
	def run(self):
		print(self.addr, "connected! ("+str(self.port)+")")
		with ClientHandler.serverLock:
			self.server.numberOfPlayers += 1
		data = "".encode('utf-8')
		while data.decode() != "STOP":
			data = self.conn.recv(1024)
			print("Received '"+data.decode()+"' from ", self.addr, "("+str(self.port)+")")
			self.conn.sendall(data)
		self.conn.close()
		print(self.addr, "disconnected! ("+str(self.port)+")")
		with ClientHandler.serverLock:
			self.server.numberOfPlayers -= 1






