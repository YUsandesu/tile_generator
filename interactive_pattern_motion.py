import py5_tools
py5_tools.add_jars('./jars')
import py5
from controlP5 import ControlP5
import math
from data_dict import base_data
from data_generation import (
    calculate_offsets, multiplier, steps, spacing, 
    compute_grid, sin_cos_table, sin_cos_rotate, shift,
    calculate_intersection_points
)
import cv2
import numpy as np


def toggle_optical_flow():
    global optical_flow_active, camera_initialized, cap, old_gray, p0, mask
    global last_reset_time
    optical_flow_active = cp5.getController('optical_flow').getValue()
    
    if optical_flow_active and not camera_initialized:
        initialize_camera()
        last_reset_time = py5.millis()
    elif not optical_flow_active and camera_initialized:
        cleanup_camera()

def initialize_camera():
    global camera_initialized, cap, old_gray, p0, mask
    # Initialize camera and optical flow
    cap = cv2.VideoCapture(0)
    ret, old_frame = cap.read()
    if ret:
        old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
        
        # Parameters for ShiTomasi corner detection
        feature_params = {
            "maxCorners": 100,
            "qualityLevel": 0.3,
            "minDistance": 7,
            "blockSize": 7
        }
        
        # Parameters for lucas kanade optical flow
        global lk_params
        lk_params = {
            "winSize": (15, 15),
            "maxLevel": 2,
            "criteria": (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        }
        
        # Find initial corners
        p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)
        mask = np.zeros_like(old_frame)
        camera_initialized = True

def cleanup_camera():
    global camera_initialized, cap
    if camera_initialized:
        cap.release()
        camera_initialized = False

def reset_optical_flow():
    global last_reset_time
    cleanup_camera()
    initialize_camera()
    last_reset_time = py5.millis()

def update_pattern():
    """Update the pattern based on current control values"""
    global tile_positions, original_positions
    
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
    
    # Initialize velocities when pattern changes
    global tile_velocities
    tile_velocities.clear()
    for i in tile_positions:
        tile_velocities[i] = {'x': 0, 'y': 0}

def process_optical_flow():
    global old_gray, p0, mask, tile_positions, tile_velocities, last_motion_time, last_reset_time
    
    if not optical_flow_active or not camera_initialized:
        return
    
    # Check if we need to reset optical flow (every 5 seconds)
    current_time = py5.millis()
    if current_time - last_reset_time > 5000:
        reset_optical_flow()
        return
    
    ret, frame = cap.read()
    if ret:
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate optical flow
        p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
        
        if p1 is not None:
            # Create debug visualization
            debug_frame = frame.copy()
            
            good_new = p1[st==1]
            good_old = p0[st==1]
            
            # Draw the tracks
            for i, (new, old) in enumerate(zip(good_new, good_old)):
                a, b = new.ravel()
                c, d = old.ravel()
                # Draw line between old and new position
                cv2.line(debug_frame, (int(a), int(b)), (int(c), int(d)), (0, 255, 0), 2)
                # Draw current position
                cv2.circle(debug_frame, (int(a), int(b)), 3, (0, 0, 255), -1)
            
            # Show the debug window
            cv2.imshow('Optical Flow Debug', debug_frame)
            cv2.waitKey(1)
            
            # Calculate motion vectors for each tracked point
            motion_vectors = good_new - good_old
            any_significant_motion = False
            
            # Convert tile positions to screen coordinates
            scale_factor = min(py5.width / 2, (py5.height - 100) / 2) / (data['steps'] * 20)
            screen_positions = {}
            for i in tile_positions:
                screen_x = py5.width/2 + tile_positions[i]['x'] * data['spacing'] * scale_factor
                screen_y = (py5.height-100)/2 + tile_positions[i]['y'] * data['spacing'] * scale_factor
                screen_positions[i] = {'x': screen_x, 'y': screen_y}
            
            # Apply forces to tiles based on nearby motion
            dt = 1.0/60.0  # Assume 60fps for time step
            
            for i in tile_positions:
                max_force_x = 0
                max_force_y = 0
                
                # Find the closest motion vectors to this tile
                for j, (new, old) in enumerate(zip(good_new, good_old)):
                    # Get motion vector coordinates
                    px, py = new.ravel()
                    
                    # Calculate distance between motion point and tile
                    dx = px - screen_positions[i]['x']
                    dy = py - screen_positions[i]['y']
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    # Only apply force if motion is within influence radius (e.g., 100 pixels)
                    if distance < 100:
                        # Calculate influence based on distance (closer = stronger)
                        influence = 1.0 - (distance / 100.0)
                        
                        # Get motion vector
                        motion_x = motion_vectors[j][0]
                        motion_y = motion_vectors[j][1]
                        
                        # Update maximum force if this motion is stronger
                        force = math.sqrt(motion_x*motion_x + motion_y*motion_y) * influence
                        if force > math.sqrt(max_force_x*max_force_x + max_force_y*max_force_y):
                            max_force_x = motion_x * influence * 2.0  # Adjust multiplier as needed
                            max_force_y = motion_y * influence * 2.0
                
                if abs(max_force_x) > 0.1 or abs(max_force_y) > 0.1:
                    any_significant_motion = True
                
                # Spring force (Hooke's law: F = -kx)
                displacement_x = tile_positions[i]['x'] - original_positions[i]['x']
                displacement_y = tile_positions[i]['y'] - original_positions[i]['y']
                spring_force_x = -SPRING_K * displacement_x
                spring_force_y = -SPRING_K * displacement_y
                
                # Total force including damping (-cv)
                total_force_x = max_force_x + spring_force_x - DAMPING * tile_velocities[i]['x']
                total_force_y = max_force_y + spring_force_y - DAMPING * tile_velocities[i]['y']
                
                # Update velocity (F = ma -> a = F/m -> v = v + at)
                tile_velocities[i]['x'] += (total_force_x / MASS) * dt
                tile_velocities[i]['y'] += (total_force_y / MASS) * dt
                
                # Update position (x = x + vt)
                tile_positions[i]['x'] += tile_velocities[i]['x'] * dt
                tile_positions[i]['y'] += tile_velocities[i]['y'] * dt
            
            if any_significant_motion:
                last_motion_time = current_time
            
            # Update tracking
            old_gray = frame_gray.copy()
            p0 = good_new.reshape(-1, 1, 2)

def dispose():
    if camera_initialized:
        cap.release()
        cv2.destroyAllWindows()

def setup():
    global cp5, data, cap, old_gray, p0, mask, tile_positions, original_positions
    global optical_flow_active, camera_initialized
    global last_motion_time, last_reset_time
    global tile_velocities
    py5.size(1200, 900)
    
    # Initialize flags and timers
    optical_flow_active = False
    camera_initialized = False
    last_motion_time = 0
    last_reset_time = 0
    
    # Initialize data from base_data
    data = base_data.copy()
    data['width'] = py5.width
    data['height'] = py5.height - 100
    
    # Initialize position and velocity tracking
    tile_positions = {}
    original_positions = {}
    tile_velocities = {}
    
    # Spring and motion parameters
    global SPRING_K, DAMPING, MASS
    SPRING_K = 0.1  # Reduced from 0.5 to make spring looser
    DAMPING = 0.8   
    MASS = 1.0
    
    # Create control panel
    cp5 = ControlP5(py5.get_current_sketch())
    
    # Add controls at the bottom
    controls_y = py5.height - 80
    spacing_x = 180
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
    
    # Optical Flow Toggle
    (cp5.addToggle('optical_flow')
        .setPosition(current_x, controls_y)
        .setSize(50, 20)
        .setValue(False)
        .onChange(lambda e: toggle_optical_flow()))
    
    # Initial pattern generation
    update_pattern()

def draw():
    py5.background(51)
    
    # Process optical flow if active
    if optical_flow_active:
        process_optical_flow()
    
    # Draw tile view
    with py5.push_matrix():
        py5.translate(py5.width/2, (py5.height-100)/2)
        scale_factor = min(py5.width / 2, (py5.height - 100) / 2) / (data['steps'] * 20)
        py5.scale(scale_factor)
        
        sorted_points = sorted(
            data['intersectionPoints'].values(),
            key=lambda pt: math.sqrt(pt['x']**2 + pt['y']**2)
        )
        
        # Update position trackers if they don't match the current points
        if len(tile_positions) != len(sorted_points):
            tile_positions.clear()
            original_positions.clear()
            tile_velocities.clear()
            for i, pt in enumerate(sorted_points):
                center_x = sum(dp['x'] for dp in pt['dualPts']) / len(pt['dualPts'])
                center_y = sum(dp['y'] for dp in pt['dualPts']) / len(pt['dualPts'])
                tile_positions[i] = {'x': center_x, 'y': center_y}
                original_positions[i] = {'x': center_x, 'y': center_y}
                tile_velocities[i] = {'x': 0, 'y': 0}
        
        # Check if we need to return tiles to original positions
        current_time = py5.millis()
        should_return = (current_time - last_motion_time > 5000)  # 5 seconds
        
        for i, pt in enumerate(sorted_points):
            current_pos = tile_positions[i]
            
            # Return to original position if needed
            if should_return:
                tile_positions[i]['x'] = py5.lerp(current_pos['x'], original_positions[i]['x'], 0.1)
                tile_positions[i]['y'] = py5.lerp(current_pos['y'], original_positions[i]['y'], 0.1)
            
            # Calculate offset from original position
            offset_x = (current_pos['x'] - original_positions[i]['x']) * data['spacing']
            offset_y = (current_pos['y'] - original_positions[i]['y']) * data['spacing']
            
            # Draw tile outline with offset
            py5.fill(200, 200, 200, 100)
            py5.begin_shape()
            for dual_pt in pt['dualPts']:
                py5.vertex(
                    dual_pt['x'] * data['spacing'] + offset_x,
                    dual_pt['y'] * data['spacing'] + offset_y
                )
            py5.end_shape(py5.CLOSE)
            
            # Draw tile number
            py5.fill(255)
            py5.no_stroke()
            text_size = 12/scale_factor
            py5.text_size(text_size)
            py5.text_align(py5.CENTER, py5.CENTER)
            py5.text(str(i+1), 
                    current_pos['x'] * data['spacing'],
                    current_pos['y'] * data['spacing'])
    
    # Draw control area background
    py5.fill(40)
    py5.no_stroke()
    py5.rect(0, py5.height-100, py5.width, 100)

if __name__ == '__main__':
    py5.run_sketch() 