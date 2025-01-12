import py5
import numpy as np

def distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def draw_bezier_curve(lengg, stjiaodu):
    P0 = np.array([0, 0])
    P1 = np.array([100/300*lengg, 120/300*lengg])
    P2 = np.array([150/300*lengg, 200/300*lengg])
    P3 = np.array([lengg, 0])
    
    # def bezier(t, P0, P1, P2, P3):
    #     return (1 - t) ** 3 * P0 + 3 * (1 - t) ** 2 * t * P1 + 3 * (1 - t) * t ** 2 * P2 + t ** 3 * P3

    # t_values = np.linspace(0, 1, 8)
    # bezier_points = np.array([bezier(t, P0, P1, P2, P3) for t in t_values])
    # points = np.array([bezier_points])

    # sveangdis = []
    # current_angle = 0
    # for i in range(len(points) - 1):
    #     delta_x = points[i + 1][0] - points[i][0]
    #     delta_y = points[i + 1][1] - points[i][1]
    #     distance = np.linalg.norm(points[i] - points[i + 1])
    #     angle_radians = np.arctan2(delta_y, delta_x)
    #     angle_degrees = np.degrees(angle_radians)
    #     relative_angle = angle_degrees - current_angle
    #     sveangdis.append((relative_angle, distance))
    #     current_angle = angle_degrees

    py5.circle(P0[0], P0[1], 10)
    py5.circle(P1[0], P1[1], 10)
    # py5.push_matrix()
    # py5.translate(0, 0)
    # py5.rotate(np.radians(stjiaodu))

    # for angle, distance in sveangdis:
    #     py5.rotate(np.radians(angle))
    #     py5.line(0, 0, distance, 0)
    #     py5.translate(distance, 0)

    # py5.pop_matrix()

def setup():
    py5.size(800, 800)
    py5.background(255)

def draw():
    py5.stroke(0)
    py5.no_fill()
    lengg = 300
    stjiaodu = 90
    draw_bezier_curve(lengg, stjiaodu)

py5.run_sketch()