import numpy as np
import py5
from conda.gateways.repodata import RepoInterface
from cytoolz import remove
from docutils.utils.math.latex2mathml import letters
import random
from collections import defaultdict

from fontTools.misc.cython import returns
from numba.core.cgutils import ifnot
from numba.cuda import local
from py5 import stroke, color, vertices
from pygments.lexer import words

pointdic={}
letterlist = [chr(i) for i in range(65, 91)]  # ASCII 65-90 对应 A-Z
nowletterlist=letterlist[:]
linedic={}
surfacedic={}
surface_drawed=[]


import numpy as np

class Matrix2D:
    def __init__(self):

            self.matrix = np.array(matrix)
            if self.matrix.shape[0] != 3:
                 raise ValueError("初始化错误：提供的矩阵必须是行数为(3)的二维矩阵")


    def apply_translation(self, tx, ty):
        """
        对当前矩阵应用平移变换。
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

def save_line (apletter,bpletter,floor=0,color=(0,0,0,255),strokeweight=3,visible=True):
    global linedic
    inf={}
    inf["location"]=list(pointdic[apletter])+list(pointdic[bpletter])
    inf["floor"] = floor
    inf["color"]=color
    inf["stroke_weight"] = strokeweight
    inf["visible"]=visible
    linedic[apletter+"-"+bpletter]=inf

def save_surface(chain_of_point,floor=0,color=(200,200,20,255),fill=False,stroke=None,stroke_color=(0,0,0)):
    global pointdic
    global surfacedic
    surf_pointgroup=[]
    alist_of_point=chain_of_point.split('-')
    for aletter in alist_of_point:
        point_xy=pointdic.get(aletter,0)
        if point_xy!=0:
            surf_pointgroup.append(point_xy)
        else:
            return "false:cant find point by letter"
    nowdic={}
    nowdic['floor']=floor
    nowdic['local']=surf_pointgroup
    nowdic['color']=py5.color(*color)
    nowdic['fill']=fill
    nowdic['stroke']=stroke
    nowdic['stroke_color']=py5.color(*stroke_color)
    surfacedic[chain_of_point]=nowdic
    return surf_pointgroup

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
    for key,value in linedic.items():
        pointlist.append(value["location"])
    py5.lines(np.array(pointlist,dtype=np.float32))
    #这里lines接收的是Np中的四维浮点数组[a b c d]
def screen_drawlines_detail(floor):
    for key, val in linedic.items():
        if val['floor']!=floor:
            continue
        if val['visible']==False:
            continue
        color=val['color']
        py5.stroke(py5.color(*color))
        strokeweigh=val['stroke_weight']
        py5.stroke_weight(strokeweigh)
        py5.line(*val['location'])
def screen_draw():
    for f in range(0,3):
        screen_draw_surface(f)
        screen_drawlines_detail(f)
def trans_chain_to_letterlist(chain):
    nodes = chain.split("-")  # 将链式结构分解为节点列表["A", "B", "C"]
    # 生成相邻对
    pairs = [(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)]
    # 加入首尾连接
    pairs.append((nodes[-1], nodes[0]))# 结果: [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A')]
    formatted_pairs = [f"{a}-{b}" for a, b in pairs]
    return formatted_pairs
#给定一个字符串A-B-C将它切割成[A,B][B,C][C,A]返回
def Local_to_Matrix(Chain):
    global surfacedic
    print(surfacedic[Chain]['local'])
    vertices = np.array(surfacedic[Chain]['local'])
    homogeneous_vertices = np.hstack([vertices, np.ones((vertices.shape[0], 1))])
    return homogeneous_vertices
#给定字符串表示 返回一个齐次坐标矩阵
def Matrix_to_local(matrix):
    cartesian_vertices = matrix[:, :-1]
    return cartesian_vertices
#给定矩阵 返回列表型np.array 非齐次坐标矩阵

def ceshi2():
    listceshi=[]
    for i in range(0,20000):
        listceshi.append([random.randint(-200,200),random.randint(-200,200)])
    back=droppoint_group_in_note(listceshi)
    for i in find_same_in_dic(pointdic,False):
        i=i[1:]
        removepoint_group(i)
def ceshi3():
    global linedic
    global pointdic
    linedic={}
    for i in range(50):
        save_line(random.choice(list(pointdic.keys())), random.choice(list(pointdic.keys())),
                  floor=random.randint(0,3),
                  color=tuple(np.random.randint(0, 200, size=3)),
                  strokeweight=random.randint(1,10))
    #print(pointdic)

def is_point_in_apolx(polx, P):
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

print(trans_chain_to_letterlist('A-B-C-D-E'))
#ceshi2()
print (pointdic)
#print(save_surface("A-C-D-E-M6-A7"))
#print(save_surface("D6-E2-M2-A1",color=(0,0,0)))
print(surfacedic)
print(is_point_in_apolx([[-100,0],[100,0],[0,100]],[0,100]))
#ceshi3()
#screen_drawlines()

# 示例

# 一个多边形外接圆圆心：所有顶点的平均值
#接下来

#把线条（函数直线）储存下来

#新的子程序：用函数（直线）把图形切割

#增加一个通过[x,y]创建线段的子程序：
#储存线段加一个判断，如果线段在【点集】中，使用字母，如果不在的话创建字母
#如果点 𝑃在四边形内部，则点𝑃对每条边的叉积结果的符号应该是相同的。
#为平面创建一个子平面来播放动画

#需求：
#将代码修改成 给定Fold symmetry，pattern，Disorder
#返回一个字典形 {形状A：[（x,y）,（z，h）][(a,b),(c,d)]，形状B:……}

'''    k=(y1-y2)/(x1-x2)
    b=y1-k*x1
    '''




