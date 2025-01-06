import sys

import py5
import numpy as np
import time

# from altair import Theta
from py5 import text_size
import YuSan_PY5_Toolscode as YT
from YuSan_PY5_Toolscode import save_surface, surfacedic

TheTextsize = 22
start_time = time.time()

#互相垂直的两条直线关系是k2=-(1/k1)
#中点：(向量A+向量B)/2
#直线斜率：k=（y2-y1）/（x2-x1）
#def find_perpendicular(A,B):


def draw_tup_shape(pointtuple,drawnumber=True,nubersize=30):
    def convert_points_to_lines(inpointtuple):
        # 将点的列表转换为线段的列表
        lines = []
        for i in range(len(inpointtuple) - 1):  # 遍历相邻点
            x1, y1 = inpointtuple[i]
            x2, y2 = inpointtuple[i + 1]
            lines.append([x1, y1, x2, y2])
        return lines
    # py5.lines需要特殊输入格式【（x1,y1,x2,y2）,（x3,y3,x4,y4）】
    # 此函数是为了转换格式,可以将（x,y）(z，h)转换成一组连续的直线
    if pointtuple[0] != pointtuple[len(pointtuple) - 1]:
        print("输入的点集收尾不相接", "自动补充", "[", len(pointtuple) + 1, "]=", pointtuple[0])
        pointtuple.append(pointtuple[0])
        print(pointtuple)
    py5.lines(convert_points_to_lines(pointtuple))
    if drawnumber==True:
        nowsize = TheTextsize
        for i in range(len(pointtuple)):
            py5.fill(255, 0, 0)
            py5.text_size(nubersize)
            if i == 0:
                py5.text("," + str(i), pointtuple[i][0] + 22, pointtuple[i][1])
                continue
            py5.text(i, pointtuple[i][0], pointtuple[i][1])
        py5.text_size(nowsize)
        # 创建每个点的序号
#输入一组点坐标，此函数可以将这组坐标连线（形成收尾相接的曲线）



def creat_anybianxing(center=None,radio=None,ask_point=None,any=3):
    if not center and not ask_point and not radio:
        print("空参数无法计算")
        return ("err")
    if not center and not ask_point and radio:
        print("缺少center坐标，存在r，输出以原点为center的")
    if center and ask_point and not radio:
        if (len(ask_point)>1):
            print("存在多个point,需要验证是否满足条件")
            return ("err")
        else:
            print(ask_point)
            #dianji=
            print("dianji=",dianji)
            draw_tup_shape(dianji)
    if not center and ask_point and radio:
        print("存在point和radio，可以计算Center位置，若point数量≤2，会存在多个可能的Center")
#根据输入量创建多边形【center】中心点，radio半径（中心点到角的举例），【any】几边形

def setup():
    py5.size(800, 600)  # 设置窗口尺寸为 800x600 像素
    py5.background(240)  # 设置背景颜色为浅灰色
    py5.text_size(TheTextsize)
    YT.ceshi2()

    alatter = YT.droppoint_group_in_note(YT.get_everypoint((100, 100), (100, -100), 6))
    result = '-'.join(alatter)
    save_surface(result, floor=2)
    print(YT.SurfChain_to_HomoMatrix(list(surfacedic.keys())[0]))
    print(surfacedic)
    print (YT.HomoMatrix_to_local(YT.SurfChain_to_HomoMatrix(list(surfacedic.keys())[0])))
    py5.frame_rate(30) #设置帧率
def draw():
    YT.ceshi3()


    py5.translate(800 / 2, 600 / 2)
    py5.background(200,200,255,255)
    py5.fill(50, 100, 200)  # 设置文字颜色

    py5.stroke(0)  # 设置线条颜色为黑色
    py5.stroke_weight(2)  # 设置线条宽度为 2 像素
    #creat_anybianxing(((0, 0),), None, ((0, 200),),9)
    py5.point(0,0)
    py5.text("reg",0,0)
    py5.stroke(255, 0, 0,100)
    py5.lines([
        (400, 0, -400, 0),
        (0, 400, 0, -400)
    ])

    YT.draw_orgin_axes()
    #YT.ceshi2()

    #YT.screnn_drawlines_detail()
    YT.screen_draw()
    # 停止 draw 循环
    #py5.no_loop()
    #py5.loop()
    frame=py5.get_frame_rate()

    py5.fill(0)  # 设置文字颜色为黑色
    matrix = py5.get_matrix()
    # 提取当前原点位置
    origin_x = matrix[0][2]
    origin_y = matrix[1][2]
    py5.translate(-origin_x, -origin_y)
    py5.text_align(py5.LEFT)
    py5.text_align(py5.BOTTOM)
    py5.text(f'Frame Rate: {frame}', 10, 10)  # 显示帧速率

# 启动 py5 草图
py5.run_sketch()


'''
def 创建一组倾斜直线（度数，间隔，次数）
循环（次数）：
  y=tan(？度数)（x+b间隔*次数）
  把以上加入元组A
返回（元组A）

def 求交点（A,B）
  #A=k1x+g1b
  #B=k2x+g2b
  求X（k1x+g1b=k2x+g2b）
  以上加入元组X
  带入求Y（）
  以上加入元组Y
  循环(a，求上述元组项数)
    元组综合=append（元组X[a],元组Y[a]）
  返回（元组综合）

循环（N，5次）
  循环（K，平铺次数）
    创建一组倾斜直线(360/5*N，间隔*K)
    ALL=以上加入dic型

求交点（ALL）
求夹角（ALL）
加入元组（焦点，夹角）
取出夹角数列表即可
根据夹角列表的顺序 创建PENROSE形状网络
'''




