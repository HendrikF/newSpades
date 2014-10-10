from math import sqrt

class Vector(object):
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    
    # Operations with Numbers
    def _calc_num(self, other, method):
        return self.__class__(
            method(self.x, other), 
            method(self.y, other), 
            method(self.z, other)
        )
    
    # Operations with Vectors
    def _calc_vec(self, other, method):
        return self.__class__(
            method(self.x, other.x), 
            method(self.y, other.y), 
            method(self.z, other.z)
        )
    
    __add__ = lambda self,other: self._calc_vec(other, method=lambda x,y: x+y)
    __sub__ = lambda self,other: self._calc_vec(other, method=lambda x,y: x-y)
    
    __mul__ = lambda self,other: self._calc_num(other, method=lambda x,y: x*y)
    __floordiv__ = lambda self,other: self._calc_num(other, method=lambda x,y: x//y)
    __truediv__ = lambda self,other: self._calc_num(other, method=lambda x,y: x/y)
    __mod__ = lambda self,other: self._calc_num(other, method=lambda x,y: x%y)
    __pow__ = lambda self,other: self._calc_num(other, method=lambda x,y: x**y)
    
    # Reflected operations
    __rmul__ = __mul__
    __rfloordiv__ = lambda self,other: self._calc_num(other, method=lambda x,y: y//x)
    __rtruediv__ = lambda self,other: self._calc_num(other, method=lambda x,y: y/x)
    __rmod__ = lambda self,other: self._calc_num(other, method=lambda x,y: y%x)
    __rpow__ = lambda self,other: self._calc_num(other, method=lambda x,y: y**x)
    
    # Augmented assignment
    __iadd__ = __add__
    __isub__ = __sub__
    __imul__ = __mul__
    __ifloordiv__ = __floordiv__
    __itruediv__ = __truediv__
    __imod__ = __mod__
    __ipow__ = __pow__
    
    # Type conversion
    __float__ = lambda self: sqrt(self.x**2 + self.y**2 + self.z**2)
    __int__ = __len__ = lambda self: int(round(float(self)))
    def __round__(self, n=0):
        x = round(self.x, n)
        y = round(self.y, n)
        z = round(self.z, n)
        if n == 0:
            x = int(x)
            y = int(y)
            z = int(z)
        return self.__class__(x, y, z)
    
    __str__ = __repr__ = lambda self: "<Vector:({v.x}, {v.y}, {v.z})>".format(v=self)
    
    __pos__ = lambda self: self._calc_num(1, method=lambda x,y: abs(x))
    __neg__ = lambda self: self._calc_num(1, method=lambda x,y: -abs(x))
    
    __iter__ = lambda self: iter([self.x, self.y, self.z])
    
    __getitem__ = lambda self,key: {
        "x": self.x,
        "y": self.y,
        "z": self.z,
        0: self.x,
        1: self.y,
        2: self.z
    }[key]
    def __setitem__(self, key, value):
        if key == "x" or key == 0:
            self.x = value
        elif key == "y" or key == 1:
            self.y = value
        elif key == "z" or key == 2:
            self.z = value
        else:
            raise IndexError
    
    def getUnitVector(self, unit=1):
        if float(self) == 0 or unit == 0:
            return self.__class__(0, 0, 0)
        return self.__truediv__(float(self) / unit)
    
    def getMainDirection(self):
        if abs(self.x) > abs(self.y):
            return 0
        elif abs(self.x) < abs(self.y):
            return 1
        else:
            return None
    
    def update(self, x=None, y=None, z=None):
        if x == None:
            x = self.x
        if y == None:
            y = self.y
        if z == None:
            z = self.z
        return self.__class__(x, y, z)
    
    def add(self, x=0, y=0, z=0):
        self.x += x
        self.y += y
        self.z += z
        return self
