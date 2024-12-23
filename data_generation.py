import math
import json
import random
from data_dict import base_data

data = base_data.copy()

def approx(value):
    return round(value * data['inverseEpsilon']) / data['inverseEpsilon']

def dist(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def normalize(points):
    num_pts = len(points)
    xbar = 0
    ybar = 0
    max_dist = 0

    # find longest diagonal
    for i in range(num_pts):
        xbar += points[i]['x']
        ybar += points[i]['y']
        for j in range(i, num_pts):
            d = dist(points[i]['x'], points[i]['y'], points[j]['x'], points[j]['y'])
            if d > max_dist:
                max_dist = d
    # calculate mean point
    xbar /= num_pts
    ybar /= num_pts

    # subtract mean and normalize based on length of longest diagonal
    normalized_points = [
        [50 * (point['x'] - xbar) / max_dist, 50 * (point['y'] - ybar) / max_dist]
        for point in points
    ]
    return normalized_points

# def convert_pts_2_str(points):
#     return ' '.join([f"{point[0] + 25},{point[1] + 25}" for point in points])

# def rgbToHex(r, g, b):
#       R = round(r)
#       G = round(g)
#       B = round(b)
#       return '#' + ((1 << 24) + (R << 16) + (G << 8) + B).toString(16).slice(1)



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

        pt['area'] = str(round(area * 1000) / 1000)
        pt['numVertices'] = len(angles)
        pt['angles'] = json.dumps(angles)
        pt['dualPts'] = dual_pts
        pt['mean'] = mean
    return pts

def calculate_colors(hue, hue_range, sat, contrast):
    lightness = 50

    start = [hue + hue_range, sat, lightness + contrast]
    end = [hue - hue_range, sat, lightness - contrast]
    return [start, end]


def calculate_tiles(pts, multiplier, epsilon=1e-10):
    for pt in pts.values():
        angles = [line['angle'] * multiplier for line in pt['lines']]
        angles += [(angle + math.pi) % (2 * math.pi) for angle in angles]
        angles = sorted(set(approx(angle, epsilon) for angle in angles))

        offset_pts = [{'x': pt['x'] + epsilon * -math.sin(angle), 'y': pt['y'] + epsilon * math.cos(angle)} for angle in angles]

        dual_pts = [{'x': (offset_pts[i]['x'] + offset_pts[(i + 1) % len(offset_pts)]['x']) / 2,
                     'y': (offset_pts[i]['y'] + offset_pts[(i + 1) % len(offset_pts)]['y']) / 2} for i in range(len(offset_pts))]

        pt['dualPts'] = dual_pts
        pt['mean'] = {'x': pt['x'], 'y': pt['y']}
        pt['area'] = sum(0.5 * (dual_pts[i]['x'] * dual_pts[(i + 1) % len(dual_pts)]['y'] - dual_pts[i]['y'] * dual_pts[(i + 1) % len(dual_pts)]['x']) for i in range(len(dual_pts)))
        pt['angles'] = angles

    return pts

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

# Save the results to files
with open('grid.json', 'w') as file:
    json.dump(grid, file, indent=4)

with open('data.json', 'w') as file:
    json.dump(data, file, indent=4)

# with open('tiles.json', 'w') as file:
#     json.dump(tiles, file, indent=4)

with open('intersection_points.json', 'w') as file:
    json.dump(intersection_points, file, indent=4)

print("Grid and tiles have been calculated and saved to 'grid.json' and 'tiles.json'")
