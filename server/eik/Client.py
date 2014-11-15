
import socket
import json

host = input("Hostname: ")
port = int(input("Port: "))
print("Connecting...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
print("Connected!")

name = input("Username: ")
s.sendall(name.encode())
allowed = s.recv(1024).decode()
if allowed == "False":
    print("Name already in use!")
else:
    print("Name not in use!")
    teams = json.loads(s.recv(1024).decode())
    print("Write team-name to join:")
    for t in teams:
        print(" - ", t[0])
    team = input("Team: ")
    s.sendall(team.encode())
    team = s.recv(1024).decode()
    print("You joined " + team + "!")

"""
data = "".encode('utf-8')
while data.decode() != "STOP":
    msg = input("Message: ")
    s.sendall(msg.encode('utf-8'))
    data = s.recv(1024)
    print("Received '"+data.decode()+"'")
"""
s.close()
print("Connection closed!")
