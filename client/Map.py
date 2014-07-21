class Map(object):
    def __init__(self, data):
        self.data = data
        self.len_x = len(data)
        self.len_y = len(data[0])
        self.len_z = len(data[0][0])
    
    def getBlocks(self):
        for x, x_ in enumerate(self.data):
            for y, y_ in enumerate(x_):
                for z, z_ in enumerate(y_):
                    if z_ == False:
                        continue
                    if not self.isBlockHidden(x, y, z):
                        yield (x, y, z, z_)
    
    def isBlockHidden(self, x, y, z):
        if x+1 >= self.len_x:
            return False
        elif self.data[x+1][y][z] == False:
            return False
        if x <= 0:
            return False
        elif self.data[x-1][y][z] == False:
            return False
        
        if y+1 >= self.len_y:
            return False
        elif self.data[x][y+1][z] == False:
            return False
        if y <= 0:
            return False
        elif self.data[x][y-1][z] == False:
            return False
        
        if z+1 >= self.len_z:
            return False
        elif self.data[x][y][z+1] == False:
            return False
        if z <= 0:
            return False
        elif self.data[x][y][z-1] == False:
            return False
        
        return True
    
    def getZ(self, x, y):
        for z in range(self.len_z-1, -1, -1):
            if self.data[x][y][z] != False:
                return z
        return 0
