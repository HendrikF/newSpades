#!/usr/bin/python3
from Registry import Registry

from Server import Server

registry = Registry()
registry('Server', Server)

# Load scripts here

server = registry('Server')(registry)
server.start()
