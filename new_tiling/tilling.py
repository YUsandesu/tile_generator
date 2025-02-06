import gird
import py5
import json
from YuSan_PY5_Toolscode import *

#TODO 这里需要将gird返回的字典 对应找到焦点

#TODO 根据gird的字典头，创建tilling拼块
#具体方法：
#+++++奇数+++++
#sym=5时 会有10条向量 若原始向量为A B C D E
#那么：存在-A -B -C -D -E 方向和原始向量相反
#最终排列顺序：A -D  B -E  C -A  D -B  E  -C
#           1  2  3  4  5  6  7  8  9  10
#360/10=[36] --> 180/36=[5] -->5+1=6 所以第六位是A
#+++++偶数+++++
#sym=6时 原始向量已经存在互相相反的向量了，所有只有6条向量
#A B C D E F
#1 2 3 4 5 6
#360/6=60 180/60=3 3+1=4 -->第四条（D）是和A相反的向量
#A出发的直线与原始向量A方向相同，-A出发的直线与原始向量A的方向相反
#TODO 以右手系排序交点向量（需要分奇偶）

def setup():
    py5.size(500,500)

def draw():
    py5.background(155)


def get_inter_2dict(a_dict,b_dict):
    """
    查找两个line字典之间的所有焦点
    """
    points=[]
    inter=Tools2D()
    for key,value in a_dict.items():
        for b_key,b_value in b_dict.items():
            the_point=inter.intersection_2line(value,b_value)
            if the_point is not None:
                points.append(the_point)
    return points

def distance_line_dict(line_dict,center=(250,250)):
    """
    center：以某一点为中心求距离
    返回一个以距离作为key的line字典
    用于重新排序line字典便于进行tilling
    ！如果距离相同会返回列表型的Values
    """
    t=Tools2D()
    back_line_dict={}
    rename=0
    for key,value in line_dict.items():
        the_distance=t.distance_point_to_line(point=center,line=value)
        if the_distance in back_line_dict:
            if isinstance(back_line_dict[the_distance], list):
                # 如果已经是列表，将值添加到列表中
                back_line_dict[the_distance].append(value.copy())
            else:
                # 如果当前值不是列表，转换为列表
                back_line_dict[the_distance] = [back_line_dict[the_distance], value.copy()]
            continue
        back_line_dict[the_distance]=value.copy()
    back_line_dict=dict(sorted(back_line_dict.items())) #从小到大排序
    return back_line_dict


the_gird_dict=gird.create_gird(5,50,100,[250,250],line_num=3)
new_grid_dict = {str(key): value for key, value in the_gird_dict.items()}

with open('output.json','w') as js_file:
    json.dump(new_grid_dict,js_file,indent=4)
# py5.run_sketch()