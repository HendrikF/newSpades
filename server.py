#!/usr/bin/python3
import argparse
from shared import logging

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--loglevel', nargs='?', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the severity threshold of logged messages')
args = parser.parse_args()

logging.setup('server')
if args.loglevel:
    logging.setLogLevel(args.loglevel)

from server.Registry import Registry
registry = Registry()

from server.Server import Server
registry('Server', Server)
from server.ServerPlayer import ServerPlayer
registry('ServerPlayer', ServerPlayer)

# Load scripts here - give them the registry to read, inherit from and write their 'children' into

server = registry('Server')()
server.start()
