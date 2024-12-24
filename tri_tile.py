import py5
import numpy as np
from triangle import Triangle

tri_list = [Triangle.equilateral(i) for i in range(-10, 10, 1)]
# print(tri_list)
width = 720
height = 485
axis2view_dir = np.array([
    [1, 0],
    [0, -1]
])
axis2view_offset = np.array([width / 2, height / 2]).reshape([-1, 1])

tri_points_list = []
for tri in tri_list:
    tri_points = np.array([tri.p0, tri.p1, tri.p2])
    tri_points[:, 0] += tri.width * tri.idx
    # print(tri_points)
    tri_points = axis2view_dir @ tri_points.T + axis2view_offset
    tri_points = tri_points.T
    tri_points_list.append(tri_points)

def setup():
    py5.size(720, 485)
    py5.background('#004477')
    py5.stroke('#FFFFFF')
    py5.stroke_weight(3)
    
    for points in tri_points_list:
        previous_point = None
        for point in points:
            
            py5.circle(point[0], point[1], 2)
            if previous_point is not None:
                py5.line(
                    point[0], point[1],
                    previous_point[0], previous_point[1]
                )
            previous_point = point
        py5.line(
            point[0], point[1],
            points[0][0], points[0][1]
        )
    
# def draw():
#     py5.stroke('#FFFFFF')
#     py5.stroke_weight(3)
#     axis = 250
    
    
py5.run_sketch()