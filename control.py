import py5_tools
py5_tools.add_jars('./jars')
import py5
from controlP5 import ControlP5

def setup():
    py5.size(400, 400)
    # Import the ControlP5 library
    global controlP5
    cp5 = ControlP5(py5.get_current_sketch())

    # Add a button
    cp5.addButton("click_me") \
             .setPosition(50, 50) \
             .setSize(100, 40) \
             .setLabel("Click Me!")

    # Add a slider
    cp5.addSlider("slider_value") \
             .setPosition(50, 150) \
             .setSize(200, 20) \
             .setRange(0, 100) \
             .setValue(50)

def draw():
    py5.background(200)

# Define event methods for GUI components
def click_me():
    print("Button clicked!")

def slider_value(val):
    print(f"Slider value: {val}")

py5.run_sketch()
