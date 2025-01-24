import py5_tools
py5_tools.add_jars('./jars')
import py5
from controlP5 import ControlP5, Slider
import math
import hsluv
from data_dict import base_data
from data_generation import (
    calculate_offsets, multiplier, steps, spacing, 
    compute_grid, sin_cos_table, sin_cos_rotate, shift,
    calculate_intersection_points, calculate_colors,
    calculate_color_palette
)
import json
import pygame

pygame.mixer.init()
pygame.mixer.music.load('ai_pipeline/music.mid')

def setup():
    global cp5, data
    py5.size(1200, 900)  # Reduced width since we only have tile view
    
    # Initialize data from base_data
    data = base_data.copy()
    data['width'] = py5.width
    data['height'] = py5.height - 100  # Reserve space for controls
    
    # Create control panel
    cp5 = ControlP5(py5.get_current_sketch())
    
    # Add controls at the bottom
    controls_y = py5.height - 80
    spacing_x = 180  # Horizontal spacing between controls
    current_x = 20
    
    # Symmetry slider
    (cp5.addSlider('symmetry')
        .setPosition(current_x, controls_y)
        .setSize(150, 20)
        .setRange(3, 12)
        .setValue(data['symmetry'])
        .onChange(lambda e: update_pattern()))
    current_x += spacing_x
    
    # Radius slider
    (cp5.addSlider('radius')
        .setPosition(current_x, controls_y)
        .setSize(150, 20)
        .setRange(10, 150)
        .setValue(data['radius'])
        .onChange(lambda e: update_pattern()))
    current_x += spacing_x
    
    # Pattern slider
    (cp5.addSlider('pattern')
        .setPosition(current_x, controls_y)
        .setSize(150, 20)
        .setRange(0, 1)
        .setValue(data['pattern'])
        .onChange(lambda e: update_pattern()))
    current_x += spacing_x
    
    # Disorder slider
    (cp5.addSlider('disorder')
        .setPosition(current_x, controls_y)
        .setSize(150, 20)
        .setRange(0, 1)
        .setValue(data['disorder'])
        .onChange(lambda e: update_pattern()))
    current_x += spacing_x
    
    # Zoom slider
    (cp5.addSlider('zoom')
        .setPosition(current_x, controls_y)
        .setSize(150, 20)
        .setRange(0.1, 2)
        .setValue(data['zoom'])
        .onChange(lambda e: update_pattern()))
    current_x += spacing_x
    
    # Initial pattern generation
    update_pattern()
    pygame.mixer.music.play()

def update_pattern():
    """Update the pattern based on current control values"""
    # Update data from controls
    data['symmetry'] = int(cp5.getController('symmetry').getValue())
    data['radius'] = cp5.getController('radius').getValue()
    data['pattern'] = cp5.getController('pattern').getValue()
    data['disorder'] = cp5.getController('disorder').getValue()
    data['zoom'] = cp5.getController('zoom').getValue()
    
    # Calculate pattern data
    data['steps'] = steps(data['radius'], data['symmetry'])
    data['spacing'] = spacing(data['zoom'], data['width'], data['height'], data['steps'])
    data['multiplier'] = multiplier(data['symmetry'])
    
    sin_cos_table_val = sin_cos_table(data['symmetry'], data['multiplier'])
    sin_cos_rotate_val = sin_cos_rotate(data['rotate'])
    shift_val = shift(sin_cos_table_val, sin_cos_rotate_val)
    data['offsets'] = calculate_offsets(
        data['symmetry'], data['pattern'], data['disorder'], 
        data['randomSeed'], data['pan'], data['steps'], shift_val
    )
    
    # Calculate grid and intersections
    grid = compute_grid(data['symmetry'], data['steps'], data['offsets'])
    data['grid'] = grid
    data['intersectionPoints'] = calculate_intersection_points(data, grid, sin_cos_table_val)

def draw():
    py5.background(51)
    
    # Draw tile view
    with py5.push_matrix():
        # Center and scale the tiles
        py5.translate(py5.width/2, (py5.height-100)/2)  # Account for control space
        
        # Reduce the scale factor to make pattern smaller
        scale_factor = min(py5.width / 2, (py5.height - 100) / 2) / (data['steps'] * 20)
        py5.scale(scale_factor)
        
        # Draw numbered tiles
        py5.stroke(255)
        py5.stroke_weight(1/scale_factor)
        
        # Sort intersection points by distance from center for consistent numbering
        sorted_points = sorted(
            data['intersectionPoints'].values(),
            key=lambda pt: math.sqrt(pt['x']**2 + pt['y']**2) # condition: add circle around center
        )
        tile_dict = {}
        
        for i, pt in enumerate(sorted_points):
            # Calculate center of the tile
            center_x = sum(dp['x'] for dp in pt['dualPts']) / len(pt['dualPts'])
            center_y = sum(dp['y'] for dp in pt['dualPts']) / len(pt['dualPts'])
            point_list = []
            # Draw tile outline
            py5.fill(200, 200, 200, 100)  # Light gray semi-transparent fill
            py5.begin_shape()
            for dual_pt in pt['dualPts']:
                point = (
                    dual_pt['x'] * data['spacing'],
                    dual_pt['y'] * data['spacing']
                )
                py5.vertex(*point)
                point_list.append(point)
            py5.end_shape(py5.CLOSE)
            
            # Draw tile number
            py5.fill(255)
            py5.no_stroke()
            # Scale text size with the inverse of scale_factor
            text_size = 12/scale_factor
            py5.text_size(text_size)
            py5.text_align(py5.CENTER, py5.CENTER)
            # Draw number at the calculated center of the tile
            py5.text(str(i+1), 
                    center_x * data['spacing'], 
                    center_y * data['spacing'])
            tile_dict[str(i+1)] = point_list
    
    # Draw control area background
    py5.fill(40)
    py5.no_stroke()
    py5.rect(0, py5.height-100, py5.width, 100)
    
    with open('tile_result.json', 'w') as file:
        json.dump(tile_dict, file, indent=4)

py5.run_sketch() 