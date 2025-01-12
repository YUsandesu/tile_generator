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

class TileGenerator(py5.Sketch):
    def __init__(self):
        super().__init__()
        self.cp5 = None
        self.data = base_data.copy()
        self.tile_width = self.data['width']
        self.tile_height = int(0.9 * self.data['height'])
        self.controller_height = int(0.95 * self.data['height'])

        self.last_motion_time = 0
        self.last_reset_time = 0
        self.should_return = True
        self.tile_positions = {}
        self.original_positions = {}
        self.tile_velocities = {}
        self.SPRING_K = 0.1
        self.DAMPING = 0.8
        self.MASS = 1.0
        
        self.cap = None
        self.old_gray = None
        self.p0 = None
        self.mask = None
        self.optical_flow_active = False
        self.camera_initialized = False
        self.lk_params = {
            "winSize": (15, 15),
            "maxLevel": 2,
            "criteria": (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        }

    def toggle_optical_flow(self):
        self.optical_flow_active = self.cp5.getController('optical_flow').getValue()
        
        if self.optical_flow_active and not self.camera_initialized:
            self.initialize_camera()
            self.last_reset_time = self.millis()
        elif not self.optical_flow_active and self.camera_initialized:
            self.cleanup_camera()

    def initialize_camera(self):
        # Initialize camera and optical flow
        self.cap = cv2.VideoCapture(0)
        ret, old_frame = self.cap.read()
        if ret:
            self.old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
            
            # Parameters for ShiTomasi corner detection
            feature_params = {
                "maxCorners": 100,
                "qualityLevel": 0.3,
                "minDistance": 7,
                "blockSize": 7
            }
            
            # Find initial corners
            self.p0 = cv2.goodFeaturesToTrack(self.old_gray, mask=None, **feature_params)
            self.mask = np.zeros_like(old_frame)
            self.camera_initialized = True

    def cleanup_camera(self):
        if self.camera_initialized:
            self.cap.release()
            self.camera_initialized = False

    def reset_optical_flow(self):
        self.cleanup_camera()
        self.initialize_camera()
        self.last_reset_time = self.millis()

    def update_pattern(self):
        self.tile_velocities.clear()
        for i in self.tile_positions:
            self.tile_velocities[i] = {'x': 0, 'y': 0}
            
        self.data['symmetry'] = int(self.cp5.getController('symmetry').getValue())
        self.data['radius'] = self.cp5.getController('radius').getValue()
        self.data['pattern'] = self.cp5.getController('pattern').getValue()
        self.data['disorder'] = self.cp5.getController('disorder').getValue()
        self.data['zoom'] = self.cp5.getController('zoom').getValue()
    
        # Calculate pattern data
        self.data['steps'] = steps(self.data['radius'], self.data['symmetry'])
        self.data['spacing'] = spacing(self.data['zoom'], self.data['width'], self.data['height'], self.data['steps'])
        self.data['multiplier'] = multiplier(self.data['symmetry'])
        
        self.sin_cos_table_val = sin_cos_table(self.data['symmetry'], self.data['multiplier'])
        self.sin_cos_rotate_val = sin_cos_rotate(self.data['rotate'])
        self.shift_val = shift(self.sin_cos_table_val, self.sin_cos_rotate_val)
        self.data['offsets'] = calculate_offsets(
            self.data['symmetry'], self.data['pattern'], self.data['disorder'], 
            self.data['randomSeed'], self.data['pan'], self.data['steps'], self.shift_val
        )
        
        # Calculate grid and intersections
        grid = compute_grid(self.data['symmetry'], self.data['steps'], self.data['offsets'])
        self.data['grid'] = grid
        self.data['intersectionPoints'] = calculate_intersection_points(self.data, grid, self.sin_cos_table_val)

    def process_optical_flow(self):
        if not self.optical_flow_active or not self.camera_initialized:
            return
        
        if self.should_return:
            self.reset_optical_flow()
            return
        
        ret, frame = self.cap.read()
        if ret:
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            p1, st, err = cv2.calcOpticalFlowPyrLK(self.old_gray, frame_gray, self.p0, None, **self.lk_params)
            if p1 is not None:
                # Create debug visualization
                # debug_frame = frame.copy()
                
                good_new = p1[st==1]
                good_old = self.p0[st==1]
                
                # Draw the tracks
                # for i, (new, old) in enumerate(zip(good_new, good_old)):
                #     a, b = new.ravel()
                #     c, d = old.ravel()
                #     # Draw line between old and new position
                #     cv2.line(debug_frame, (int(a), int(b)), (int(c), int(d)), (0, 255, 0), 2)
                #     # Draw current position
                #     cv2.circle(debug_frame, (int(a), int(b)), 3, (0, 0, 255), -1)
                
                # # Show the debug window
                # cv2.imshow('Optical Flow Debug', debug_frame)
                # cv2.waitKey(1)
                
                # Calculate motion vectors for each tracked point
                motion_vectors = good_new - good_old
                any_significant_motion = False
                
                # Convert tile positions to screen coordinates
                screen_positions = {}
                for i in self.tile_positions:
                    screen_x = self.width/2 + self.tile_positions[i]['x'] * self.data['spacing'] * self.scale_factor
                    screen_y = (self.height-100)/2 + self.tile_positions[i]['y'] * self.data['spacing'] * self.scale_factor
                    screen_positions[i] = {'x': screen_x, 'y': screen_y}
                
                # Apply forces to tiles based on nearby motion
                dt = 1.0/60.0  # Assume 60fps for time step
                
                for i in self.tile_positions:
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
                    displacement_x = self.tile_positions[i]['x'] - self.original_positions[i]['x']
                    displacement_y = self.tile_positions[i]['y'] - self.original_positions[i]['y']
                    spring_force_x = -self.SPRING_K * displacement_x
                    spring_force_y = -self.SPRING_K * displacement_y
                    
                    # Total force including damping (-cv)
                    total_force_x = max_force_x + spring_force_x - self.DAMPING * self.tile_velocities[i]['x']
                    total_force_y = max_force_y + spring_force_y - self.DAMPING * self.tile_velocities[i]['y']
                    
                    # Update velocity (F = ma -> a = F/m -> v = v + at)
                    self.tile_velocities[i]['x'] += (total_force_x / self.MASS) * dt
                    self.tile_velocities[i]['y'] += (total_force_y / self.MASS) * dt
                    
                    # Update position (x = x + vt)
                    self.tile_positions[i]['x'] += self.tile_velocities[i]['x'] * dt
                    self.tile_positions[i]['y'] += self.tile_velocities[i]['y'] * dt
                
                if any_significant_motion:
                    self.last_motion_time = self.millis()
                
                # Update tracking
                self.old_gray = frame_gray.copy()
                self.p0 = good_new.reshape(-1, 1, 2)

    def dispose(self):
        if self.camera_initialized:
            self.cap.release()
            cv2.destroyAllWindows()

    def settings(self):
        self.size(self.tile_width, self.data['height'])
        
    def setup(self):
        self.cp5 = ControlP5(self)
        controls_y = self.controller_height
        spacing_x = int(self.tile_width / 6)  # 6 controls
        current_x = 20
        
        slider_format = lambda name, min_val, max_val, decimal_place: (
            self.cp5.addSlider(name)
                .setPosition(current_x, controls_y)
                .setSize(150, 30)
                .setRange(min_val, max_val)
                .setValue(self.data[name])
                .setDecimalPrecision(decimal_place)
                .onChange(lambda _: self.update_pattern())
        )
        
        # Symmetry slider
        slider_format("symmetry", 3, 15, 0)
        current_x += spacing_x
        # Radius slider
        slider_format("radius", 30, 80, 2)
        current_x += spacing_x
        # Pattern slider
        slider_format("pattern", 0.0, 0.9, 2)
        current_x += spacing_x
        # Disorder slider
        slider_format("disorder", 0.0, 1.0, 2)
        current_x += spacing_x
        # Zoom slider
        slider_format("zoom", 0.1, 2.0, 2)
        current_x += spacing_x
        # Optical Flow Toggle
        (
            self.cp5.addToggle('optical_flow')
                .setPosition(current_x, controls_y)
                .setSize(30, 30)
                .setValue(False)
                .onChange(lambda _: self.toggle_optical_flow())
        )
        
        # Initial pattern generation
        self.update_pattern()

    def draw(self):
        self.background('#004477')
        width, height = self.data['width'], self.data['height']
        
        if self.optical_flow_active:
            self.process_optical_flow()
        
        # Draw tile view
        with self.push_matrix():
            self.translate(width / 2, height / 2)
            self.scale_factor = min(width / 2, height / 2) / (self.data['steps'] * 20)
            self.scale(self.scale_factor)
            
            sorted_points = sorted(
                self.data['intersectionPoints'].values(),
                key=lambda pt: math.sqrt(pt['x']**2 + pt['y']**2)
            )
            # Update position trackers if they don't match the current points
            if len(self.tile_positions) != len(sorted_points):
                self.tile_positions.clear()
                self.original_positions.clear()
                self.tile_velocities.clear()
                for i, pt in enumerate(sorted_points):
                    center_x = sum(dp['x'] for dp in pt['dualPts']) / len(pt['dualPts'])
                    center_y = sum(dp['y'] for dp in pt['dualPts']) / len(pt['dualPts'])
                    self.tile_positions[i] = {'x': center_x, 'y': center_y}
                    self.original_positions[i] = {'x': center_x, 'y': center_y}
                    self.tile_velocities[i] = {'x': 0, 'y': 0}
            
            # Check if we need to return tiles to original positions
            self.should_return = self.millis() - self.last_motion_time > 5000  # 5 seconds
            for i, pt in enumerate(sorted_points):
                current_pos = self.tile_positions[i]
                
                # Return to original position if needed
                if self.should_return:
                    self.tile_positions[i]['x'] = self.lerp(current_pos['x'], self.original_positions[i]['x'], 0.1)
                    self.tile_positions[i]['y'] = self.lerp(current_pos['y'], self.original_positions[i]['y'], 0.1)
                
                # Calculate offset from original position
                offset_x = (current_pos['x'] - self.original_positions[i]['x']) * self.data['spacing']
                offset_y = (current_pos['y'] - self.original_positions[i]['y']) * self.data['spacing']
                
                # Draw tile outline with offset
                self.fill(200, 200, 200, 100)
                self.begin_shape()
                for dual_pt in pt['dualPts']:
                    self.vertex(
                        dual_pt['x'] * self.data['spacing'] + offset_x,
                        dual_pt['y'] * self.data['spacing'] + offset_y
                    )
                self.end_shape(self.CLOSE)
                
                # Draw tile number
                self.stroke_weight(1.5)
                self.stroke(125, 125, 125)
                self.fill(255)
                self.text_size(16 / self.scale_factor)
                self.text_align(self.CENTER, self.CENTER)
                self.text(
                    str(i + 1), 
                    current_pos['x'] * self.data['spacing'],
                    current_pos['y'] * self.data['spacing']
                )
        
        # Draw control area background
        self.fill(40)
        self.no_stroke()
        self.rect(0, int(0.93 * self.height), width, 100)


if __name__ == '__main__':
    TileGenerator().run_sketch() 