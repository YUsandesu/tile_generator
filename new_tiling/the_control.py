import py5
from controlP5 import ControlP5, Slider

slider_value:int

def slider():
    global cp5
    cp5 = ControlP5(py5.get_current_sketch())
    cp5.addSlider("slider_value") \
        .setPosition(50, 150) \
        .setSize(200, 20) \
        .setRange(0, 100) \
        .setValue(50)
def slider_value():
    global cp5
    global slider_value
    now_value = round(cp5.getController('slider_value').getValue())
    if slider_value!=now_value:
        slider_value=now_value
        print(now_value)
        return  now_value
    return None

