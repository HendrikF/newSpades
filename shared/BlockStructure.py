import struct

from transmitter.ByteBuffer import ByteBuffer

import logging
logger = logging.getLogger(__name__)

class BlockStructure:
    """ A structure of blocks...
    """
    FACES = [
        ( 0, 1, 0), # UP
        ( 0,-1, 0), # DOWN
        (-1, 0, 0), # FRONT
        ( 1, 0, 0), # BACK
        ( 0, 0, 1), # RIGHT
        ( 0, 0,-1), # LEFT
    ]
    
    """Represents a structure of cubes"""
    def __init__(self):
        # dict[(x, y, z)] = (r, g, b)
        self.blocks = {}
    
    def addBlock(self, position, color):
        if position in self.blocks:
            self.removeBlock(position)
        self.blocks[position] = color
    
    def removeBlock(self, position):
        return self.blocks.pop(position, None)
    
    def exportBytes(self):
        # create color palette
        colorsSet = set(list(self.blocks.values()))
        colors = {}
        # pack palette
        data = struct.pack('!i', len(colorsSet))
        for i, color in enumerate(colorsSet):
            colors[color] = i
            data += struct.pack('!fff', color[0], color[1], color[2])
        # pack blocks
        data += struct.pack('!i', len(self.blocks))
        for position, color in self.blocks.items():
            data += struct.pack('!iiii', position[0], position[1], position[2], colors[color])
        return data
    
    def importBytes(self, bytes):
        byteBuffer = ByteBuffer(bytes)
        # read color palette
        numColors = byteBuffer.readStruct('i')[0]
        colors = []
        for _ in range(numColors):
            colors.append(byteBuffer.readStruct('fff'))
        # read blocks
        numBlocks = byteBuffer.readStruct('i')[0]
        for _ in range(numBlocks):
            position = byteBuffer.readStruct('iii')
            color = colors[byteBuffer.readStruct('i')[0]]
            self.addBlock(position, color)
        # for chaining
        return self
