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

class TILLING:
    def __init__(self,girds_data):
        if girds_data:
            self.girds_data = girds_data
        else:
            raise ValueError("缺少girds_data")
        self.interaction_data_point_location={}
        self.interaction_data_line_id={}

    def get_girds_interaction(self):
        """
        查找两个line字典之间的所有焦点
        输入值:((vector):{0:line_dict,1:xx,-1:xx},():{0:xx,1:xx,-1:xx})
        输出值:{ (p_x,p_y):[{v:v,n:n},{v_info}],[_x,_y]:[...],.. }
        """
        tools = Tools2D()
        girds_list = [i['girds'] for i in self.girds_data]

        interaction_data = {}  # 按坐标点聚合的交点信息
        inter_point_data = {}  # 按线段维度聚合的交点信息（新结构）

        for t_out, out_gird in enumerate(girds_list[:-1]):
            for t_in, in_gird in enumerate(girds_list[t_out + 1:], start=t_out + 1):
                for number_out, line_detail_out in out_gird.items():
                    for number_in, line_detail_in in in_gird.items():
                        interaction_point = tools.intersection_2line(line_detail_out, line_detail_in)
                        if interaction_point is None:
                            continue

                        # 新数据结构处理 (使用元组作为复合键)
                        # 处理外层线段 (t_out, number_out)
                        key_out = (t_out, number_out)
                        if key_out not in inter_point_data:
                            inter_point_data[key_out] = []
                        inter_point_data[key_out].append(interaction_point)

                        # 处理内层线段 (t_in, number_in)
                        key_in = (t_in, number_in)
                        if key_in not in inter_point_data:
                            inter_point_data[key_in] = []
                        inter_point_data[key_in].append(interaction_point)

                        # 保留原坐标点维度聚合逻辑
                        point_key = tuple(interaction_point)
                        if point_key not in interaction_data:
                            interaction_data[point_key] = []
                        interaction_data[point_key].extend([
                            (t_out,number_out),
                            (t_in,number_in)
                        ])

        self.interaction_data_line_id = inter_point_data
        self.interaction_data_point_location = interaction_data
        # interaction_data_point_location 结构示例
        # {
        #     (0, 0): [[x1, y1], [x2, y2], ...],  # gird_data[0]中girds键下0号线段的所有交点
        #     (1, -1): [[x3, y3]],  # gird_data[1]中girds键下-1号线段的交点
        #     (2, 1): [...]  # gird_data[2]中girds键下1号线段的交点
        # }

    def sort_girds_interaction(self):
        # 指向1象限是x自小到大排列(+,+)=+,指向2象限是x自大到小排列(-,+)=-
        # 指向3象限是x自大到小排列(-,-)=-,指向4象限是x自小到大排列(+,-)=+
        #y:         +                          +
        #           -                          -
        # 综上
        # 只需要判断 pen_origin_vector 的x符号,为正就是从小到大,为负就是从大到小
        # 为0就判断y的符号,为正就是y从小到大,为负就是从大到小

        inter_data = self.interaction_data_point_location
        reverse_data={}
        #line_id 例: (a,b) --> girds_data[a]['girds'][b]
        for point,line_id_list in inter_data.items():
            for line_id in line_id_list:

                if not isinstance(line_id,tuple):
                    line_id=tuple(line_id)#防止传入的是列表导致错误

                if line_id not in reverse_data:
                    reverse_data[line_id]=[]
                reverse_data[line_id].append(point)

        for line_id,points in reverse_data.items():
            data_id,girds_id = line_id[0],line_id[1]
            line=self.girds_data[data_id]['girds'][girds_id]
            direction_vector = line['direction_vector']
            x,y = direction_vector

            points=np.array(points)
            if not x==0:
                sorted_indices = np.argsort(np.sign(x)*points[:, 0]) #根据x坐标
            elif not y==0:
                sorted_indices = np.argsort(np.sign(y)*points[:, 1])  # 根据x坐标
            else:continue
            sorted_points = points[sorted_indices].tolist()
            reverse_data[line_id]=sorted_points
        self.interaction_data_line_id = reverse_data

    @staticmethod
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

        tem = Tools2D()  # 防止出现无穷小数
        tilling = [[tem.reduce_errors(num=vector[0]), tem.reduce_errors(vector[1])] for vector in tilling]

        # 此处一并返回原vector,方便拼接.
        # vector_o[0]是 tilling[-1]和[0] (开头和末尾)
        # vector_o[1]是[0]和[1] (第一个和第二个)-->以此类推
        tilling_dict = {(tuple(vectors[0])): [tilling[-1], tilling[0]]}
        tilling_dict = tilling_dict | {(tuple(vector)): [tilling[t - 1], tilling[t]]  # noqa
                                       for t, vector in
                                       enumerate(tilling_vectors[1:], start=1)}  # 切掉了0 这样t不会超出index

        return tilling_dict

    def splice_tilling(self,interaction_point_location):
        """

        """
        # <think>一个交点具有两个向量,相应的具有:四个方向
        data_point = self.interaction_data_point_location
        if not interaction_point_location in data_point:
            raise ValueError (f"interaction_data_point_location中未找到点{interaction_point_location}")

        # 获取自己的tilling形状
        inter_lines = data_point[interaction_point_location]
        now_vector = [self.girds_data[index] for index,num in inter_lines]
        o_vector = [i['origin_vector']for i in self.girds_data]
        self.get_tilling_information(o_vector,now_vector)

        #拼接两个正向的



        print()

    @staticmethod
    def is_able_splice(inter_info_a, inter_info_b):
        """
        判断能否成功拼接
        返回这个tilling共线的[A共线的边,B共线的边]
        """
        # inter_info 示例: [{'vector': (0, 25), 'num': 0}, {'vector': (-24, 7), 'num': 1}]

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

        # TODO 这里需要求两条线之间的向量A-B 是否Pen_vector方向相同
        # 条件: A,B交点信息,至少有一项是重合的-->也就是说在gird上 至少在一个方向上共线
        # 重合的边 就是生成tilling共线的边
        # 如果是朝正方向移动的那么就是 A的正 对应 B的负 如果是朝负方向移动 就是A-对B+





back_list= [{'origin_vector': [0, 25.519524250561197], 'pen_origin_vector': [-25.519524250561197, 0], 'shift_vector_based_distance': [0, 15], 'origin_directed_line': {'directed': True, 'location_point': [400.0, 315.0], 'direction_vector': [-25.519524250561197, 0]}, 'girds': {0: {'directed': True, 'location_point': [400.0, 315.0], 'direction_vector': [-25.519524250561197, 0]}, 1: {'directed': True, 'location_point': [400.0, 465.0], 'direction_vector': [-25.519524250561197, 0]}, -1: {'directed': True, 'location_point': [400.0, 165.0], 'direction_vector': [-25.519524250561197, 0]}}}, {'origin_vector': [-24.27050983124842, 7.885966681787004], 'pen_origin_vector': [-7.885966681787006, -24.27050983124842], 'shift_vector_based_distance': [-14.265847744427303, 4.635254915624212], 'origin_directed_line': {'directed': True, 'location_point': [385.7341522555727, 304.6352549156242], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, 'girds': {0: {'directed': True, 'location_point': [385.7341522555727, 304.6352549156242], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, 1: {'directed': True, 'location_point': [243.07567481129968, 350.9878040718663], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, -1: {'directed': True, 'location_point': [528.3926296998458, 258.2827057593821], 'direction_vector': [-7.885966681787006, -24.27050983124842]}}}, {'origin_vector': [-15.000000000000002, -20.6457288070676], 'pen_origin_vector': [20.6457288070676, -15.000000000000004], 'shift_vector_based_distance': [-8.8167787843871, -12.13525491562421], 'origin_directed_line': {'directed': True, 'location_point': [391.1832212156129, 287.8647450843758], 'direction_vector': [20.6457288070676, -15.000000000000004]}, 'girds': {0: {'directed': True, 'location_point': [391.1832212156129, 287.8647450843758], 'direction_vector': [20.6457288070676, -15.000000000000004]}, 1: {'directed': True, 'location_point': [303.0154333717419, 166.51219592813368], 'direction_vector': [20.6457288070676, -15.000000000000004]}, -1: {'directed': True, 'location_point': [479.3510090594839, 409.2172942406179], 'direction_vector': [20.6457288070676, -15.000000000000004]}}}, {'origin_vector': [14.999999999999996, -20.645728807067602], 'pen_origin_vector': [20.645728807067602, 14.999999999999995], 'shift_vector_based_distance': [8.816778784387097, -12.135254915624213], 'origin_directed_line': {'directed': True, 'location_point': [408.8167787843871, 287.8647450843758], 'direction_vector': [20.645728807067602, 14.999999999999995]}, 'girds': {0: {'directed': True, 'location_point': [408.8167787843871, 287.8647450843758], 'direction_vector': [20.645728807067602, 14.999999999999995]}, 1: {'directed': True, 'location_point': [496.9845666282581, 166.51219592813365], 'direction_vector': [20.645728807067602, 14.999999999999995]}, -1: {'directed': True, 'location_point': [320.6489909405161, 409.2172942406179], 'direction_vector': [20.645728807067602, 14.999999999999995]}}}, {'origin_vector': [24.270509831248425, 7.885966681786999], 'pen_origin_vector': [-7.885966681786997, 24.270509831248425], 'shift_vector_based_distance': [14.265847744427305, 4.635254915624208], 'origin_directed_line': {'directed': True, 'location_point': [414.26584774442733, 304.6352549156242], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, 'girds': {0: {'directed': True, 'location_point': [414.26584774442733, 304.6352549156242], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, 1: {'directed': True, 'location_point': [556.9243251887004, 350.9878040718663], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, -1: {'directed': True, 'location_point': [271.60737030015423, 258.2827057593821], 'direction_vector': [-7.885966681786997, 24.270509831248425]}}}]
till=TILLING(back_list)
till.get_girds_interaction()
till.sort_girds_interaction()
print(f'interaction_data_line_id:\n{till.interaction_data_line_id}')
print(f'interaction_data_point_location:\n{till.interaction_data_point_location}')
# for i in back_list:
#     print(f"\n{i}")
