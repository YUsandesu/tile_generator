import py5
import math
from controlP5 import ControlP5, Slider

slider_dic={}
def load():
    global cp5
    cp5 = ControlP5(py5.get_current_sketch())
def slider(title,location=[50,150],value=50,range=[0,50]):
    global cp5
    global slider_dic

    cp5.addSlider(title) \
        .setPosition(location[0], location[1]) \
        .setSize(200, 20) \
        .setRange(range[0], range[1]) \
        .setValue(math.floor(value))
    slider_dic[title]=math.floor(value)

def slider_value():
    """
    如果发生改变slider_value字典
    反走返回None
    """
    global cp5
    global slider_dic
    for title,value in slider_dic.items():
        the_siled=cp5.getController(title)
        if the_siled is None:
            return None
        now_value = math.floor(the_siled.getValue())
        if slider_dic[title] != now_value:
            slider_dic[title] = now_value
            print(now_value)
            return slider_dic.copy()
    return None

