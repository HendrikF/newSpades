#!/usr/bin/python3
import argparse
import sys

import shared.logging

###################
# Setup argparser

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--loglevel', nargs='?', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the severity threshold of logged messages')
parser.add_argument('-c', '--create-config', action='store_true', dest='create_config', help='Only create default config file and exit')
args = parser.parse_args()

#################
# Setup logging

shared.logging.setup('server')
if args.loglevel:
    shared.logging.setLogLevel(args.loglevel)

import logging
logger = logging.getLogger()

#########################
# Write and load config

from server.config import config

if args.create_config:
    # config created by importing config, we can exit
    sys.exit()

##################
# Load scripts

from importlib import import_module

from server import registry

from server.Server import Server
registry.add('Server', Server)
from server.ServerPlayer import ServerPlayer
registry.add('ServerPlayer', ServerPlayer)

# scripts will be a reference to the config entry
scripts = config.get('scripts', [])
scriptModules = []
for script in scripts[:]:
    try:
        scriptModules.append(import_module('scripts.' + script))
    except ImportError as e:
        logger.error('Cant load script %s: %s', script, e)
        # we remove the failed scripts, so scripts can check for dependencies
        scripts.remove(script)

for module in scriptModules:
    logger.info('Loading script %s', module.__name__.replace('scripts.', ''))
    module.applyScript()

################
# Start server

server = registry.get('Server')()
server.start()
