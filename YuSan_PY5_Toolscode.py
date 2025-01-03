import numpy as np
import py5
import random
from collections import defaultdict
import sympy as sym
import math

from IPython.testing.decorators import skipif
from PyQt5.QtCore import center
from anyio import value
from conda.instructions import PRINT
from numba.core.ir import Raise
from numpy.matrixlib.defmatrix import matrix
from py5 import point

pointdic={}
letterlist = [chr(i) for i in range(65, 91)]  # ASCII 65-90 对应 A-Z
a_letterlist=[chr(i) for i in range(97, 123)]  # ASCII 范围 97 到 122
nowletterlist=letterlist[:]
SegmentLine_dic={}
surfacedic={}
surface_drawed=[]
line_dic={}
now_a_list=[]

class Matrix2D:
    def __init__(self, matrix=None):
        """
        初始化二维矩阵。
        参数：
        - matrix: 一个形状为 (3, N) 的二维矩阵。如果未提供，则初始化为单位矩阵。
        """
        if matrix is None:
            # 默认初始化为单位矩阵
            self.matrix = np.identity(3)
        else:
            # 转换为 NumPy 数组
            self.matrix = np.array(matrix)

            # 检查矩阵是否符合 (3, N) 的形状
            if len(self.matrix.shape) != 2 or self.matrix.shape[0] != 3:
                raise ValueError("初始化错误：提供的矩阵必须是形状为 (3, N) 的二维矩阵。")

    def apply_translation(self, tx, ty):
        """
        对当前矩阵应用平移变换。
        参数：
        - tx: x 方向的平移距离
        - ty: y 方向的平移距离
        """
        translation_matrix = np.array([
            [1, 0, tx],
            [0, 1, ty],
            [0, 0, 1]
        ])
        # 左乘平移矩阵
        self.matrix = translation_matrix @ self.matrix
        return self

    def apply_rotation(self, theta):
        """
        对当前矩阵应用旋转变换。
        参数：
        - theta: 旋转角度（以弧度为单位）
        """
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        rotation_matrix = np.array([
            [cos_theta, -sin_theta, 0],
            [sin_theta, cos_theta, 0],
            [0, 0, 1]
        ])
        # 左乘旋转矩阵
        self.matrix = rotation_matrix @ self.matrix
        return self

    def apply_scaling(self, sx, sy):
        """
        对当前矩阵应用缩放变换。
        参数：
        - sx: x 方向的缩放比例
        - sy: y 方向的缩放比例
        """
        scaling_matrix = np.array([
            [sx, 0, 0],
            [0, sy, 0],
            [0, 0, 1]
        ])
        # 左乘缩放矩阵
        self.matrix = scaling_matrix @ self.matrix
        return self

    def reset(self):
        """
        将矩阵重置为单位矩阵。
        """
        self.matrix = np.identity(3)
        return self

    def get_matrix(self):
        """
        返回当前矩阵。
        """
        return self.matrix

    def __repr__(self):
        """
        矩阵的字符串表示。
        """
        return f"Matrix2D(\n{self.matrix}\n)"

#================创建多边形操作================
def get_nextpot_bycos(A, B, cosR):
    VeA = sym.Matrix([[A[0]], [A[1]]])  # 列向量
    VeB = sym.Matrix([[B[0]], [B[1]]])  # 列向量
    VeC = sym.Matrix([sym.symbols('x', real=True), sym.symbols('y', real=True)])  # 列向量 (x, y)
    R = (VeA - VeB).norm()
    # print("R:", R.evalf())
    eq1 = sym.Eq((VeA - VeC).norm(), (VeA - VeB).norm())  # AB=AC=R
    eq2 = sym.Eq((VeA - VeC).dot(VeA - VeB), R * R * cosR)  # 向量点积公式：（A - C）dot(A - B) =∣AC∣*∣AB∣⋅cos(Angel)
    C = sym.solve([eq1, eq2], VeC)
    return (C)
# 给定点A和B，AB,AC之间夹角cosR 求解C
# 【准备拓展】：给定点A和B，存在一些可能的夹角（一组列表），求所有可能解
# for cosR in cosR_list:
# 如果A,B不是四（多）边形临边而是对边的情况下↑↑↑↑无法求解
def get_everypoint(A, B, ang):
    jieguo = []
    jieguo.append(B)

    def cal_times(ang):
        times = (ang - 1 + 2 - 1) // 2
        return (times)

    times = cal_times(ang)
    # print(ang, "角(边)形需要计算次数：", times)
    eachradio = 2 * np.pi / ang
    for i in range(1, cal_times(ang) + 1):
        inputcosR = np.cos(eachradio * i)
        back = get_nextpot_bycos(A, B, inputcosR)
        jieguo.append(back[0])
        if len(back) != 1:
            jieguo.append(back[1])
        # print("循环：", i, "计算结果：", back)

    def change_shunxu(alist):
        lennum = len(alist)
        ou = range(0, lennum, 2)
        ji = range(1, lennum, 2)
        ji = ji[::-1]
        linb = list(ou) + list(ji)
        # print(linb)
        newlist = []
        for i in range(lennum):
            newlist.append(alist[linb[i]])
        # print(newlist)
        return (newlist)

    reallist = change_shunxu(jieguo)
    return (reallist)
# ↑通过给定【Center】：A，【AskPoint】：B，ang:【边数】
# 返回一个列表型，这个ang边形的点集
#===========================================

#================创建易读坐标系================
def draw_orgin_axes(fangda=10,step=10,textstep=1,textsize=13,suojin=30):
    global fangdaxishu
    py5.push_matrix()
    matrix = py5.get_matrix()
    # 提取当前原点位置
    origin_x = matrix[0][2]
    origin_y = matrix[1][2]
    py5.translate(-origin_x,-origin_y)
    fangdaxishu = fangda
    tick_size = 5  # 刻度线长度
    lasttext = 0
    py5.text_size(textsize)
    Xzero=py5.width//2
    Yzero=py5.height//2
    Xmax=py5.width-suojin
    Xmin=0+suojin
    Ymax=0+suojin
    Ymin=py5.height-suojin
    global orgcenter
    orgcenter = [Xzero,Yzero]
    #绘制X轴
    py5.stroke(0)
    py5.stroke_weight(2)  # 线粗细
    py5.line(Xmin,Yzero,Xmax,Yzero)
    #绘制Y轴
    py5.stroke(0)
    py5.stroke_weight(2)  # 线粗细
    py5.line(Xzero,Ymin,Xzero,Ymax)
    #绘制X轴刻度和标注
    q=textstep*step//2
    for i in range(step, Xmax // 2, step):
        py5.stroke(0,0,0,100)
        py5.stroke_weight(2)  # 线粗细
        py5.fill(0,0,0,100)
        py5.text_align(py5.CENTER)
        py5.line(Xzero + i, Yzero, Xzero + i, Yzero - tick_size)
        py5.line(Xzero - i, Yzero, Xzero - i, Yzero - tick_size)
        if i == q+ textstep*step or i==q or textstep % 2 !=0:
            q = i
            if not (Xzero + i)-lasttext<=py5.text_width(str(-i//fangda)):
                py5.line(Xzero + i, Yzero, Xzero + i, Yzero - tick_size)
                py5.line(Xzero - i, Yzero, Xzero - i, Yzero - tick_size)
                py5.text(str(-i//fangda), Xzero - i, Yzero + tick_size + textsize // 2 + 2)
                py5.text(str(i//fangda), Xzero + i, Yzero + tick_size + textsize // 2 + 2)  # 添加数字标注
                lasttext = Xzero + i



    for i in range(step, Ymin // 2, step):  # 从中心点开始向两端绘制刻度

        py5.stroke(0, 0, 0, 100)
        py5.stroke_weight(2)  # 线粗细
        py5.fill(0, 0, 0, 100)
        py5.text_align(py5.RIGHT)

        py5.line(Xzero, Yzero - i, Xzero + tick_size, Yzero - i)
        py5.line(Xzero, Yzero + i, Xzero + tick_size, Yzero + i)
        panduanzhedang=abs((Yzero + tick_size + textsize // 2 + 2)-(Yzero + i + 5))
        #print(panduanzhedang)
        if panduanzhedang<= textsize//2:
            py5.text(str(i//fangda), Xzero - 5, Yzero - i + 5)
            continue
        py5.text(str(i//fangda), Xzero - 5, Yzero - i + 5)
        py5.text(str(-i//fangda), Xzero - 5, Yzero + i + 5)
    py5.pop_matrix()
#绘制一个坐标系【fangda】是放大比例，step是间隔多少绘制一个刻度，texttstep是间隔显示
#suojin是画面两边缩进不画线
def list_depth(lst):
            if not isinstance(lst, list):
                if not isinstance(lst, tuple):
                    # 如果当前不是列表，层数为 0
                    return 0
            if not lst:
                # 如果列表是空的，层数为 1（只有一层）
                return 1
            # 递归判断每个元素的嵌套深度，并取最大值
            return 1 + max(list_depth(item) for item in lst)
def tans_to_easyread (listxy):
    if list_depth(listxy)==1 and len(listxy)==2:
        newvecty =(orgcenter[1]-listxy[1])/ fangdaxishu
        newvectx=(listxy[0]-orgcenter[0])/fangdaxishu
        repoint = [newvectx,newvecty]
        return repoint
    else:
        print(listxy)
        raise ValueError("Data must be a list[x,y]")  # 抛出 ValueError 异常
def easyread_to_real():
    print()
#如果格式不会会报错
#===========================================

#================点线面存取操作================
#////////////《点操作》////////////
def removepoint_group(p_group):
    if list_depth(p_group) == 1:
        for i in p_group:

            removepoint_by_letter(i)
        return

    if list_depth(p_group)== 2:
        for i in p_group:
            removepoint_by_xy(i)
def removepoint_by_letter(aletter):
    global pointdic
    global nowletterlist

    if aletter not in pointdic:
        return "cant find point"
    del pointdic[aletter]

    # 初始化变量
    n = -1
    num = len(nowletterlist)  # 默认插入到最后
    number_aletter = int(aletter[1:] or 0) if len(aletter) > 1 else 0  # alletter 的数字部分，默认为 0
    # 遍历列表寻找插入点
    for i in nowletterlist:
        n += 1
        if i == None:
            break

        # 提取数字部分，若无数字部分则默认为 0
        number_i = int(i[1:] or 0)  # 当前元素的数字部分，默认为 0


        # 优先比较数字部分
        if number_i < number_aletter:  # 当前数字小于 alletter 的数字，继续循环
            continue
        elif number_i == number_aletter:  # 数字相同，比较字母部分
            if ord(i[0]) < ord(aletter[0]):  # 当前字母小于 alletter 的字母，继续循环
                continue
        # 如果当前数字大于 alletter 的数字，或者数字相同但字母大于 alletter 的字母，找到插入点
        num = n
        break

    # 修正 num 的值，确保插入点在列表范围内
    if len(nowletterlist) <= num:
        num = len(nowletterlist)  # 插入到末尾
    elif num < 0:
        num = 0  # 插入到开头

    # 插入元素
    nowletterlist.insert(num, aletter)
def removepoint_by_xy(listxy):
    global pointdic
    target_value = listxy
    # 找到所有键
    keys = [k for k, v in pointdic.items() if v == target_value]
    if keys != None:
        removepoint_by_letter(keys[-1])
    else:
        return ("mei zhao dao")
#如果找不到会有返回值
def droppoint_group_in_note(apointgroup):
    back=[]
    for i in apointgroup:
        if not isinstance(i,list):
            if not isinstance(i,tuple):
                ValueError("data is not list or tuple")
        if len(i)==2:
            back.append(droppoint_in_note(i))
        else:
            ValueError("data is not:([x,y],(x,y),(x,y))")
    return back
#如果成功会返回一个代号列表[A,B,C,D]
#如果格式不会会报错
def droppoint_in_note(apoint):
    global letterlist
    global nowletterlist
    global pointdic
    if len(nowletterlist)==0:
        if len(letterlist[-1])==1:
            moreletterlist=[f"{chr(i)}1" for i in range(65, 91)]
            letterlist=letterlist+moreletterlist
            nowletterlist=moreletterlist
        else:
            morenum=str(int(letterlist[-1][1:])+1)
            moreletterlist = [chr(i)+morenum for i in range(65, 91)]
            letterlist = letterlist + moreletterlist
            nowletterlist = moreletterlist
    if list_depth(apoint)==1 and len(apoint)==2:
        back = nowletterlist[0]
        pointdic[nowletterlist[0]] = apoint
        del nowletterlist[0]
        return back
    else:
        print (list_depth(apoint),len(apoint))

        raise ValueError("Data must be a list[x,y]or(x,y)")  # 抛出 ValueError 异常
#如果格式不会会报错
#成功返回一个字母代号

#////////////《线操作》////////////
def save_Segmentline_by_ABletter (Aletter, Bletter, floor=0, color=py5.color(0, 0, 0, 255), strokeweight=3, visible=True):
    global SegmentLine_dic
    inf={}
    inf["location"]=list(pointdic[Aletter])+list(pointdic[Bletter])
    inf["floor"] = floor
    inf["color"]=color
    inf["stroke_weight"] = strokeweight
    inf["visible"]=visible
    SegmentLine_dic[Aletter + "-" + Bletter]=inf
def save_Segmentline_by_ABpointxy(Apoint, Bpoint, floor=0, color=py5.color(0, 0, 0, 255), strokeweight=3, visible=True):
    Aletter = droppoint_in_note(Apoint)
    Bletter = droppoint_in_note(Bpoint)
    save_Segmentline_by_ABletter (Aletter, Bletter, floor, color, strokeweight, visible)
    return Aletter+"-"+Bletter
def remove_Segmentline(chain):
    del SegmentLine_dic[chain]
#有图层高度floor
def save_line(k,b,a=1):
    global line_dic
    detaildic = {}
    if a==0 and k==0:
        raise ValueError("a和k不能同时为0，请检查输入")
    if a==0:
        strline = f"x={b/-k}"
        detaildic['str']=strline
        detaildic['k'] = -1
        detaildic['b'] = b/-k
        detaildic['a'] = 0
    if k==0:
        strline = f"y={b}"
        detaildic['str'] = strline
        detaildic['k'] = 0
        detaildic['b'] = b
    if a==1 and k!=0:
        strline = f"y={k}x+{b}"
        detaildic['str'] = strline
        detaildic['k'] = k
        detaildic['b'] = b
    newletter= ask_a_new_letter()
    line_dic[newletter]=detaildic
    return newletter
#函数：ay=kx+b

def segmentline_to_line(chain):
    global pointdic
    Aletter,Bletter=chain.split('-')
    x1,x2=pointdic[Aletter][0],pointdic[Bletter][0]
    y1,y2=pointdic[Aletter][1],pointdic[Bletter][1]
    if x1==x2 and y1==y2:
        raise ValueError('is not a line,this is a point')
    if x1==x2:
       a=0
       b=x1
       k=-1
    else:
       a=1

    if y1==y2:
       k=0
       b=y1
    if x1!=x2 and y1!=y2:
       k = (y1 - y2) / (x1 - x2)
       b = y1 - k * x1
    str=save_line(k,b,a)
    print('segmentline_to_line:',str)
    return str
#返回一个代号letter

def solve_line(line_letter, x=None, y=None):
    if x==None and y==None:
        raise ValueError("x，y都没有输入值 无法计算")
    global line_dic
    detail_dic = line_dic[line_letter]
    if 'a' in detail_dic:
        the_a=detail_dic['a']
    else:
        the_a=1

    the_b,the_k=detail_dic['b'],detail_dic['k']
    if y==None:
        if the_a == 0:
            raise ValueError("无法计算，因为a=0时0y=kx+b 无法计算y")
        #计算y
        return  the_k*x+the_b
    if x == None:
        #计算x
        if the_k==0:
            raise ValueError("无法计算，因为k=0时y=0x+b 无法计算x")
        return (y-the_b)/the_k

def line_segment_intersection(Aline, Bline):
    """
    使用 numpy 计算两条线段的交点
    :param A1: 线段 A 的起点 (x1, y1)
    :param A2: 线段 A 的终点 (x2, y2)
    :param B1: 线段 B 的起点 (x3, y3)
    :param B2: 线段 B 的终点 (x4, y4)
    :return: 交点坐标 (x, y)，如果没有交点返回 None
    """
    x1, y1 = Aline[0]
    x2, y2 = Aline[1]
    x3, y3 = Bline[0]
    x4, y4 = Bline[1]

    # 创建系数矩阵 A@缩小量=b
    A = np.array([[x2 - x1, x3 - x4], [y2 - y1, y3 - y4]])
    b = np.array([x3 - x1, y3 - y1])

    # 计算行列式
    det = np.linalg.det(A)

    # 判断是否平行或共线
    if abs(det) < 1e-10:  # 行列式接近 0，表示两条线段平行或共线
        return None

    # 解线性方程组
    t, s = np.linalg.solve(A, b)

    # 判断参数 t 和 s 是否在 [0, 1] 范围内
    if 0 <= t <= 1 and 0 <= s <= 1:
        # 计算交点坐标
        intersection_x = x1 + t * (x2 - x1)
        intersection_y = y1 + t * (y2 - y1)
        return (intersection_x, intersection_y)

    return None  # 如果 t 或 s 不在范围内，则没有交点
#矩阵方法 查找两条线段交点，无交点返回None
def intersection_2_Segmentline(Aline_S, Bline_S):
    Ax1, Ay1 = Aline_S[0]
    Ax2, Ay2 = Aline_S[1]
    Bx1, By1 = Bline_S[0]
    Bx2, By2 = Bline_S[1]

    if Bx1 == Bx2 and By1==By2 and Ax1==Ax2 and Ay1==Ay2:
        #raise ValueError('输入了一个点')
        return Ax1,Ay1
    if Bx1 == Bx2 and By1==By2:
        #raise ValueError('B线是一个点')
        temp_chain = save_Segmentline_by_ABpointxy(Aline_S[0], Aline_S[1])
        temp_line_letter = segmentline_to_line(temp_chain)
        if By1 == solve_line(temp_line_letter, x=Bx1) and Bx1 == solve_line(temp_line_letter, y=By1):
            return Bx1, By1
        else:
            return None
    if Ax1==Ax2 and Ay1==Ay2:
        #raise ValueError('A线是一个点')
        temp_chain=save_Segmentline_by_ABpointxy(Bline_S[0],Bline_S[1])
        temp_line_letter=segmentline_to_line(temp_chain)
        if Ay1==solve_line(temp_line_letter,x=Ax1) and Ax1==solve_line(temp_line_letter, y=Ay1):
            return Ax1,Ay1
        else:
            return None



    print ('A:',Aline_S,'B:',Bline_S)
    # 检查线段投影范围是否重叠（快速排除法）
    rangeX = max(min(Ax1, Ax2), min(Bx1, Bx2)), min(max(Ax1, Ax2), max(Bx1, Bx2))
    rangeY = max(min(Ay1, Ay2), min(By1, By2)), min(max(Ay1, Ay2), max(By1, By2))
    if rangeX[0] > rangeX[1] or rangeY[0] > rangeY[1]:
        return None  # 没有重叠，线段不可能相交

    # 计算直线的斜率和截距
    if Ax1 == Ax2:  # 第一条线和y轴水平
        k_A, b_A = None, Ax1
    else:
        k_A = (Ay1 - Ay2) / (Ax1 - Ax2)
        b_A = Ay1 - k_A * Ax1
    if Bx1 == Bx2:  # 第二条线和y轴水平
        k_B, b_B = None, Bx1
    else:
        k_B = (By1 - By2) / (Bx1 - Bx2)
        b_B = By1 - k_B * Bx1



    # 检查是否平行
    if k_A is not None and k_B is not None:  # 两条线都不是垂直线
        if abs(k_A - k_B) < 1e-10:  # 斜率相等，平行，不可能有交点
            return None
        # 计算交点
        x = (b_B - b_A) / (k_A - k_B)
        y = k_A * x + b_A
    elif k_A is None:  # 第一条线垂直
        x = Ax1
        y = k_B * Ax1 + b_B
    elif k_B is None:  # 第二条线垂直
        x = b_B
        y = k_A * x + b_A

    # 检查交点是否在两条线段的范围内
    if rangeX[0] <= x <= rangeX[1] and rangeY[0] <= y <= rangeY[1]:
        return x, y
    else:
        return None  # 交点不在线段范围内
#经典方法 查找两条线段交点，无交点返回None

def intersection_line_Segmentline(line='a',segline_chain='A-B'):
    global pointdic
    global line_dic
    Aletter,Bletter=segline_chain.split('-')
    A=pointdic[Aletter]
    B=pointdic[Bletter]
    Ax,Ay=A
    Bx,By=B
    seg_rangeX, seg_rangeY = [min([Ax,Bx]),max([Ax,Bx])],[min([Ay,By]),max([Ay,By])]
    print(line_dic[line])

    #根据投影判断是否可能存在交点
    if not 'a' in line_dic[line]:
        if line_dic[line]['k']!=0:
            line_shadow_y1 = line_dic[line]['k'] * seg_rangeX[0] + line_dic[line]['b']
            line_shadow_y2 = line_dic[line]['k'] * seg_rangeX[1] + line_dic[line]['b']
            line_shadow_Rangey = [min([line_shadow_y1, line_shadow_y2]), max([line_shadow_y1, line_shadow_y2])]
            line_shadow_x1 = (seg_rangeY[0] - line_dic[line]['b']) / line_dic[line]['k']
            line_shadow_x2 = (seg_rangeY[1] - line_dic[line]['b']) / line_dic[line]['k']
            line_shadow_Rangex = [min([line_shadow_x1, line_shadow_x2]), max([line_shadow_x1, line_shadow_x2])]
            final_range_x = [max(line_shadow_Rangex[0], seg_rangeX[0]), min(line_shadow_Rangex[1], seg_rangeX[1])]
            final_range_y = [max(line_shadow_Rangey[0], seg_rangeY[0]), min(line_shadow_Rangey[1], seg_rangeY[1])]
            print('投影范围：', line_shadow_Rangex, line_shadow_Rangey)
            print(final_range_x, final_range_y)
            if final_range_x[0]>final_range_x[1] or final_range_y[0]>final_range_y[1]:
                #范围无效 不存在交点
                return None
            else:
                if final_range_x[0]==final_range_x[1] and final_range_y[0]==final_range_y[1]:
                    #raise ValueError('范围仅为一个点')
                    print('范围仅为一个点')
                    letter_theline=segmentline_to_line(segline_chain)
                    print(letter_theline)
                    if solve_line(letter_theline,x=final_range_x[0])==final_range_y[0]:
                        #如果把点的x坐标带入直线中，得到的y值刚好是点的y坐标

                        return [final_range_x[0],final_range_y[0]]
                    else:
                        return None
                temp_Ax,temp_Bx=final_range_x[0],final_range_x[1]
                temp_Ay=solve_line(line,x=temp_Ax)
                temp_By = solve_line(line, x=temp_Bx)
                temp_A,temp_B=[temp_Ax,temp_Ay],[temp_Bx,temp_By]
                inter_point=intersection_2_Segmentline([temp_A,temp_B], [A,B])
                return inter_point
        else:
            #k=0时候，y=b 只需要比较线段的y范围是否包含b
            if seg_rangeY[0]<=line_dic[line]['b']<=seg_rangeY[1]:
                value_y=line_dic[line]['b']
                the_line = segmentline_to_line(segline_chain)
                value_x = solve_line(the_line, y=value_y)
                return [value_x, value_y]
            else:
                return None
    else:
        if line_dic[line]['k']!=0:
            raise ValueError("a=0 且 k=0 ：输入的是一个点而不是线")
        #a=0时候,x=b/-k 是一条垂直线 只需要比较线段的x范围是否包含b/-k
        if seg_rangeY[0] <= line_dic[line]['b']/-line_dic[line]['k'] <= seg_rangeY[1]:
            value_x=line_dic[line]['b']/-line_dic[line]['k']
            the_line=segmentline_to_line(segline_chain)
            value_y=solve_line(the_line,x=value_x)
            return [value_x,value_y]
        else:
            return None


    print(A,B)
    print(seg_rangeX,seg_rangeY)



#////////////《面操作》////////////
def save_surface(chain_of_point,floor=0,color=py5.color(200,200,20,255),fill=False,stroke=None,stroke_color=py5.color(0,0,0)):
    global pointdic
    global surfacedic
    global SegmentLine_dic
    surf_pointgroup=[]
    alist_of_point=chain_of_point.split('-')
    for aletter in alist_of_point:
        point_xy=pointdic.get(aletter,0)
        if point_xy!=0:
            surf_pointgroup.append(point_xy)
        else:
            return "false:cant find point by letter"
    segmentlinegroup = trans_chain_to_pointletter_list(chain_of_point)
    for i in segmentlinegroup:
        #检查是否已经创建了线段 如果不存在就创建线段
        if i in SegmentLine_dic or i[::-1] in SegmentLine_dic:
            continue
        else:
            q=i.split('-')
            save_Segmentline_by_ABletter(q[0],q[1],visible=False)
    nowdic={}
    nowdic['floor']=floor
    all_x,all_y=0,0
    for x,y in surf_pointgroup:
        all_x,all_y=all_x+x,all_y+y
    center=[all_x/len(surf_pointgroup),all_y/len(surf_pointgroup)]
    nowdic['center']=center
    nowdic['local']=surf_pointgroup
    nowdic['color']=color
    nowdic['fill']=fill
    nowdic['stroke']=stroke
    nowdic['stroke_color']=stroke_color
    surfacedic[chain_of_point]=nowdic
    return surf_pointgroup
#【center】会自动生成在参数字典中：重心:是所有顶点坐标的平均值
def save_surface_by_pointlist(apointlist,floor=0,color=(200,200,20,255),fill=False,stroke=None,stroke_color=(0,0,0)):
    theletter=droppoint_group_in_note(apointlist)
    chain="-".join(theletter)
    save_surface(chain,floor,color,fill,stroke,stroke_color)

def split_surface_by_line(surface_chain, line_params):
   trans_chain_to_pointletter_list(surface_chain)


def is_point_in_surface(polx, P):
    """
       判断点 P 是否在 polx 中（包括在边上）
       polx: 多边形的顶点矩阵 [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
       P: 点的坐标 [x, y]
       return: 'inside' 如果点在内部, 'on_edge' 如果点在边上, 'outside' 如果点在外部
    """
    #应当检查符号chain，给定的四边形是否已经闭合，若已经闭合 不可以用下文的
    #polx[(i + 1) % len(polx)]
    #而应该改用
    #polx[i+1]
    def cross_product(A, B, P):
        # 计算叉积
        A = np.array(A)
        B = np.array(B)
        P = np.array(P)
        AB=B-A
        AP=P-A
        return np.cross(AB,AP)

    def is_point_on_segment(A, B, P):
        """
        判断点 P 是否在线段 AB 上
        :param A: 线段起点 [x1, y1]
        :param B: 线段终点 [x2, y2]
        :param P: 待检测点 [x, y]
        :return: True 如果 P 在线段 AB 上, 否则 False
        """
        # 叉积为 0 且点在线段范围内
        A = np.array(A)
        B = np.array(B)
        P = np.array(P)
        cross = cross_product(A, B, P)
        # 判断叉积是否为 0
        if abs(cross) > 1e-10:  # 允许微小误差
            return False
        # 判断是否在范围内
        dot_product = np.dot(P - A, B - A)  # 投影点是否在 A->B 的方向上
        squared_length = np.dot(B - A, B - A)  # AB 的平方长度
        return 0 <= dot_product <= squared_length

    # 检查每条边
    on_edge = False
    signs = []
    for i in range(len(polx)):
        A = polx[i]
        B = polx[(i + 1) % len(polx)]  # 四边形是闭合的
        if is_point_on_segment(A, B, P):  # 点在边上
            on_edge = True
        signs.append(cross_product(A, B, P))

    # 检查所有符号是否一致
    if all(s > 0 for s in signs) or all(s < 0 for s in signs):
        return 'inside' if not on_edge else 'on_edge'
    return 'on_edge' if on_edge else 'outside'
#返回值：'inside' 内部, 'on_edge' 点在多边形的边上, 'outside' 外部
#polx接受列表型 也接受非齐次坐标矩阵
def SurfChain_to_HomoMatrix(Chain):
    global surfacedic
    print(surfacedic[Chain]['local'])
    vertices = np.array(surfacedic[Chain]['local'])
    homogeneous_vertices = np.hstack([vertices, np.ones((vertices.shape[0], 1))])
    return homogeneous_vertices
#给定平面字符串表示 返回一个齐次坐标矩阵
def HomoMatrix_to_local(matrix):
    cartesian_vertices = matrix[:, :-1]
    return cartesian_vertices
#给定齐次坐标矩阵 返回非齐次坐标矩阵 列表型np.array

#////////////《常用操作》////////////
def ask_a_new_letter():
    global a_letterlist
    global now_a_list
    if len(a_letterlist) == 0:
        if len(now_a_list[-1])==1:
            # 此时小写字母后面还没有序号
            a_letterlist = [chr(i)+"1" for i in range(97, 123)]
        if len(now_a_list[-1])>1:
            # 此时存在序号，需要判断序号大小
            xuhao=int(now_a_list[-1][1:])+1
            a_letterlist = [chr(i) + str(xuhao) for i in range(97, 123)]
    thekey = a_letterlist.pop(0)
    now_a_list.append(thekey)

    return thekey
#从字母集中请求获得一个小写字母，并添加到当前已用集合中
def del_a_letter(aletter):
    global a_letterlist
    global now_a_list
    if aletter in now_a_list:
        Sure = True
        #计算我的num
        if len(aletter)==1:
            num=ord(aletter)-97+1
        if len(aletter)>1:
            num =(ord(aletter[0])-97+1)+int(aletter[1:])*26
        surenum=0
        thisnum = 0
        while Sure:
            if surenum >= len( a_letterlist):
                surenum=-1
                # print('超出范围 加入到最后')
                break
            if len( a_letterlist[surenum]) == 1:
                # print('没有序号，直接比较')
                thisnum=ord(a_letterlist[surenum])-97+1
                if thisnum>num:
                    break
            if len(a_letterlist[surenum]) > 1:
                # 存在序号
                thisnum=(ord(a_letterlist[surenum][0])-97+1)+int(a_letterlist[surenum][1:])*26
                if thisnum>num:
                    break
            surenum=surenum+1
        a_letterlist.insert(surenum, aletter)
        now_a_list.remove(aletter)
    else:
        return 'cant find the letter in : now_a_list'
#从当前已用集合中删除一个小写字母，放回字母集中
def point_to_line_distance(point, line_params):
    """
    计算点到直线的垂直距离
    :param point: 点的坐标 (x0, y0)
    :param line_params: 直线的参数 (a, b, c)，表示 ax + by + c = 0
    :return: 点到直线的垂直距离
    """
    x0, y0 = point
    a, b, c = line_params

    # 计算距离公式
    distance = abs(a * x0 + b * y0 + c) / math.sqrt(a ** 2 + b ** 2)
    return distance
#计算点到直线距离，返回一个数
def find_same_in_dic(d,seevaule=False):
    value_to_keys = defaultdict(list)
    for key, value in d.items():
        value_to_keys[tuple(value)].append(key)  # 将键分组到相同值的列表中
    # 创建一个字典value_to_keys，值作为键，键作为值（存储列表）
    if seevaule==False:
       duplicates = [keys for value, keys in value_to_keys.items() if len(keys) > 1]
       return duplicates
    duplicates = {value: keys for value, keys in value_to_keys.items() if len(keys) > 1}  # 只保留有重复的值
    return duplicates
#找到字典中相同的值，返回一个列表[[A,B,C],[D,E,F]]
#seevaule=True 返回{"[A,B,C]":[1,3],"[D,E]":[2,4]}
#d接受的参数是一个字典形
def check_same_pointdic_and_segmentlinedic():
    print()
def trans_chain_to_pointletter_list(chain):
    nodes = chain.split("-")  # 将链式结构分解为节点列表["A", "B", "C"]
    # 生成相邻对
    pairs = [(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)]
    # 加入首尾连接
    pairs.append((nodes[-1], nodes[0]))# 结果: [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A')]
    formatted_pairs = [f"{a}-{b}" for a, b in pairs]
    return formatted_pairs
#给定一个字符串A-B-C将它切割成[A-B][B-C][C-A]返回
#=========================================

#=============绘图渲染操作===================
def screen_draw_surface(floor):
    global surfacedic
    global surface_drawed
    allsurfacelist=surfacedic.keys()
    for sf in allsurfacelist:
        thedic = surfacedic[sf]
        if thedic['floor']!=floor:
            continue
        #=============读取位置信息（列表）===============
        weizhi = thedic['local']
        if not isinstance(weizhi, np.ndarray): #如果不是NP数组(矩阵)
            weizhi = np.array(weizhi,dtype=float)
        vertices = weizhi
        # ===========================================
        surface_drawed.append(sf)
        surface_drawed[-1] = py5.create_shape()

        surface_drawed[-1].begin_shape()
        surface_drawed[-1].fill(thedic['color'])
        if thedic['stroke'] == None:
            surface_drawed[-1].no_stroke()
        else:
            surface_drawed[-1].stroke(thedic['stroke_color'])
        if thedic['fill'] == False:
            surface_drawed[-1].no_fill()
        surface_drawed[-1].fill(thedic['color'])
        surface_drawed[-1].vertices(vertices)
        surface_drawed[-1].end_shape()
        py5.shape(surface_drawed[-1])
def screen_drawlines(color=0,strok_weight=2):
    py5.stroke(color)
    py5.stroke_weight(strok_weight)
    pointlist=[]
    for key,value in SegmentLine_dic.items():
        pointlist.append(value["location"])
    py5.lines(np.array(pointlist,dtype=np.float32))
    #这里lines接收的是Np中的四维浮点数组[a b c d]
def screen_drawlines_detail(floor):
    for key, val in SegmentLine_dic.items():
        if val['floor']!=floor:
            continue
        if val['visible']==False:
            continue
        color=val['color']
        py5.stroke(color)
        strokeweigh=val['stroke_weight']
        py5.stroke_weight(strokeweigh)
        py5.line(*val['location'])
def screen_draw():
    for f in range(0,3):
        screen_draw_surface(f)
        screen_drawlines_detail(f)

#=========================================


def ceshi2():
    listceshi=[]
    for i in range(0,2000):
        listceshi.append([random.randint(-200,200),random.randint(-200,200)])
    back=droppoint_group_in_note(listceshi)
    for i in find_same_in_dic(pointdic,False):
        i=i[1:]
        removepoint_group(i)
def ceshi3():
    global SegmentLine_dic
    global pointdic
    SegmentLine_dic={}
    for i in range(50):
        save_Segmentline_by_ABletter(random.choice(list(pointdic.keys())), random.choice(list(pointdic.keys())),
                                     floor=random.randint(0,3),
                                     color=tuple(np.random.randint(0, 200, size=3)),
                                     strokeweight=random.randint(1,10))
    #print(pointdic)

# save_Segmentline_by_ABpointxy([0,0],[200,200])
save_Segmentline_by_ABpointxy([150,310],[200,310])
save_line(2,10)
print(intersection_line_Segmentline ('a','A-B'))

#接下来



#如果点 𝑃在四边形内部，则点𝑃对每条边的叉积结果的符号应该是相同的。
#为平面创建一个子平面来播放动画

#split_surface_by_line（）是GPT生成的 应该修改使其符合规范（利用trans_chain_to_letterlist()和line_segment_intersection()）


#对平面进行仿射变换操作，其中旋转操作（以中心center为轴）

#应该制作查重优化机制 如果点重合 那么修改的不仅是点字典还要修改直线字典和面字典
# def check_same_pointdic_and_segmentlinedic():


#Pattern（图案、模式），Disorder（无序）
#Pattern1：百叶窗消失：以多边形任意一条边（比较长的）创造一组直线切割多边形 形成条纹状，切割距离可以与斐波那契数列成反比例



