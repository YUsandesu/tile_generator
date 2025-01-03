
import random
import YuSan_PY5_Toolscode as yt
import py5



def setup():
    # 设置窗口大小
    py5.size(800, 600)  # 宽度 800，高度 600
    py5.background(255)  # 设置背景颜色为白色
    for x in range (50,800,100):
        for y in range (50,600,100):
            fivepolx = yt.droppoint_group_in_note(yt.get_everypoint((x, y), (x - 30, y-30), 4))
            polx_chain = '-'.join(fivepolx)
            yt.save_surface(polx_chain)

def draw():
    py5.background(255)  # 设置背景颜色为白色
    yt.screen_draw()

# 启动 py5 应用程序
py5.run_sketch()