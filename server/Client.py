
import socket

host = input("Hostname: ")
port = int(input("Port: "))
print("Connecting...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
print("Connected!")
data = "".encode('utf-8')
while data.decode() != "STOP":
	msg = input("Message: ")
	s.sendall(msg.encode('utf-8'))
	data = s.recv(1024)
	print("Received '"+data.decode()+"'")
s.close()
print("Connection closed!")
