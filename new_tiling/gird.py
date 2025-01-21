from YuSan_PY5_Toolscode import *
import py5
import math



def spilt_2pi(n):
    return 2*math.pi/n

def setup():
    py5.size(400,300)
    py5.frame_rate(144)

def draw():
    py5.background(255)
    screen_draw(3, Seglinedic=test_random_segline(10))
    screen_print_fps()

gird = Tools2D()
b= screen_axis(0,0)[1]
gird.line_drop(k=math.tan(spilt_2pi(5)),b=b)
print(gird.get_line_dic())

py5.run_sketch()