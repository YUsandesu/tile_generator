import py5
import math
import json

with open('data.json', 'r') as file:
    data = json.load(file)

def draw_tiles(data):
    steps = data['steps']
    multiplier = data['multiplier']
    spacing = min(py5.width, py5.height) / steps
    pre_factor = spacing * multiplier / math.pi
    pre_factor *= data['zoom']
    stroke_val = data['stroke']
    rotate_val = py5.radians(data['rotate'])
    stroke_weight = min(math.sqrt(pre_factor) / 4.5, 1)
    pan = -data['zoom'] * min(py5.width, py5.height) * data['pan']

    py5.push()
    py5.background(0, 0, 51)
    py5.translate(py5.width / 2 + pan, py5.height / 2)
    py5.rotate(rotate_val)
    py5.stroke_weight(stroke_weight)

    for coor, tile in data['intersectionPoints'].items():
        tile_is_selected = any(e['x'] == tile['x'] and e['y'] == tile['y'] for e in data['selectedTiles'])

        tile_in_selected_line = False
        num_lines_passing_through_tile = 0

        if data['selectedLines']:
            for line in tile['lines']:
                if any(e['angle'] == line['angle'] and e['index'] == line['index'] for e in data['selectedLines']):
                    tile_in_selected_line = True
                    num_lines_passing_through_tile += 1

        if data['colorTiles']:
            color = next(e for e in data['tiles'] if (data['orientationColoring'] and e['angles'] == tile['angles']) or e['area'] == tile['area'])

            py5.fill(color['fill'])
            if data['showStroke']:
                py5.stroke(stroke_val, stroke_val, stroke_val)
            else:
                py5.no_stroke()

            if tile_in_selected_line:
                py5.fill(0, 255, 0)
                if num_lines_passing_through_tile > 1:
                    py5.fill(60, 179, 113)
            if tile_is_selected:
                py5.fill(128, 215, 255)

        else:
            py5.stroke(0, 255, 0)
            py5.no_fill()

            if tile_in_selected_line:
                py5.fill(0, 255, 0, 150)
                if num_lines_passing_through_tile > 1:
                    py5.fill(60, 179, 113, 150)
            if tile_is_selected:
                py5.fill(110, 110, 255)

        py5.begin_shape()
        for pt in tile['dualPts']:
            py5.vertex(pre_factor * pt['x'], pre_factor * pt['y'])
        py5.end_shape(py5.CLOSE)

    py5.pop()

def setup():
    py5.size(800, 800)

def draw():
    draw_tiles(data)

py5.run_sketch()