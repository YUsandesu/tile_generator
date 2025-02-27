# import gird
import py5
import json
import numpy as np
from YuSan_PY5_Toolscode import Tools2D


def distance_line_dict(line_dict, center=(250, 250)):
    """
    center：以某一点为中心求距离
    返回一个以距离作为key的line字典
    用于重新排序line字典便于进行tilling
    ！如果距离相同会返回列表型的Values
    """
    t = Tools2D()
    back_line_dict = {}
    rename = 0

    for key, value in line_dict.items():
        the_distance = t.distance_point_to_line(point=center, line=value)
        if the_distance in back_line_dict:
            if isinstance(back_line_dict[the_distance], list):
                # 如果已经是列表，将值添加到列表中
                back_line_dict[the_distance].append(value.copy())
            else:
                # 如果当前值不是列表，转换为列表
                back_line_dict[the_distance] = [back_line_dict[the_distance], value.copy()]
            continue
        back_line_dict[the_distance] = value.copy()
    back_line_dict = dict(sorted(back_line_dict.items()))  # 从小到大排序
    return back_line_dict

def setup():
    py5.size(500, 500)

def draw():
    py5.background(155)

def get_girds_interaction(gird_data:list):
    """
    查找两个line字典之间的所有焦点
    输入值:((vector):{0:line_dict,1:xx,-1:xx},():{0:xx,1:xx,-1:xx})
    输出值:{ (p_x,p_y):[{v:v,n:n},{v_info}],[_x,_y]:[...],.. }
    """

    tools = Tools2D()

    girds_list = [i['girds']for i in gird_data]

    interaction_data = {}

    for t,i in enumerate(gird_data):#创建空字典
        gird_data[t]['interaction'] = {}
    for t_out, out_gird in enumerate(girds_list[:-1]):  # 循环向量列表 切掉最后一项
        for t_in, in_gird in enumerate(girds_list[t_out + 1:],start = t_out + 1):  # 循环向量列表 切掉当前项
            for number_out, line_detail_out in out_gird.items():
                for number_in, line_detail_in in in_gird.items():
                    interaction_point = tools.intersection_2line(line_detail_out, line_detail_in)
                    if interaction_point is None: continue

                    if number_out not in gird_data[t_out]['interaction']:
                        gird_data[t_out]['interaction'][number_out]=[]
                    if number_in not in gird_data[t_in]['interaction']:
                        gird_data[t_in]['interaction'][number_in]=[]

                    gird_data[t_out]['interaction'][number_out].append(interaction_point)
                    gird_data[t_in]['interaction'][number_in].append(interaction_point)

                    if tuple(interaction_point) not in interaction_data:
                        interaction_data[tuple(interaction_point)]=[]
                    interaction_data[tuple(interaction_point)].append({"gird_list_index":t_out,"num":number_out})
                    interaction_data[tuple(interaction_point)].append({"gird_list_index": t_in, "num": number_in})
    print(f'交点信息:{interaction_data}')
    #目前有两种 interaction一种是以点为key的inter_data 还有一种是以直线为key的 girds[t]['interaction']
    return gird_data

def sort_girds_interaction(gird_data):
    for each_gird in gird_data:
        for line_num,line_info in each_gird['girds']:
            zero = line_info['location_point']
            direction =  line_info['direction_vector']
            index = line_num
            points_list = each_gird['interaction'][index]
            #TODO 求zero和point之间的向量 1.是否和direction相同决定正负 2.保存距离,作为字典的key
            # 按照距离重新排序,从小到大(向量方向)


def get_tilling_information(gird_origin_vectors, vectors):
    """
    这是一个辅助函数,获得拼接图形的顺序,根据顺序可以拼接出闭合的多边形
    all_vectors_list是顺时针排列的origin_vector
    vector_list是当前交点的vectors信息
    返回一个列表,是拼接的顺序,可以按照这个顺序拼接出闭合多边形
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
    # TODO 目前all_vectors_list必须是顺时针排列,应该增加一个矩阵点乘来排列

    # 转换成元组方便使用集合方法
    the_origin_vectors = [tuple(vector) for vector in gird_origin_vectors]
    vectors_set = {tuple(vector) for vector in vectors}

    sides = len(the_origin_vectors)
    if sides % 2 != 0:  # 奇数
        print('进入奇数处理')
        temp_list = [None] * sides * 2
        for i, the_vector in enumerate(the_origin_vectors):
            if the_vector in vectors_set:
                temp_list[2 * i] = the_vector  # noqa
                temp_list[(2 * i + sides) % (sides * 2)] = (-the_vector[0], -the_vector[1])  # noqa
        tilling_vectors = [a_vector for a_vector in temp_list if a_vector is not None]

    else:  # 偶数
        back_list_positive = [the_vector for the_vector in the_origin_vectors if the_vector in vectors_set]
        back_list_negative = [(-the_vector[0], -the_vector[1])
                              for the_vector in the_origin_vectors if the_vector in vectors_set]
        # 考虑十字情况,有时正向量和反向量重复,合并的时候需要判断是否重复
        tilling_vectors = back_list_positive + [negative_v for negative_v in back_list_negative
                                                if negative_v not in back_list_positive]

    # tilling_vectors只是移动的路径,需要绘制成坐标点
    tilling_vectors_np = np.array(tilling_vectors)
    cumulative_sum = np.cumsum(tilling_vectors_np, axis=0)
    tilling = cumulative_sum.tolist()

    tem=Tools2D() #防止出现无穷小数
    tilling = [ [tem.reduce_errors(num=vector[0]),tem.reduce_errors(vector[1])] for vector in tilling]


    # 此处一并返回原vector,方便拼接.
    # vector_o[0]是 tilling[-1]和[0] (开头和末尾)
    # vector_o[1]是[0]和[1] (第一个和第二个)-->以此类推
    tilling_dict = {(tuple(vectors[0])): [tilling[-1], tilling[0]]}
    tilling_dict = tilling_dict | {(tuple(vector)): [tilling[t - 1], tilling[t]]  # noqa
                                   for t, vector in enumerate(tilling_vectors[1:], start=1)}  # 切掉了0 这样t不会超出index

    return tilling_dict

def splice_tilling(tilling_info_a, tilling_info_b, positive_direction):
    """
    start_interaction:某一个交点
    direction,拼接方向
    """
    # <think>一个交点具有两个向量,相应的具有:四个方向
    # TODO 在gird上面行走 例:一个交点是两条直线相交形成的,那么有4中行走方向(A正,A负,B正,B负)
    print()

def is_able_splice(inter_info_a, inter_info_b):
    """
    判断能否成功拼接
    返回这个tilling共线的[A共线的边,B共线的边]
    """
    #inter_info 示例: [{'vector': (0, 25), 'num': 0}, {'vector': (-24, 7), 'num': 1}]

    collinear = {}
    different = {}

    for info_a in inter_info_a:
        if info_a in inter_info_b:
            collinear = info_a
            inter_info_a.remove(info_a)
            inter_info_b.remove(info_a)
            continue

    if not collinear:
        return False

    #TODO 这里需要求两条线之间的向量A-B 是否Pen_vector方向相同
    #条件: A,B交点信息,至少有一项是重合的-->也就是说在gird上 至少在一个方向上共线
    #重合的边 就是生成tilling共线的边
    #如果是朝正方向移动的那么就是 A的正 对应 B的负 如果是朝负方向移动 就是A-对B+

back_list= [{'origin_vector': [0, 25.519524250561197], 'pen_origin_vector': [-25.519524250561197, 0], 'shift_vector_based_distance': [0, 10], 'origin_directed_line': {'directed': True, 'location_point': [400.0, 310.0], 'direction_vector': [-25.519524250561197, 0]}, 'girds': {0: {'directed': True, 'location_point': [400.0, 310.0], 'direction_vector': [-25.519524250561197, 0]}, 1: {'directed': True, 'location_point': [400.0, 362.0], 'direction_vector': [-25.519524250561197, 0]}, -1: {'directed': True, 'location_point': [400.0, 258.0], 'direction_vector': [-25.519524250561197, 0]}, 2: {'directed': True, 'location_point': [400.0, 414.0], 'direction_vector': [-25.519524250561197, 0]}, -2: {'directed': True, 'location_point': [400.0, 206.0], 'direction_vector': [-25.519524250561197, 0]}, 3: {'directed': True, 'location_point': [400.0, 466.0], 'direction_vector': [-25.519524250561197, 0]}, -3: {'directed': True, 'location_point': [400.0, 154.0], 'direction_vector': [-25.519524250561197, 0]}, 4: {'directed': True, 'location_point': [400.0, 518.0], 'direction_vector': [-25.519524250561197, 0]}, -4: {'directed': True, 'location_point': [400.0, 102.0], 'direction_vector': [-25.519524250561197, 0]}, 5: {'directed': True, 'location_point': [400.0, 570.0], 'direction_vector': [-25.519524250561197, 0]}, -5: {'directed': True, 'location_point': [400.0, 50.0], 'direction_vector': [-25.519524250561197, 0]}, 6: {'directed': True, 'location_point': [400.0, 622.0], 'direction_vector': [-25.519524250561197, 0]}, -6: {'directed': True, 'location_point': [400.0, -2.0], 'direction_vector': [-25.519524250561197, 0]}, 7: {'directed': True, 'location_point': [400.0, 674.0], 'direction_vector': [-25.519524250561197, 0]}, -7: {'directed': True, 'location_point': [400.0, -54.0], 'direction_vector': [-25.519524250561197, 0]}, 8: {'directed': True, 'location_point': [400.0, 726.0], 'direction_vector': [-25.519524250561197, 0]}, -8: {'directed': True, 'location_point': [400.0, -106.0], 'direction_vector': [-25.519524250561197, 0]}}}, {'origin_vector': [-24.27050983124842, 7.885966681787004], 'pen_origin_vector': [-7.885966681787006, -24.27050983124842], 'shift_vector_based_distance': [-9.510565162951535, 3.090169943749474], 'origin_directed_line': {'directed': True, 'location_point': [390.48943483704846, 303.09016994374946], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, 'girds': {0: {'directed': True, 'location_point': [390.48943483704846, 303.09016994374946], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, 1: {'directed': True, 'location_point': [341.0344959897005, 319.1590536512467], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, -1: {'directed': True, 'location_point': [439.94437368439645, 287.0212862362522], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, 2: {'directed': True, 'location_point': [291.5795571423525, 335.227937358744], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, -2: {'directed': True, 'location_point': [489.39931253174444, 270.95240252875493], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, 3: {'directed': True, 'location_point': [242.12461829500452, 351.29682106624125], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, -3: {'directed': True, 'location_point': [538.8542513790924, 254.88351882125767], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, 4: {'directed': True, 'location_point': [192.6696794476565, 367.3657047737385], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, -4: {'directed': True, 'location_point': [588.3091902264405, 238.8146351137604], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, 5: {'directed': True, 'location_point': [143.21474060030855, 383.4345884812358], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, -5: {'directed': True, 'location_point': [637.7641290737884, 222.74575140626314], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, 6: {'directed': True, 'location_point': [93.75980175296058, 399.50347218873304], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, -6: {'directed': True, 'location_point': [687.2190679211363, 206.67686769876588], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, 7: {'directed': True, 'location_point': [44.304862905612595, 415.5723558962303], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, -7: {'directed': True, 'location_point': [736.6740067684843, 190.6079839912686], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, 8: {'directed': True, 'location_point': [-5.150075941735452, 431.6412396037276], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, -8: {'directed': True, 'location_point': [786.1289456158324, 174.53910028377132], 'direction_vector': [-7.885966681787006, -24.27050983124842]}}}, {'origin_vector': [-15.000000000000002, -20.6457288070676], 'pen_origin_vector': [20.6457288070676, -15.000000000000004], 'shift_vector_based_distance': [-5.877852522924733, -8.090169943749473], 'origin_directed_line': {'directed': True, 'location_point': [394.12214747707526, 291.90983005625054], 'direction_vector': [20.6457288070676, -15.000000000000004]}, 'girds': {0: {'directed': True, 'location_point': [394.12214747707526, 291.90983005625054], 'direction_vector': [20.6457288070676, -15.000000000000004]}, 1: {'directed': True, 'location_point': [363.55731435786663, 249.84094634875328], 'direction_vector': [20.6457288070676, -15.000000000000004]}, -1: {'directed': True, 'location_point': [424.6869805962839, 333.9787137637478], 'direction_vector': [20.6457288070676, -15.000000000000004]}, 2: {'directed': True, 'location_point': [332.99248123865806, 207.772062641256], 'direction_vector': [20.6457288070676, -15.000000000000004]}, -2: {'directed': True, 'location_point': [455.25181371549246, 376.04759747124507], 'direction_vector': [20.6457288070676, -15.000000000000004]}, 3: {'directed': True, 'location_point': [302.42764811944943, 165.70317893375875], 'direction_vector': [20.6457288070676, -15.000000000000004]}, -3: {'directed': True, 'location_point': [485.8166468347011, 418.11648117874233], 'direction_vector': [20.6457288070676, -15.000000000000004]}, 4: {'directed': True, 'location_point': [271.86281500024086, 123.63429522626149], 'direction_vector': [20.6457288070676, -15.000000000000004]}, -4: {'directed': True, 'location_point': [516.3814799539097, 460.1853648862396], 'direction_vector': [20.6457288070676, -15.000000000000004]}, 5: {'directed': True, 'location_point': [241.2979818810322, 81.56541151876422], 'direction_vector': [20.6457288070676, -15.000000000000004]}, -5: {'directed': True, 'location_point': [546.9463130731183, 502.25424859373686], 'direction_vector': [20.6457288070676, -15.000000000000004]}, 6: {'directed': True, 'location_point': [210.7331487618236, 39.49652781126696], 'direction_vector': [20.6457288070676, -15.000000000000004]}, -6: {'directed': True, 'location_point': [577.5111461923269, 544.3231323012342], 'direction_vector': [20.6457288070676, -15.000000000000004]}, 7: {'directed': True, 'location_point': [180.168315642615, -2.572355896230306], 'direction_vector': [20.6457288070676, -15.000000000000004]}, -7: {'directed': True, 'location_point': [608.0759793115355, 586.3920160087314], 'direction_vector': [20.6457288070676, -15.000000000000004]}, 8: {'directed': True, 'location_point': [149.6034825234064, -44.64123960372757], 'direction_vector': [20.6457288070676, -15.000000000000004]}, -8: {'directed': True, 'location_point': [638.6408124307441, 628.4608997162286], 'direction_vector': [20.6457288070676, -15.000000000000004]}}}, {'origin_vector': [14.999999999999996, -20.645728807067602], 'pen_origin_vector': [20.645728807067602, 14.999999999999995], 'shift_vector_based_distance': [5.877852522924731, -8.090169943749475], 'origin_directed_line': {'directed': True, 'location_point': [405.87785252292474, 291.90983005625054], 'direction_vector': [20.645728807067602, 14.999999999999995]}, 'girds': {0: {'directed': True, 'location_point': [405.87785252292474, 291.90983005625054], 'direction_vector': [20.645728807067602, 14.999999999999995]}, 1: {'directed': True, 'location_point': [436.4426856421333, 249.84094634875328], 'direction_vector': [20.645728807067602, 14.999999999999995]}, -1: {'directed': True, 'location_point': [375.31301940371617, 333.9787137637478], 'direction_vector': [20.645728807067602, 14.999999999999995]}, 2: {'directed': True, 'location_point': [467.00751876134194, 207.772062641256], 'direction_vector': [20.645728807067602, 14.999999999999995]}, -2: {'directed': True, 'location_point': [344.74818628450754, 376.04759747124507], 'direction_vector': [20.645728807067602, 14.999999999999995]}, 3: {'directed': True, 'location_point': [497.5723518805505, 165.70317893375875], 'direction_vector': [20.645728807067602, 14.999999999999995]}, -3: {'directed': True, 'location_point': [314.18335316529897, 418.11648117874233], 'direction_vector': [20.645728807067602, 14.999999999999995]}, 4: {'directed': True, 'location_point': [528.1371849997591, 123.63429522626146], 'direction_vector': [20.645728807067602, 14.999999999999995]}, -4: {'directed': True, 'location_point': [283.61852004609034, 460.18536488623965], 'direction_vector': [20.645728807067602, 14.999999999999995]}, 5: {'directed': True, 'location_point': [558.7020181189678, 81.56541151876417], 'direction_vector': [20.645728807067602, 14.999999999999995]}, -5: {'directed': True, 'location_point': [253.05368692688174, 502.2542485937369], 'direction_vector': [20.645728807067602, 14.999999999999995]}, 6: {'directed': True, 'location_point': [589.2668512381763, 39.49652781126693], 'direction_vector': [20.645728807067602, 14.999999999999995]}, -6: {'directed': True, 'location_point': [222.48885380767314, 544.3231323012342], 'direction_vector': [20.645728807067602, 14.999999999999995]}, 7: {'directed': True, 'location_point': [619.8316843573849, -2.5723558962303628], 'direction_vector': [20.645728807067602, 14.999999999999995]}, -7: {'directed': True, 'location_point': [191.92402068846454, 586.3920160087314], 'direction_vector': [20.645728807067602, 14.999999999999995]}, 8: {'directed': True, 'location_point': [650.3965174765935, -44.64123960372763], 'direction_vector': [20.645728807067602, 14.999999999999995]}, -8: {'directed': True, 'location_point': [161.35918756925597, 628.4608997162287], 'direction_vector': [20.645728807067602, 14.999999999999995]}}}, {'origin_vector': [24.270509831248425, 7.885966681786999], 'pen_origin_vector': [-7.885966681786997, 24.270509831248425], 'shift_vector_based_distance': [9.510565162951536, 3.0901699437494723], 'origin_directed_line': {'directed': True, 'location_point': [409.51056516295154, 303.09016994374946], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, 'girds': {0: {'directed': True, 'location_point': [409.51056516295154, 303.09016994374946], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, 1: {'directed': True, 'location_point': [458.9655040102995, 319.1590536512467], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, -1: {'directed': True, 'location_point': [360.05562631560355, 287.0212862362522], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, 2: {'directed': True, 'location_point': [508.4204428576475, 335.227937358744], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, -2: {'directed': True, 'location_point': [310.60068746825556, 270.95240252875493], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, 3: {'directed': True, 'location_point': [557.8753817049956, 351.29682106624125], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, -3: {'directed': True, 'location_point': [261.14574862090757, 254.8835188212577], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, 4: {'directed': True, 'location_point': [607.3303205523436, 367.36570477373846], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, -4: {'directed': True, 'location_point': [211.69080977355955, 238.81463511376043], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, 5: {'directed': True, 'location_point': [656.7852593996915, 383.4345884812357], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, -5: {'directed': True, 'location_point': [162.23587092621156, 222.7457514062632], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, 6: {'directed': True, 'location_point': [706.2401982470394, 399.503472188733], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, -6: {'directed': True, 'location_point': [112.7809320788636, 206.67686769876593], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, 7: {'directed': True, 'location_point': [755.6951370943875, 415.57235589623025], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, -7: {'directed': True, 'location_point': [63.32599323151561, 190.60798399126867], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, 8: {'directed': True, 'location_point': [805.1500759417355, 431.6412396037275], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, -8: {'directed': True, 'location_point': [13.871054384167564, 174.5391002837714], 'direction_vector': [-7.885966681786997, 24.270509831248425]}}}]
back_list=get_girds_interaction(back_list)
for i in back_list:
    print(f"\n{i}")
