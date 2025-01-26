import py5_tools
py5_tools.add_jars('../jars')
import time
from YuSan_PY5_Toolscode import *
from the_control import *



def create_gird(sides, distance):
    global vector
    global gird
    distance = [distance for i in range(sides)]
    print(distance)
    pv = Tools2D()
    # 创建一个多边形,返回点集到vector
    vector = pv.regular_polygon(sides=sides, side_length=30)
    # 取vector的垂直向量vector_pen
    vector_pen = pv.vector_rotate(vector, 90)

    o_gird = Tools2D()
    for i in vector_pen:
        # 把vector_pen换成直线
        o_gird.vector_to_line(i, [200, 150])
    gird_0 = o_gird.get_line_dic()  #

    # 平移gird_0
    gird = Tools2D()
    for t, (letter, line_detail) in enumerate(gird_0.items()):
        direction_vector = vector[t]  # 平移方向为vector
        for i in range(0, 50):
            # 用vector_change_norm拉伸向量长度
            gird.line_shift(line_detail,
                            gird.vector_change_norm(direction_vector, distance[t] + 100 * i),
                            rewrite=False, drop=True)
            gird.line_shift(line_detail,
                            gird.vector_change_norm(direction_vector, distance[t] + 100 * -i),
                            rewrite=False, drop=True)


start_time = time.time()
create_gird(8,14)
end_time = time.time()
elapsed_time = end_time - start_time  # 计算耗时
print(f'耗时{round(elapsed_time * 1000,5)}毫秒')

def setup():
    py5.size(400,300)
    py5.frame_rate(144)
    slider()

def draw():
    back = slider_value()
    if back is not None:
        create_gird(8,back)
    py5.background(255)
    screen_draw_vector(vector,screen_axis(-50,-50))
    screen_draw_lines(gird.get_line_dic())
    fps()


def fps():
    now_fps = py5.get_frame_rate()  # 获取当前帧率
    py5.fill(0)  # 设置文本颜色为黑色
    py5.text(f"FPS: {now_fps:.2f}", 10, 30)  # 在屏幕上显示帧率


py5.run_sketch()

