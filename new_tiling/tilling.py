import gird
import py5
from YuSan_PY5_Toolscode import *



def setup():
    py5.size(500,500)
    global points

def draw():
    py5.background(155)
    screen_draw_lines(the_gird_dic,py5.color(0,0,0,50))
    screen_draw_points(points,fill=None,size=7)

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

def distance_line_dict(line_dict,center=[250,250]):
    """
    center：以某一点为中心求距离
    返回一个以距离作为key的line字典
    用于重新排序line字典便于进行tilling
    """
    t=Tools2D()
    back_line_dict={}
    for key,value in line_dict.items():
        the_distance=t.distance_point_to_line(point=center,line=value)
        back_line_dict[the_distance]=value.copy()
    back_line_dict=dict(sorted(back_line_dict.items()))
    return back_line_dict

the_gird_list=gird.create_gird(5,15,100,[250,250])
print(distance_line_dict(the_gird_list[0]))

# py5.run_sketch()