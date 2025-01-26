from YuSan_PY5_Toolscode import *
import py5

plox_vector=Tools2D()
vector = plox_vector.regular_polygon(sides=5,side_length=30)
o_gird = Tools2D()
vector_pen=o_gird.vector_rotate(vector,90)
#取向量的垂直向量vector_pen

for i in vector_pen:
    #把向量换成直线
    o_gird.vector_to_line(i,[200,150])
gird = Tools2D()
for t,(k,v) in enumerate(o_gird.get_line_dic().items()):
    now_vector=vector[t]
    for i in range(0,50):
        gird.line_shift(v, gird.vector_norm(now_vector, 100 * i))
        gird.line_shift(v, gird.vector_norm(now_vector, 100 * -i))


def setup():
    py5.size(400,300)
    py5.frame_rate(144)


def draw():
    py5.background(255)
    screen_draw_vector(vector,screen_axis(-50,-50))
    screen_draw_lines(gird.get_line_dic())
    py5.no_loop()

py5.run_sketch()
