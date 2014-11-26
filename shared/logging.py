import logging, logging.handlers
import os, os.path

def setup(filename, level=None):
    loglevel = logging.WARNING if level is None else getattr(logging, level)
    
    logger = logging.getLogger()
    logger.setLevel(loglevel)
    
    consolehandler = logging.StreamHandler()
    consolehandler.setLevel(logging.DEBUG)
    fileformatter = logging.Formatter('%(name)s\t%(levelname)s\t%(message)s')
    consolehandler.setFormatter(fileformatter)
    logger.addHandler(consolehandler)
    
    if not os.path.exists('logs'):
        try:
            os.mkdir('logs', 0o775)
        except OSError as e:
            logger.warn('Could not create logs directory - %s', e)
    if os.path.exists('logs'):
        if not os.path.isdir('logs'):
            logger.warn('Can not add RotatingFileHandler - logs is not a directory')
        else:
            filehandler = logging.handlers.RotatingFileHandler('logs/%s.log'%(filename), maxBytes=3*1024**2, backupCount=3)
            filehandler.setLevel(logging.DEBUG)
            fileformatter = logging.Formatter('%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s')
            filehandler.setFormatter(fileformatter)
            logger.addHandler(filehandler)

def setLogLevel(ll):
    loglevel = getattr(logging, ll)
    logger = logging.getLogger()
    logger.setLevel(loglevel)
