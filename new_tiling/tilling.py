# import gird
import py5
import json
import numpy as np
from YuSan_PY5_Toolscode import Tools2D, screen_axis, screen_draw_SegmentLine


class BruijnsTilling:
    def __init__(self,girds_data=None,sides=5,shifted_distance=50,gap=100,center=(100, 100),num_of_line=15):
        if girds_data:
            self.girds_data = girds_data
        else:
            self.girds_data = self.create_gird(sides=sides,shifted_distance=shifted_distance,gap=gap,center=center,num_of_line=num_of_line)
        self.interaction_data_point_location: dict[tuple[float | int]:list[int]] ={} # 按坐标点聚合的线段id信息
        self.interaction_data_line_id: dict[tuple[int]:list[float | int]] ={} # 按线段id聚合的坐标点信息
        self.get_girds_interaction()


    def get_girds_interaction(self):
        """
        查找两个line字典之间的所有焦点
        输入值:((vector):{0:line_dict,1:xx,-1:xx},():{0:xx,1:xx,-1:xx})
        输出值:{ (p_x,p_y):[{v:v,n:n},{v_info}],[_x,_y]:[...],.. }
        最后自动按照向量方向来排序(从反方向-->正方向排队)
        """
        tools = Tools2D()
        girds_list = [i['girds'] for i in self.girds_data]

        #清空已有
        if self.interaction_data_point_location:
            self.interaction_data_point_location={}
        if self.interaction_data_line_id:
            self.interaction_data_point_location = {}

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
                        if key_out not in self.interaction_data_line_id:
                            self.interaction_data_line_id[key_out] = []
                        self.interaction_data_line_id[key_out].append(interaction_point)

                        # 处理内层线段 (t_in, number_in)
                        key_in = (t_in, number_in)
                        if key_in not in self.interaction_data_line_id:
                            self.interaction_data_line_id[key_in] = []
                        self.interaction_data_line_id[key_in].append(interaction_point)

                        # 保留原坐标点维度聚合逻辑
                        point_key = tuple(interaction_point)
                        if point_key not in self.interaction_data_point_location:
                            self.interaction_data_point_location[point_key] = []
                        self.interaction_data_point_location[point_key].extend([
                            (t_out,number_out),
                            (t_in,number_in)
                        ])

        self._sort_girds_interaction()
        # interaction_data_point_location 结构示例
        # {
        #     (0, 0): [[x1, y1], [x2, y2], ...],  # gird_data[0]中girds键下0号线段的所有交点
        #     (1, -1): [[x3, y3]],  # gird_data[1]中girds键下-1号线段的交点
        #     (2, 1): [...]  # gird_data[2]中girds键下1号线段的交点
        # }

    def _sort_girds_interaction(self):
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

        # gird_origin_vectors 必须是顺时针排列

        # def _sort_clockwise(the_vectors):
        #     """使用向量叉积进行顺时针排序"""
        #     center = np.mean(the_vectors, axis=0)
        #     return sorted(the_vectors, key=lambda v: np.arctan2(v[1] - center[1], v[0] - center[0]))

        # 转换成元组方便使用集合方法
        the_origin_vectors = [tuple(vector) for vector in gird_origin_vectors]
        vectors_set = {tuple(vector) for vector in vectors}
        sides = len(the_origin_vectors)
        if sides % 2 != 0:  # 奇数
            # print('进入奇数处理')
            temp_list = [None] * sides * 2
            temp_list:  [None] * sides * 2 #防止pycharm检查器报错
            for i, the_vector in enumerate(the_origin_vectors):
                if the_vector in vectors_set:
                    temp_list[2 * i] = the_vector
                    temp_list[(2 * i + sides) % (sides * 2)] = (-the_vector[0], -the_vector[1])
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

        # 防止出现无穷小数
        tilling = [[Tools2D.reduce_errors(vector[0]), Tools2D.reduce_errors(vector[1])] for vector in tilling]

        # 此处一并返回原vector,方便拼接.
        # vector_o[0]是 tilling[-1]和[0] (开头和末尾)
        # vector_o[1]是[0]和[1] (第一个和第二个)-->以此类推
        tilling_dict_positive = {(tuple(vectors[0])): [tilling[-1], tilling[0]]}
        tilling_dict_negative = {}
        for t, vector in enumerate(tilling_vectors[1:], start=1):
            if tuple(vector) in vectors_set:
                tilling_dict_positive[tuple(vector)] = [tilling[t - 1], tilling[t]]
            else:
                tilling_dict_negative[tuple(vector)] = [tilling[t - 1], tilling[t]]

        return tilling_dict_positive,tilling_dict_negative

    def splice_tilling(self,interaction_point_location):
        """

        """
        # <think>一个交点具有两个向量,相应的具有:四个方向
        tem = Tools2D()

        data_point = self.interaction_data_point_location
        o_vector = [i['origin_vector'] for i in self.girds_data]

        if not interaction_point_location in data_point:
            raise ValueError (f"interaction_data_point_location中未找到点{interaction_point_location}")


        inter_lines_index_num:list[int,int] = data_point[interaction_point_location]
        now_vector: list[tuple[int | float]] = [tuple(o_vector[i]) for i,_ in inter_lines_index_num]
        # 获取自己的tilling形状
        o_positive_sides,o_negative_sides = self.get_tilling_information(o_vector,now_vector)
        origin_tilling:dict[tuple:list[list]] = o_positive_sides | o_negative_sides
        return_list = list(origin_tilling.values())
        #查询正方向的点和负方向的点
        data_line_id = self.interaction_data_line_id

        next_points_list:list[tuple[list,bool]] = []
        for line_id in inter_lines_index_num:
            list_index = data_line_id[line_id].index(list(interaction_point_location))
            #查询字典中的前后,字典中已经按照线的方向顺序排好了
            try:next_points_list.append( (data_line_id[line_id][list_index + 1],True) )
            except IndexError:pass #防止超出范围
            try:next_points_list.append( (data_line_id[line_id][list_index + -1],False) )
            except IndexError:pass

        for next_point,is_positive in next_points_list:

            next_vectors = [tuple(o_vector[index]) for index,_ in data_point[tuple(next_point)]]
            next_positive_sides,next_negative_sides = self.get_tilling_information(o_vector,next_vectors)
            next_sides = next_positive_sides|next_negative_sides

            target_side = set(now_vector)&set(next_vectors)
            if len(target_side)!=1:
                raise ValueError(f"获取到不止一条的共线,无法拼接:{target_side}")
            target_side = target_side.pop()

            if is_positive:up_sign = 1
            else:up_sign = -1
            # 因为是正方向, 正向量形成的点和下一个的负方向对齐,负方向反之 负方向对应的线和next正方向的对其

            collinear_in_now =  origin_tilling[(up_sign*target_side[0],up_sign*target_side[1])]
            collinear_in_next = next_sides.pop( (-up_sign*target_side[0], -up_sign*target_side[1]) )

            #因为方向相反,交叉求shift距离
            t_now, _ = collinear_in_now
            _,t_next = collinear_in_next
            shift_vector = [t_now[0] - t_next[0], t_now[1] - t_next[1]]
            new_seg_line_list = list(next_sides.values())
            for segment_line in new_seg_line_list:
                #平移到指定位置来和now_tilling拼合
                return_list.append(tem.point_shift(segment_line, shift_vector))
        # print(splice_tilling:{return_list}')
        return  return_list

    @staticmethod
    def create_gird(sides, shifted_distance=0, gap=100, center=(100, 100), num_of_line=50):
        """
        此函数用于创建一组网格系统
        distance：初始向量取垂直线以后，相互远离的距离。
        zoom：每条网格线相隔的距离
        返回一个列表，每个列表中包含一个方向的平行网格线，由所有网格线组成一个gird
        """

        tools = Tools2D()
        return_girds_data = []

        # 在【0，0】创建一个多边形,返回点集到vector
        vectors_origin = tools.regular_polygon(sides=sides, side_length=30)
        return_girds_data = [{'origin_vector': o_v} for o_v in vectors_origin]

        # 取vector的垂直向量vector_pen
        vectors_origin_pen = [tools.vector_rotate(the_vector, 90) for the_vector in vectors_origin]
        for t, p_o_v in enumerate(vectors_origin_pen):
            return_girds_data[t]['pen_origin_vector'] = p_o_v

        # 定义有向直线:
        for d_v in vectors_origin_pen:
            tools.directed_line_drop(location_point=center, direction_vector=d_v)

        origin_directed_lines = tools.get_line_dic()
        origin_directed_lines_id = list(origin_directed_lines.keys())

        for times, origin_line_id in enumerate(origin_directed_lines_id):
            # 按照vector的方向,改变vector的模长-->获得平移向量distance_vector
            # TODO 此处模长可以不用以相同数值平移,可以存在长度差,应该再增加一个参数调整长度差
            distance_shift_vector = tools.vector_change_norm(vectors_origin[times], shifted_distance)
            return_girds_data[times]['shift_vector_based_distance'] = distance_shift_vector
            tools.line_shift(origin_line_id, distance_shift_vector, rewrite=True, drop=False)

        origin_directed_lines = list(tools.get_line_dic().values())  # 取出的直线数据,准备平移
        for t, o_d_line in enumerate(origin_directed_lines):
            return_girds_data[t]['origin_directed_line'] = o_d_line
        tools.reset()  # 清除内容

        # 平移gird_0，构建平行网格gird
        for t, line_dict in enumerate(origin_directed_lines):  # 遍历原始gird每一条线
            return_girds_data[t]['girds'] = {0: return_girds_data[t]['origin_directed_line']}
            for the_time, i in enumerate(range(1, (num_of_line - 1) // 2 + 1)):  # (num_of_line-1)是因为去掉原始line的1,
                # 最后+1是因为range不包括最后一项

                # vector_origin的顺序和origin_lines的方向是一致的, 长度取zoom的倍数即可
                positive_vector = tools.vector_change_norm(vectors_origin[t], gap * i)
                negative_vector = tools.vector_change_norm(vectors_origin[t], gap * -i)

                # 和origin_vector同方向的为正,反方向的为负
                line_positive_detail = tools.line_shift(line_dict, positive_vector, rewrite=False, drop=False)
                line_negative_detail = tools.line_shift(line_dict, negative_vector, rewrite=False, drop=False)

                return_girds_data[t]['girds'][the_time + 1] = line_positive_detail  # 命名方式1,2,3...
                return_girds_data[t]['girds'][-(the_time + 1)] = line_negative_detail  # -1,-2,-3...

        # print(f'\nback_list:\n')
        # for t, i in enumerate(back_list):
        #     print(f'\n{t}:\n{i}')
        print('完整输出:')
        print(return_girds_data)
        return return_girds_data

used_data= [{'origin_vector': [0, 25.519524250561197], 'pen_origin_vector': [-25.519524250561197, 0], 'shift_vector_based_distance': [0, 15], 'origin_directed_line': {'directed': True, 'location_point': [400.0, 315.0], 'direction_vector': [-25.519524250561197, 0]}, 'girds': {0: {'directed': True, 'location_point': [400.0, 315.0], 'direction_vector': [-25.519524250561197, 0]}, 1: {'directed': True, 'location_point': [400.0, 465.0], 'direction_vector': [-25.519524250561197, 0]}, -1: {'directed': True, 'location_point': [400.0, 165.0], 'direction_vector': [-25.519524250561197, 0]}}}, {'origin_vector': [-24.27050983124842, 7.885966681787004], 'pen_origin_vector': [-7.885966681787006, -24.27050983124842], 'shift_vector_based_distance': [-14.265847744427303, 4.635254915624212], 'origin_directed_line': {'directed': True, 'location_point': [385.7341522555727, 304.6352549156242], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, 'girds': {0: {'directed': True, 'location_point': [385.7341522555727, 304.6352549156242], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, 1: {'directed': True, 'location_point': [243.07567481129968, 350.9878040718663], 'direction_vector': [-7.885966681787006, -24.27050983124842]}, -1: {'directed': True, 'location_point': [528.3926296998458, 258.2827057593821], 'direction_vector': [-7.885966681787006, -24.27050983124842]}}}, {'origin_vector': [-15.000000000000002, -20.6457288070676], 'pen_origin_vector': [20.6457288070676, -15.000000000000004], 'shift_vector_based_distance': [-8.8167787843871, -12.13525491562421], 'origin_directed_line': {'directed': True, 'location_point': [391.1832212156129, 287.8647450843758], 'direction_vector': [20.6457288070676, -15.000000000000004]}, 'girds': {0: {'directed': True, 'location_point': [391.1832212156129, 287.8647450843758], 'direction_vector': [20.6457288070676, -15.000000000000004]}, 1: {'directed': True, 'location_point': [303.0154333717419, 166.51219592813368], 'direction_vector': [20.6457288070676, -15.000000000000004]}, -1: {'directed': True, 'location_point': [479.3510090594839, 409.2172942406179], 'direction_vector': [20.6457288070676, -15.000000000000004]}}}, {'origin_vector': [14.999999999999996, -20.645728807067602], 'pen_origin_vector': [20.645728807067602, 14.999999999999995], 'shift_vector_based_distance': [8.816778784387097, -12.135254915624213], 'origin_directed_line': {'directed': True, 'location_point': [408.8167787843871, 287.8647450843758], 'direction_vector': [20.645728807067602, 14.999999999999995]}, 'girds': {0: {'directed': True, 'location_point': [408.8167787843871, 287.8647450843758], 'direction_vector': [20.645728807067602, 14.999999999999995]}, 1: {'directed': True, 'location_point': [496.9845666282581, 166.51219592813365], 'direction_vector': [20.645728807067602, 14.999999999999995]}, -1: {'directed': True, 'location_point': [320.6489909405161, 409.2172942406179], 'direction_vector': [20.645728807067602, 14.999999999999995]}}}, {'origin_vector': [24.270509831248425, 7.885966681786999], 'pen_origin_vector': [-7.885966681786997, 24.270509831248425], 'shift_vector_based_distance': [14.265847744427305, 4.635254915624208], 'origin_directed_line': {'directed': True, 'location_point': [414.26584774442733, 304.6352549156242], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, 'girds': {0: {'directed': True, 'location_point': [414.26584774442733, 304.6352549156242], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, 1: {'directed': True, 'location_point': [556.9243251887004, 350.9878040718663], 'direction_vector': [-7.885966681786997, 24.270509831248425]}, -1: {'directed': True, 'location_point': [271.60737030015423, 258.2827057593821], 'direction_vector': [-7.885966681786997, 24.270509831248425]}}}]
till=BruijnsTilling(used_data)
print(f'interaction_data_line_id:\n{till.interaction_data_line_id}')
# print(f'interaction_data_point_location:\n{till.interaction_data_point_location}')
tilling_data = till.splice_tilling((389.10186207991956, 315.0))
# for i in back_list:
#     print(f"\n{i}")
tool = Tools2D()

def setup():
    py5.size(500, 500)
    s_v= screen_axis(0,0)
    print(tilling_data)
    for seg_line in tilling_data:
        A_P,B_P=tool.point_shift(seg_line,s_v)
        tool.Segmentline_drop(A_P, B_P)

def draw():
    py5.background(155)
    screen_draw_SegmentLine(tool.get_Segmentline_dic(),0)
py5.run_sketch()
