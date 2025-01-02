import YuSan_PY5_Toolscode as yt
import py5

def setup():
    # 设置窗口大小
    py5.size(800, 600)  # 宽度 800，高度 600
    py5.background(255)  # 设置背景颜色为白色
    fivepolx=yt.droppoint_group_in_note(yt.get_everypoint((800/2,600/2),(600,600/2),5))
    yt.save_surface('-'.join(fivepolx))
    print(yt.surfacedic)
    print(yt.SegmentLine_dic.keys())

def draw():
    yt.screen_draw()

# 启动 py5 应用程序
py5.run_sketch()