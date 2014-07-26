from math import sqrt

class Vector(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    getList = lambda self: [self.x, self.y, self.z]
    getTuple = lambda self: (self.x, self.y, self.z)
    
    # Operations with Integers
    def _calc_num(self, other, method):
        return self.__class__(
            method(self.x, other), 
            method(self.y, other), 
            method(self.z, other)
        )
    
    # Operations with other Vectors
    def _calc_vec(self, other, method):
        return self.__class__(
            method(self.x, other.x), 
            method(self.y, other.y), 
            method(self.z, other.z)
        )
    
    #__add__ = partial(_calc_vec, method=lambda x,y: x+y)
    __add__ = lambda self,other: self._calc_vec(other, method=lambda x,y: x+y)
    __sub__ = lambda self,other: self._calc_vec(other, method=lambda x,y: x-y)
    
    __mul__ = lambda self,other: self._calc_num(other, method=lambda x,y: x*y)
    __floordiv__ = lambda self,other: self._calc_num(other, method=lambda x,y: x//y)
    __div__ = lambda self,other: self._calc_num(other, method=lambda x,y: x/y)
    __mod__ = lambda self,other: self._calc_num(other, method=lambda x,y: x%y)
    __pow__ = lambda self,other: self._calc_num(other, method=lambda x,y: x**y)
    
    # Reflected operations
    __rmul__ = __mul__
    __rfloordiv__ = lambda self,other: self._calc_num(other, method=lambda x,y: y//x)
    __rdiv__ = lambda self,other: self._calc_num(other, method=lambda x,y: y/x)
    __rmod__ = lambda self,other: self._calc_num(other, method=lambda x,y: y%x)
    __rpow__ = lambda self,other: self._calc_num(other, method=lambda x,y: y**x)
    
    # Augmented assignment
    __iadd__ = __add__
    __isub__ = __sub__
    __imul__ = __mul__
    __ifloordiv__ = __floordiv__
    __idiv__ = __div__
    __imod__ = __mod__
    __ipow__ = __pow__
    
    # Type conversion
    __float__ = lambda self: sqrt(self.x**2 + self.y**2 + self.z**2)
    __int__ = __len__ = lambda self: round(float(self))
    round = lambda self: self.__class__(round(self.x), round(self.y), round(self.z))
    
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
        if float(self) == 0:
            return self.__class__(0, 0, 0)
        return self.__div__(float(self) / unit)
    
    def update(self, x=None, y=None, z=None):
        if x == None:
            x = self.x
        if y == None:
            y = self.y
        if z == None:
            z = self.z
        return self.__class__(x, y, z)
