from YuSan_PY5_Toolscode import *
import py5
import math



def spilt_2pi(n):
    return 2*math.pi/n

def setup():
    py5.size(500,300)
    py5.frame_rate(144)
    b = gird.line_solve_general(k=k, x=screen_get_info()['center'][0], y=screen_get_info()['center'][1])['b']
    gird.line_drop(k=k, b=b)
    print(gird.get_line_dic())

def draw():
    py5.background(255)
    # screen_draw(3, Seglinedic=test_random_segline(10))
    screen_draw_lines(gird.get_line_dic())
    screen_print_fps()
    py5.point(screen_get_info()['center'][0],screen_get_info()['center'][1])

    py5.no_loop()


gird = Tools2D()
k = spilt_2pi(5)

# test_random_point(100,90,num=150)

py5.run_sketch()
