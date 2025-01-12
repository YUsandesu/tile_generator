
import random
import numpy as np
from py5 import point_light, ENABLE_DEPTH_TEST, light_falloff

import YuSan_PY5_Toolscode as yt
import py5



def setup():
    # 设置窗口大小
    py5.size(800, 600,py5.P3D)  # 宽度 800，高度 600
    py5.background(0)  # 设置背景颜色为黑色
    for x in range (50,800,100):
        for y in range (50,600,100):
            fivepolx = yt.droppoint_group_in_note(yt.get_everypoint((x, y), (x - 30, y-30), 4))
            polx_chain = '-'.join(fivepolx)
            yt.save_surface(polx_chain)


def draw():
    py5.background(0)  # 设置黑色背景
    py5.ortho()
    py5.hint(py5.DISABLE_DEPTH_TEST)
    py5.directional_light(125,125,125,0,0,-1)
    # 设置点光源
    py5.point_light(255, 127, 0, 800 / 2, 600 / 2, -1000)
    py5.light_falloff(1, 0.1, 0)  # 调整光衰减

    B = py5.create_shape()

    B.begin_shape()
    B.fill(255, 255, 255)

    # 正面法向量
    B.normal(0, 0, 1)
    vertices = np.array([[0, 0, -50], [0, 600, -50], [800, 600, -50], [800, 0, -50]])
    for v in vertices:
        B.vertex(*v)

    # # 背面法向量（反向光照）
    # B.normal(0, 0, -1)
    # for v in reversed(vertices):  # 逆时针排列
    #     B.vertex(*v)

    B.end_shape(py5.CLOSE)
    py5.shape(B)

    yt.screen_draw()


# 启动 py5 应用程序
py5.run_sketch()