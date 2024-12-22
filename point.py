import numpy as np

class Point2:
    def __init__(self, x, y):
        self.x = x 
        self.y = y 
        self.pos = np.array([x, y])

    def __repr__(self):
        return f"2D Point: ({self.x}, {self.y})"
    
    def __neg__(self):
        return -self.pos
    
    def __add__(self, point):
        print("Here")
        print(isinstance(point, Point2))
        print(self)
        print(point)
        print(type(point))
        print(isinstance(point, np.ndarray))
        assert isinstance(point, Point2) or (isinstance(point, np.ndarray) and len(point) == 2)
        if isinstance(point, Point2):
            return self.pos + point.pos
        return self.pos + point
    
    # def __radd__(self, point):
    #     print("Here")
    #     print(isinstance(point, Point2))
    #     print(self)
    #     print(point)
    #     print(type(point))
    #     print(isinstance(point, np.ndarray))
    #     assert isinstance(point, Point2) or (isinstance(point, np.ndarray) and len(point) == 2)
    #     if isinstance(point, Point2):
    #         return self.pos + point.pos
    #     return self.pos + point
    
    def __sub__(self, point):
        assert isinstance(point, Point2) or (isinstance(point, np.ndarray) and len(point) == 2)
        if isinstance(point, Point2):
            return self.pos - point.pos
        return self.pos - point
    
    def __mul__(self, const):
        return self.pos * const
    
    def __rmul__(self, const):
        return self.pos * const
    
    def __truediv__(self, const):
        return self * (1 / const)

class Point3:
    def __init__(self, x, y, z):
        self.x = x 
        self.y = y 
        self.z = z
        self.pos = np.array([x, y, z])

    def __repr__(self):
        return f"3D Point: ({self.x}, {self.y}, {self.z})"
    
    def __neg__(self):
        return -self.pos
    
    def __add__(self, point):
        assert isinstance(point, Point3) or (isinstance(point, np.ndarray) and len(point) == 3)
        if isinstance(point, Point3):
            return self.pos + point.pos
        return self.pos + point
    
    def __sub__(self, point):
        assert isinstance(point, Point3) or (isinstance(point, np.ndarray) and len(point) == 3)
        if isinstance(point, Point3):
            return self.pos - point.pos
        return self.pos - point
    
    def __mul__(self, const):
        return self.pos * const
    
    def __rmul__(self, const):
        return self.pos * const
    
    def __truediv__(self, const):
        return self * (1 / const)

if __name__ == "__main__":
    a = Point2(10, 12)
    print(a)
    b = Point2(10, 10)
    print(a + b)
    print(a - b)
    
    c = Point3(10, 10, 11)
    d = Point3(10, 11, 11)
    print(c)
    print(c + d)