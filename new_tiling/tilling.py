import BruijnsSystem
from the_control import *
from PY5_2DToolkit import *
import pandas as pd

def setup():
    py5.size(500, 500)
    start_location= sd.screen_axis(0,0)
    load()
    slider('num1', [50, py5.height - 120], value=0, range_val=[0, 10],size=[400,30])
    for k,v in tool.point_dic.items():
        tool.point_dic[k]=tool.point_shift(v,start_location)

def draw():
    global  tilling_data
    py5.background(155)
    back = slider_value()
    if back is not None:
        print('changed')
    sd.screen_draw_SegmentLine(tool.get_Segmentline_dic(),0)

if __name__ == "__main__":
    tool = Tools2D()
    a = BruijnsSystem.BruijnsSystem(shifted_distance=5)
    till = a.tilling
    seg_group = till.unique_tilling(till._center_point)

    for i in seg_group:
        tool.Segmentline_drop(i[0],i[1],color=py5.color(0,0,0,100))

    sd = Screen_draw(py5)
    py5.run_sketch()
