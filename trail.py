import py5
import numpy as np

def setup():
    py5.size(800, 800)
    py5.background('#004477')
    py5.stroke('#FFFFFF')
    py5.stroke_weight(3)
    py5.no_loop()
    py5.no_fill()

def draw_triangle(x, y, side_length):
    h = (side_length * (3 ** 0.5)) / 2  # height of the equilateral triangle
    py5.begin_shape()
    py5.vertex(x, y)
    py5.vertex(x + side_length / 2, y - h)
    py5.vertex(x - side_length / 2, y - h)
    py5.end_shape(py5.CLOSE)

def draw_hexagon(x, y, side_length):
    for i in range(6):
        py5.push_matrix()
        py5.translate(x, y)
        py5.rotate(py5.radians(60 * i))
        draw_triangle(0, 0, side_length)
        py5.pop_matrix()

def draw():
    py5.background('#004477')
    side_length = 50
    h = side_length * np.sqrt(3) / 2  # height of the equilateral triangle
    x_step = 3 * side_length
    y_step = 2 * h
    cols = int(py5.width // x_step) 
    rows = int(py5.height // y_step)

    for row in range(rows + 1):
        for col in range(cols + 1):
            x0 = col * x_step
            y0 = row * y_step
            x1 = x0 + 1.5 * side_length
            y1 = y0 + h
            draw_hexagon(x0, y0, side_length)
            draw_hexagon(x1, y1, side_length)

py5.run_sketch()