import random
import py5

# Global variables
player_x = 400
player_y = 300
player_radius = 25
squares = []
score = 0

def setup():
    py5.size(800, 600)
    py5.background(255)
    py5.no_stroke()
    py5.fill(0, 0, 0)  # Black fill for squares

def draw():
    global score
    py5.background(255)
    
    # Draw and move player (circle)
    player_x, player_y = py5.mouse_x, py5.mouse_y
    py5.fill(0, 0, 255)
    py5.ellipse(player_x, player_y, player_radius * 2, player_radius * 2)
    
    # Create and move squares
    if py5.frame_count % 60 == 0:  # Create a square every second
        squares.append([random.randint(0, py5.width), 0, 20, 20])
    
    for square in squares:
        square[1] += 5  # Move square down
        py5.rect(square[0], square[1], square[2], square[3])
        
        # Collision detection
        if (player_x - player_radius < square[0] < player_x + player_radius and
            player_y - player_radius < square[1] < player_y + player_radius):
            squares.remove(square)
            score += 1
            
    # Display score
    py5.fill(0)
    py5.text_size(32)
    py5.text(f"Score: {score}", 10, 30)

def key_pressed():
    # Reset game
    global squares, score
    if py5.key == 'r':
        squares = []
        score = 0

py5.run_sketch()