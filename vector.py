import numpy as np
from point import Point2, Point3

class Vec2:
    def __init__(self, p0, p1):
        assert isinstance(p0, Point2) or (isinstance(p0, np.ndarray) and len(p0) == 2)
        assert isinstance(p1, Point2) or (isinstance(p1, np.ndarray) and len(p0) == 2)
        self.p0 = p0
        self.p1 = p1
        self.vec2 = p1 - p0

    def __repr__(self):
        return f"a 2D vector {self.p0} -> {self.p1}: {self.vec2}"
    
    def __neg__(self):
        return -self.vec2
    
    def __add__(self, v2):
        assert isinstance(v2, Vec2) or (isinstance(v2, np.ndarray) and len(v2) == 2)
        if isinstance(v2, Vec2):
            return self.vec2 + v2.vec2
        return self.vec2 + v2
    
    def __sub__(self, v2):
        assert isinstance(v2, Vec2) or (isinstance(v2, np.ndarray) and len(v2) == 2)
        if isinstance(v2, Vec2):
            return self.vec2 - v2.vec2
        return self.vec2 - v2
    
    def __mul__(self, const):
        return self.vec2 * const
    
    def __rmul__(self, const):
        return self.vec2 * const
    
    def __truediv__(self, const):
        return self.vec2 * (1 / const)
    
    def __abs__(self):
        return np.sqrt(self.vec2 @ self.vec2)

class Vec3:
    def __init__(self, p0, p1):
        assert isinstance(p0, Point3) or (isinstance(p0, np.ndarray) and len(p0) == 3)
        assert isinstance(p1, Point3) or (isinstance(p1, np.ndarray) and len(p0) == 3)
        self.p0 = p0
        self.p1 = p1
        self.vec3 = p1 - p0

    def __repr__(self):
        return f"a 3D vector {self.p0} -> {self.p1}: {self.vec3}"
    
    def __neg__(self):
        return -self.vec3
    
    def __add__(self, v2):
        assert isinstance(v2, Vec3) or (isinstance(v2, np.ndarray) and len(v2) == 3)
        if isinstance(v2, Vec3):
            return self.vec3 + v2.vec3
        return self.vec3 + v2
    
    def __sub__(self, v2):
        assert isinstance(v2, Vec3) or (isinstance(v2, np.ndarray) and len(v2) == 3)
        if isinstance(v2, Vec3):
            return self.vec3 - v2.vec3
        return self.vec3 - v2
    
    def __mul__(self, const):
        return self.vec3 * const
    
    def __rmul__(self, const):
        return self.vec3 * const
    
    def __truediv__(self, const):
        return self.vec3 * (1 / const)
    
    def __abs__(self):
        return np.sqrt(self.vec3 @ self.vec3)
    

if __name__ == "__main__":
    a = Point2(10, 12, 0)
    b = Point2(10, 10, 1)
    v = Vec2(b, a)
    print(v)
    v1 = Vec2(2 * b, a)
    print(v1 + v)
    print(v * 2)
    print(v / 2)
    print(abs(v))
    
    a = Point3(10, 12, 15, 0)
    b = Point3(10, 10, 1, 1)
    v = Vec3(b, a)
    print(v)
    v1 = Vec3(2 * b, a)
    print(v1 + v)
    print(v * 2)
    print(v / 2)
    print(abs(v))