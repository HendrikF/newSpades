import struct

class ByteBuffer(object):
    def __init__(self, data=b''):
        self.data = data
    
    def __len__(self):
        return len(self.data)
    
    def append(self, data):
        self.data += data
    
    def contains(self, data):
        return data in self.data
    
    def read(self, num, peek=False):
        if num > len(self.data):
            return False
        result = self.data[:num]
        if not peek:
            self.data = self.data[num:]
        return result
    
    def readStruct(self, format, peek=False):
        format = '!' + format
        size = struct.calcsize(format)
        data = self.read(size, peek)
        return struct.unpack(format, data)
