#!/usr/bin/python3
import argparse
from shared import logging

parser = argparse.ArgumentParser()
#parser.add_argument('host', nargs='?', help='Serverhost')
#parser.add_argument('-p', '--port', type=int, help='Serverport')
parser.add_argument('-l', '--loglevel', nargs='?', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the severity threshold of logged messages')
args = parser.parse_args()

logging.setup('server')
if args.loglevel:
    logging.setLogLevel(args.loglevel)

from server.Registry import Registry

from server.Server import Server

registry = Registry()
registry('Server', Server)

# Load scripts here - give them the registry to read, inherit from and write their 'children' into
# TODO: give registry automatically (e.g. wrapper)

server = registry('Server')(registry)
server.start()
