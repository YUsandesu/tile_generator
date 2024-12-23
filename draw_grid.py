import py5
import numpy as np
import json

# Load intersection points data
with open('intersection_points.json', 'r') as file:
    intersection_points = json.load(file)

with open('grid.json', 'r') as file:
    grid = json.load(file)

with open('data.json', 'r') as file:
    data = json.load(file)

# Sample fixed data input
data['grid'] = grid
data['intersectionPoints'] = intersection_points

def setup():
    py5.size(800, 800)
    py5.no_loop()
    draw_lines(py5, data)

def draw():
    pass

def draw_lines(instance, data):
    grid = data['grid']
    spacing = data['spacing']
    multiplier = data['multiplier']
    rotate = py5.radians(data['rotate'])

    instance.push()
    instance.background(51)  # Using a single value for grayscale background
    instance.stroke_weight(1)
    instance.translate(instance.width / 2, instance.height / 2)
    instance.rotate(rotate)

    # selectedLines = data['selectedLines']

    for line in grid:
        # if any(e['angle'] == line['angle'] and e['index'] == line['index'] for e in selectedLines):
        #     instance.stroke(0, 255, 0)
        # else:
        instance.stroke(255, 0, 0)
        draw_line(instance, multiplier * line['angle'], spacing * line['index'])

    if data['showIntersections']:
        instance.no_stroke()
        instance.fill(255)
        for pt in data['intersectionPoints'].values():
            instance.circle(pt['x'] * spacing, pt['y'] * spacing, 4)

    instance.stroke_weight(2)
    instance.stroke(0, 191, 255)
    instance.no_fill()
    # for tile in data['selectedTiles']:
    #     instance.circle(tile['x'] * spacing, tile['y'] * spacing, 10)

    instance.pop()

def draw_line(instance, angle, index):
    x0 = get_x_val(angle, index, -instance.height)
    x1 = get_x_val(angle, index, instance.height)
    if not np.isnan(x0) and not np.isnan(x1) and abs(x0) < 1000000 and abs(x1) < 1000000:
        instance.line(x0, -instance.height, x1, instance.height)
    else:
        y0 = get_y_val(angle, index, -instance.width)
        y1 = get_y_val(angle, index, instance.width)
        instance.line(-instance.width, y0, instance.width, y1)

def get_x_val(angle, index, y):
    return (index - y * py5.sin(angle)) / py5.cos(angle)

def get_y_val(angle, index, x):
    return (index - x * py5.cos(angle)) / py5.sin(angle)

py5.run_sketch()