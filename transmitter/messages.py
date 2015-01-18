import struct
from collections import OrderedDict
from .error import *

import logging
logger = logging.getLogger(__name__)

class Message(object):
    """A Message is a packet of data which can be sent over the network.
    Every Message has a unique msgID and usually some fields of data of a special type and a default value.
    Custom Messages have a msgID greater than 0."""
    msgID = 0
    msgData = {
        #'name': ('type', '(default)value')
    }
    
    def __init__(self):
        # make ordered dict to have keys in a defined order, dict would be 'random'
        msgData = OrderedDict(sorted(self.msgData.items()))
        if self.msgID == 0:
            logger.error('Message with id of 0 initialized, which is not allowed!')
            raise InvalidMessageID('msgID 0 is not allowed')
    
    def __getattr__(self, name):
        try:
            return self.msgData[name][1]
        except KeyError:
            logger.error('Wanted to access nonexistent message key', name)
            raise InvalidMessageField("key '{}' not found".format(name))
    
    def __setattr__(self, name, value):
        try:
            t, v = self.msgData[name]
            self.msgData[name] = (t, value)
        except KeyError:
            logger.error('Wanted to change nonexistent message key', name)
            raise InvalidMessageField("key '{}' not found".format(name))
    
    def getBytes(self):
        format = '!Ql'
        values = [self.msgID]
        for k, v in self.msgData.items():
            t = v[0]
            v = v[1]
            if t == 'int':      format += 'l'
            elif t == 'float':  format += 'd'
            elif t in ('str', 'bytes'):
                if t == 'str':
                    v = v.encode()
                format += 'l'
                values.append(len(v))
                format += str(len(v)) + 's'
            elif t == 'bool':   format += '?'
            else:
                logger.error('Cant encode message key of unknown type', t)
                raise InvalidFieldFormat("type '{}' unknown".format(t))
            values.append(v)
        size = struct.calcsize(format)
        values = [size] + values
        return struct.pack(format, *values)
    
    def readFromByteBuffer(self, byteBuffer):
        for k, v in self.msgData.items():
            t = v[0]
            if t == 'int':      self.__setattr__(k, byteBuffer.readStruct('l')[0])
            elif t == 'float':  self.__setattr__(k, byteBuffer.readStruct('d')[0])
            elif t in ('str', 'bytes'):
                length = byteBuffer.readStruct('l')[0]
                data = byteBuffer.readStruct(str(length) + 's')[0]
                if t == 'str':
                    data = data.decode()
                self.__setattr__(k, data)
            elif t == 'bool':   self.__setattr__(k, byteBuffer.readStruct('?')[0])
            else:
                logger.error('Cant decode message key of unknown type %s', t)
                raise InvalidFieldFormat("type '{}' unknown".format(t))
    
    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.msgData)

class MessageFactory(object):
    """A class that holds all the Message classes which can be received from the network"""
    def __init__(self):
        self.messagesByID = {}
        self.messagesByName = {}
        self.add(TConnectMessage, TDisconnectMessage)
    
    def add(self, *classes):
        for clas in classes:
            if not issubclass(clas, Message):
                logger.error('Message classes must subclass Message')
                raise TypeError('Classes must subclass Message')
            if (clas.msgID in self.messagesByID) ^ (clas.__name__ in self.messagesByName):
                logger.error('Message classes cant have the same id')
                raise DuplicateMessageID
            self.messagesByID[clas.msgID] = clas
            self.messagesByName[clas.__name__] = clas
            logger.info('Added message type to factory (%s, %s)', clas.__name__, clas.msgID)
    
    def getByID(self, _id):
        try:
            return self.messagesByID[_id]
        except KeyError:
            logger.error('Cant find message with id %s', _id)
            raise MessageNotFound("Message id '{}' not found".format(_id))
    
    def getByName(self, name):
        try:
            return self.messagesByName[name]
        except KeyError:
            logger.error('Cant find message with name %s', name)
            raise MessageNotFound("Message name '{}' not found".format(name))
    
    def is_a(self, message, name):
        return isinstance(message, self.getByName(name))
    
    def readMessage(self, byteBuffer):
        if len(byteBuffer) >= struct.calcsize('!Q'):
            if len(byteBuffer) >= byteBuffer.readStruct('Q', peek=True)[0]:
                # now remove size
                byteBuffer.readStruct('Q')[0]
                msgID = byteBuffer.readStruct('l')[0]
                msg = self.getByID(msgID)()
                msg.readFromByteBuffer(byteBuffer)
                return msg
        return False

# System messages
###################

class TSystemMessage(Message):
    """Not for sending over the network!
    These Messages are just inserted into the queue when special events happen"""
    def getBytes(self):
        return b''
    
    def readFromByteBuffer(self, byteBuffer):
        pass

class TConnectMessage(TSystemMessage):
    msgID = -1

class TDisconnectMessage(TSystemMessage):
    msgID = -2
