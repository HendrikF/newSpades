#!/usr/bin/python3
from server.Registry import Registry

from server.Server import Server

registry = Registry()
registry('Server', Server)

# Load scripts here

server = registry('Server')(registry)
server.start()
