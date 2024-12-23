import math
import json
import random
import numpy as np
import hsluv
from data_dict import base_data

data = base_data.copy()

def approx(value):
    return round(value * data['inverseEpsilon']) / data['inverseEpsilon']

def dist(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# def convert_pts_2_str(points):
#     return ' '.join([f"{point[0] + 25},{point[1] + 25}" for point in points])


def calculate_offsets(symmetry, pattern, disorder, random_seed, pan, steps, shift):
    offsets = [pattern] * symmetry
    if disorder > 0:
        random.seed(f'random seed {symmetry} and {random_seed}')
        offsets = [e + disorder * (random.random() - 0.5) for e in offsets]
    if pan > 0:
        offsets = [e - steps * pan * shift[i] for i, e in enumerate(offsets)]
    return offsets

def multiplier(symmetry):
    return 2 * math.pi / symmetry

def steps(radius, symmetry):
    return 2 * round((radius / (symmetry - 1) - 1) / 2) + 1

def spacing(zoom, width, height, steps):
    return zoom * min(width, height) / steps

def make1Dgrid(steps):
    return sorted([i - (steps - 1) / 2 for i in range(steps)], key=abs)

def compute_grid(symmetry, steps, offsets):
    lines = []
    for i in range(symmetry):
        for n in make1Dgrid(steps):
            lines.append({'angle': i, 'index': n + offsets[i] % 1})
    return lines

def sin_cos_table(symmetry, multiplier):
    return [{'sin': math.sin(i * multiplier), 'cos': math.cos(i * multiplier)} for i in range(symmetry)]

def sin_cos_rotate(rotate):
    angle = math.radians(rotate)
    return {'sin': math.sin(angle), 'cos': math.cos(angle)}

def shift(sin_cos_table, sin_cos_rotate): # use cosine difference formula with lookup tables for optimization
    return [e['cos'] * sin_cos_rotate['cos'] - e['sin'] * sin_cos_rotate['sin'] for e in sin_cos_table]

def calculate_intersection_points(data, grid, sin_cos_table):
    pts = {}
    width, height = data['width'], data['height']
    rotate = math.radians(data['rotate'])
    epsilon = data['epsilon']
    symmetry = data['symmetry']
    steps = data['steps']
    spacing = data['spacing']
    multiplier = data['multiplier']
    offsets = data['offsets']

    for line1 in grid:
        for line2 in grid:
            if line1['angle'] < line2['angle']:
                sc1, sc2 = sin_cos_table[line1['angle']], sin_cos_table[line2['angle']]
                s1, c1, s2, c2 = sc1['sin'], sc1['cos'], sc2['sin'], sc2['cos']
                
                s12 = s1 * c2 - c1 * s2
                s21 = -s12
                
                if abs(s12) > epsilon:
                    x = (line2['index'] * s1 - line1['index'] * s2) / s12
                    y = (line2['index'] * c1 - line1['index'] * c2) / s21

                    xprime = x * math.cos(rotate) - y * math.sin(rotate)
                    yprime = x * math.sin(rotate) + y * math.cos(rotate)

                    # optimization: only list intersection points viewable on screen
                    if abs(xprime * spacing) <= width / 2 + spacing and abs(yprime * spacing) <= height / 2 + spacing:
                        if (steps == 1 and dist(x, y, 0, 0) <= 0.5 * steps) or dist(x, y, 0, 0) <= 0.5 * (steps - 1):
                            index = json.dumps([approx(x), approx(y)])
                            if index in pts.keys():
                                if line1 not in pts[index]['lines']:
                                    pts[index]['lines'].append(line1)
                                if line2 not in pts[index]['lines']:
                                    pts[index]['lines'].append(line2)
                            else:
                                pts[index] = {'x': x, 'y': y, 'lines': [line1, line2]}
    
    for pt in pts.values():
        angles = [line['angle'] * multiplier for line in pt['lines']]
        angles2 = [(angle + math.pi) % (2 * math.pi) for angle in angles]
        angles = sorted(set(approx(angle) for angle in angles + angles2))

        offset_pts = [{'x': pt['x'] - epsilon * math.sin(angle), 'y': pt['y'] + epsilon * math.cos(angle)} for angle in angles]

        median_pts = []
        num_pts = len(offset_pts)
        for i in range(num_pts):
            x0, y0 = offset_pts[i]['x'], offset_pts[i]['y']
            x1, y1 = offset_pts[(i + 1) % num_pts]['x'], offset_pts[(i + 1) % num_pts]['y']
            median_pts.append({'x': (x0 + x1) / 2, 'y': (y0 + y1) / 2})

        dual_pts = []
        mean = {'x': 0, 'y': 0}
        for my_pt in median_pts:
            xd, yd = 0, 0
            for i in range(symmetry):
                ci, si = sin_cos_table[i]['cos'], sin_cos_table[i]['sin']
                k = math.floor(my_pt['x'] * ci + my_pt['y'] * si - offsets[i])
                xd += k * ci
                yd += k * si
            dual_pts.append({'x': xd, 'y': yd})
            mean['x'] += xd
            mean['y'] += yd

        num_dual_pts = len(dual_pts)
        mean['x'] /= num_dual_pts
        mean['y'] /= num_dual_pts

        area = 0
        for i in range(num_dual_pts):
            x0, y0 = dual_pts[i]['x'], dual_pts[i]['y']
            x1, y1 = dual_pts[(i + 1) % num_dual_pts]['x'], dual_pts[(i + 1) % num_dual_pts]['y']
            area += 0.5 * (x0 * y1 - y0 * x1)

        pt['area'] = round(area * 1000) / 1000
        pt['numVertices'] = len(angles)
        pt['angles'] = angles
        pt['dualPts'] = dual_pts
        pt['mean'] = mean
    return pts

def calculate_colors(hue, hue_range, sat, contrast):
    lightness = 50

    start = [hue + hue_range, sat, lightness + contrast]
    end = [hue - hue_range, sat, lightness - contrast]
    return [start, end]

def lerp(start, stop, t):
    return start + t * (stop - start)

def rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

def normalize(points):
    num_pts = len(points)
    xbar = sum(p['x'] for p in points) / num_pts
    ybar = sum(p['y'] for p in points) / num_pts
    max_dist = 0
    for i in range(num_pts):
        for j in range(i, num_pts):
            d = dist(points[i]['x'], points[i]['y'], points[j]['x'], points[j]['y'])
            if d > max_dist:
                max_dist = d
    return [[50 * (p['x'] - xbar) / max_dist, 50 * (p['y'] - ybar) / max_dist] for p in points]

def calculate_color_palette(intersection_points, orientation_coloring, colors, reverse_colors):
    proto_tiles = list(intersection_points.values())

    def filter_function(e, f):
        return e['angles'] == f['angles'] if orientation_coloring else e['area'] == f['area']

    proto_tiles = [e for i, e in enumerate(proto_tiles) if all(not filter_function(e, f) for f in proto_tiles[:i])]
    proto_tiles.sort(key=lambda x: x['numVertices'])

    num_tiles = len(proto_tiles)
    start, end = colors

    color_palette = []
    range_val = num_tiles - 1 / 2

    for i, tile in enumerate(proto_tiles):
        h = lerp(start[0], end[0], i / range_val) % 360
        s = lerp(start[1], end[1], i / range_val)
        l = lerp(start[2], end[2], i / range_val)
        color = hsluv.hsluv_to_rgb([h, s, l])
        color = [round(255 * c) for c in color]
        color_palette.append({
            'fill': rgb_to_hex(*color),
            'points': normalize(tile['dualPts']),
            'area': tile['area'],
            'angles': tile['angles'],
        })

    if reverse_colors:
        reversed_colors = [e['fill'] for e in color_palette[::-1]]
        for i, e in enumerate(color_palette):
            e['fill'] = reversed_colors[i]
    return color_palette


# Calculate necessary values
steps_val = steps(data['radius'], data['symmetry'])
spacing_val = spacing(data['zoom'], data['width'], data['height'], steps_val)
multiplier_val = multiplier(data['symmetry'])
sin_cos_table_val = sin_cos_table(data['symmetry'], multiplier_val)
sin_cos_rotate_val = sin_cos_rotate(data['rotate'])
shift_val = shift(sin_cos_table_val, sin_cos_rotate_val)
offsets_val = calculate_offsets(data['symmetry'], data['pattern'], data['disorder'], data['randomSeed'], data['pan'], steps_val, shift_val)

# Update data with calculated values
data['steps'] = steps_val
data['spacing'] = spacing_val
data['multiplier'] = multiplier_val
data['offsets'] = offsets_val

# Calculate intersection points and tiles
grid = compute_grid(data['symmetry'], steps_val, offsets_val)
intersection_points = calculate_intersection_points(data, grid, sin_cos_table_val)
# tiles = calculate_tiles(intersection_points, data['multiplier'])
colors = calculate_colors(data['hue'], data['hueRange'], data['sat'], data['contrast'])
color_palette = calculate_color_palette(intersection_points, data['orientationColoring'], colors, data['reverseColors'])

data['grid'] = grid
data['intersectionPoints'] = intersection_points
data['tiles'] = color_palette

with open('data.json', 'w') as file:
    json.dump(data, file, indent=4)

print("Grid and tiles have been calculated and saved to 'grid.json' and 'tiles.json'")