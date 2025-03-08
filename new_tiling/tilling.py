from new_tiling.BruijnsSystem import BruijnsSystem
from the_control import *
from PY5_2DToolkit import *
from BruijnsSystem import BruijnsSystem
import pandas as pd

def setup():
    py5.size(500, 500)
    s_v= sd.screen_axis(0,0)
    for seg_line in tilling_data:
        A_P,B_P=tool.point_shift(seg_line,s_v)
        tool.Segmentline_drop(A_P, B_P)
    load()
    slider('num1', [50, py5.height - 120], value=0, range_val=[0, 10],size=[400,30])
    slider('num2', [50, py5.height - 80], value=0, range_val=[0, 1000], size=[400, 30])
def draw():
    global  tilling_data
    s_v = sd.screen_axis(0, 0)
    py5.background(155)
    back = slider_value()
    if back is not None:
        tool.reset()
        tilling_data = till.create_tilling(the_p, num=back['num1']+back['num2'])
        for seg_line in tilling_data:
            A_P, B_P = tool.point_shift(seg_line, s_v)
            tool.Segmentline_drop(A_P, B_P,color=py5.color(0,0,0,90))

    sd.screen_draw_SegmentLine(tool.get_Segmentline_dic(),0)

if __name__ == "__main__":
    sd = Screen_draw(py5)
    tool = Tools2D()
    till = BruijnsSystem(sides=5, max_num_of_line=30)
    the_p = till.interaction_data_line_id[(0, 0)][60]
    print(f'选取交点:{the_p}')
    tilling_data = till.create_tilling(the_p, num=0)
    py5.run_sketch()
