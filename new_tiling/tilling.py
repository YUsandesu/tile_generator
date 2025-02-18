import gird
import py5
import json
from YuSan_PY5_Toolscode import *


#TODO 这里需要将gird返回的字典 对应找到焦点

#TODO 根据gird的字典头，创建tilling拼块


def setup():
    py5.size(500,500)

def draw():
    py5.background(155)

data={(0, 25.519524250561197): {0: {'str': 'y=315.0', 'k': 0, 'b': 315.0}, 1: {'str': 'y=465.0', 'k': 0, 'b': 465.0}, -1: {'str': 'y=165.0', 'k': 0, 'b': 165.0}},
      (-24.27050983124842, 7.885966681787004): {0: {'str': 'y=3.0776835371752527x-979.6144345325978', 'k': 3.0776835371752527, 'b': -979.6144345325978}, 1: {'str': 'y=3.0776835371752527x-1465.024631157566', 'k': 3.0776835371752527, 'b': -1465.024631157566}, -1: {'str': 'y=3.0776835371752527x-494.2042379076294', 'k': 3.0776835371752527, 'b': -494.2042379076294}},
      (-15.000000000000002, -20.6457288070676): {0: {'str': 'y=-0.7265425280053612x+609.1580308646413', 'k': -0.7265425280053612, 'b': 609.1580308646413}, 1: {'str': 'y=-0.7265425280053612x+794.5682274896099', 'k': -0.7265425280053612, 'b': 794.5682274896099}, -1: {'str': 'y=-0.7265425280053612x+423.74783423967284', 'k': -0.7265425280053612, 'b': 423.74783423967284}},
      (14.999999999999996, -20.645728807067602): {0: {'str': 'y=0.7265425280053607x+27.92400846035256', 'k': 0.7265425280053607, 'b': 27.92400846035256}, 1: {'str': 'y=0.7265425280053607x+213.334205085321', 'k': 0.7265425280053607, 'b': 213.334205085321}, -1: {'str': 'y=0.7265425280053607x-157.4861881646159', 'k': 0.7265425280053607, 'b': -157.4861881646159}},
      (24.270509831248425, 7.885966681786999): {0: {'str': 'y=-3.0776835371752562x+1482.5323952076055', 'k': -3.0776835371752562, 'b': 1482.5323952076055}, 1: {'str': 'y=-3.0776835371752562x+997.1221985826367', 'k': -3.0776835371752562, 'b': 997.1221985826367}, -1: {'str': 'y=-3.0776835371752562x+1967.9425918325744', 'k': -3.0776835371752562, 'b': 1967.9425918325744}}}

#TODO 应该让每根线都和所有线作焦点--->比较每根线的焦点集合--->获得一个倒字典统计了某个焦点有多少线经过
def get_girds_interaction(girds_dict):
    """
    查找两个line字典之间的所有焦点
    输入值:(():{0:xx,1:xx,-1:xx},():{0:xx,1:xx,-1:xx})
    返回值:{((x,y),(x,y)):{(0,0):[a,b],(0,1):[a,b],(0,-1):[a,b]}},((x,y),(..)):{(..):[.],(.):[.]..}
    """
    tools=Tools2D()
    vectors_list = list(girds_dict.keys())
    lines_dict_list = list (girds_dict.values())

    back_dict_keys=[]
    for t,vector_A in enumerate(vectors_list[:-1]):#循环向量列表 切掉最后一项
            for vector_B in vectors_list[t+1:]:#循环向量列表 切掉当前项
                back_dict_keys.append((vector_A,vector_B))

    back_dict_values=[] #示例:[{(0,1):[x,y][x,y], (0,-1):[.,.],[..]}, {(..):..,():..}, ..}]
    # lines_dict_list示例:[{0:(),1:(),-1:()}, {0:0,1:()...},..]
    for t,lines_dict_A in enumerate(lines_dict_list[:-1]):
            for lines_dict_B in lines_dict_list[t+1:]:

                value_dict = {}
                for letter_A, line_detail_A in lines_dict_A.items():
                    for letter_B,line_detail_B in lines_dict_B.items():
                        interaction_point = tools.intersection_2line(line_detail_A,line_detail_B)
                        if not interaction_point:
                            raise ValueError("get_girds_interaction没有取到焦点,请检查输入")
                        value_dict[(letter_A,letter_B)]=interaction_point
                back_dict_values.append(value_dict)

    back_dict= {key:back_dict_values[t] for t,key in enumerate(back_dict_keys)}
    print(back_dict)
    return back_dict_values






    # for vector,lines_dict in enumerate(girds_dict.items()):#先循环A字典
    #
    #     for b_key,b_value in b_dict.items():
    #         the_point=inter.intersection_2line(value,b_value)
    #         if the_point is not None:
    #             points.append(the_point)
    # return points

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

def vertices_queue(sides):
    """
    """
    # 例:1,2,3,4,5
    # 360/10=36-->180/36=5
    # 180/360/10-->5
    # 1,-4, 2,-5, 3,-1, 4,-2, 5,-3

    # 360/6=60-->180/60=3
    # 180/360/side*2=3
    #   ||
    # 间隔数目=sides
    #
    # 转换为:list[0]:1 list[2]:2 list[4]=3 list[6]=4 list[8]=5
    # list[(0+5)%10=5]=-1 list[(2+5)%10=7]=-2 list[(4+5)%10=9]=-3
    # list[(6+5)%10=1]=-4  list[(8+5)%10=3]=-5
    back = [0] * sides * 2
    for i in range(sides):
        back[2*i] = i+1 #如果需要从1开始的话
        back[(2*i+sides) % (sides * 2)] = -(i+1)
    print(back)
vertices_queue(11)

# gird_data=gird.create_gird(5, 50, 100, [250, 250], num_of_line=3)
# print(gird_data,gird.the_lines)
# # new_grid_dict = {str(key): value for key, value in gird_data.items()}
# #
# # #'w'：表示“写”模式。如果文件存在，内容会被清空并重新写入；如果文件不存在，会创建一个新文件。
# # with open('output.json','w') as js_file:
# #     json.dump(new_grid_dict,js_file,indent=4)
# py5.run_sketch()