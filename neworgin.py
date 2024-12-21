import sys
import sympy as sym
import py5
import numpy as np
import time

from altair import Theta
from py5 import text_size

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

def get_nextpot(A,B,cosR):
        VeA = sym.Matrix([[A[0]], [A[1]]])  # 列向量
        VeB = sym.Matrix([[B[0]], [B[1]]])  # 列向量
        VeC = sym.Matrix([sym.symbols('x', real=True), sym.symbols('y', real=True)])  # 列向量 (x, y)
        R = (VeA - VeB).norm()
        print("R:",R.evalf())
        eq1 = sym.Eq((VeA - VeC).norm(), (VeA - VeB).norm())  # AB=AC=R
        eq2 = sym.Eq((VeA - VeC).dot(VeA - VeB), R * R * cosR)  # 向量点积公式：（A - C）dot(A - B) =∣AC∣*∣AB∣⋅cos(Angel)
        C = sym.solve([eq1, eq2], VeC)
        return (C)
#给定点A和B，AB,AC之间夹角cosR 求解C
#【准备拓展】：给定点A和B，存在一些可能的夹角（一组列表），求所有可能解
# for cosR in cosR_list:
#如果A,B不是四（多）边形临边而是对边的情况下↑↑↑↑无法求解

def get_everypoint(A,B,ang):
    jieguo = []
    jieguo.append(B)
    def cal_times(ang):
        times=(ang-1+2-1)//2
        return (times)
    times=cal_times(ang)
    print(ang,"角(边)形需要计算次数：",times)
    eachradio=2*np.pi/ang
    for i in range(1,cal_times(ang)+1):
        inputcosR=np.cos(eachradio*i)
        back=get_nextpot(A,B,inputcosR)
        jieguo.append(back[0])
        if len(back)!=1:
            jieguo.append(back[1])
        print("循环：",i,"计算结果：",back)
    def change_shunxu(alist):
        lennum = len(alist)
        ou = range(0, lennum, 2)
        ji = range(1, lennum, 2)
        ji = ji[::-1]
        linb = list(ou) + list(ji)
        print(linb)
        newlist = []
        for i in range(lennum):
            newlist.append(alist[linb[i]])
        print(newlist)
        return (newlist)
    reallist = change_shunxu(jieguo)
    return (reallist)
#↑通过给定【Center】：A，【AskPoint】：B，ang:【边数】
#返回一个列表型，这个ang边形的点集

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
            dianji=get_everypoint(center[0],ask_point[0],any)
            print("dianji=",dianji)
            draw_tup_shape(dianji)
    if not center and ask_point and radio:
        print("存在point和radio，可以计算Center位置，若point数量≤2，会存在多个可能的Center")
#根据输入量创建多边形【center】中心点，radio半径（中心点到角的举例），【any】几边形

def setup():
    py5.size(800, 600)  # 设置窗口尺寸为 800x600 像素
    py5.background(240)  # 设置背景颜色为浅灰色
    py5.text_size(TheTextsize)

def draw():
    py5.fill(50, 100, 200)  # 设置文字颜色
    py5.translate(800/2,600/2)
    py5.stroke(0)  # 设置线条颜色为黑色
    py5.stroke_weight(2)  # 设置线条宽度为 2 像素
    creat_anybianxing(((0, 0),), None, ((0, 200),),3)
    py5.point(0,0)
    py5.text("reg",0,0)
    py5.stroke(255, 0, 0,100)
    py5.lines([
        (400, 0, -400, 0),
        (0, 400, 0, -400)
    ])

    # 停止 draw 循环
    py5.no_loop()
    #py5.loop()


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




