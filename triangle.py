import numpy as np
from point import Point2, Point3

class Triangle:
    def __init__(self, p0, p1, p2, idx):
        self.p0 = p0 
        self.p1 = p1 
        self.p2 = p2
        self.idx = idx
        self.barycenter = (self.p0 + self.p1 + self.p2) / 3
        self.width, self.height = np.max([self.p0, self.p1, self.p2], axis=0) - np.min([self.p0, self.p1, self.p2], axis=0)

    def __repr__(self):
        return f"Triangle {self.idx}: centered at {self.barycenter}"
    
    @staticmethod
    def equilateral(idx, factor=50):
        # p0 = np.array([0, np.sqrt(3)/2 - np.sqrt(3)/6]) * factor
        # p1 = np.array([-1/2, -np.sqrt(3)/6]) * factor
        # p2 = np.array([1/2, -np.sqrt(3)/6]) * factor
        p0 = np.array([-1/2, np.sqrt(3)/6]) * factor
        p1 = np.array([1/2, np.sqrt(3)/6]) * factor
        p2 = np.array([0, -np.sqrt(3)/2 + np.sqrt(3)/6]) * factor
        return Triangle(
            p0=p0, p1=p1, p2=p2,
            idx=idx
        )
    
    
if __name__ == "__main__":
    a = np.array([0, 0])
    b = np.array([0, 3])
    c = np.array([4, 0])
    tri = Triangle(a, b, c, idx=0)
    print(tri)
    tri1 = Triangle.equilateral(1)
    print(tri1)
    print(tri1.p0, tri1.p1, tri1.p2)
    print(tri1.width, tri1.height)