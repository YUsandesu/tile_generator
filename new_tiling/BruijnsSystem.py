import sys
import time
from new_tiling.PY5_2DToolkit import Tools2D
import numpy as np
import pandas as pd
import warnings
from itertools import islice
from tabulate import tabulate
import humanize

class BruijnsSystem:
    def __init__(self, sides=5, origin_norm=80, shifted_distance=0, gap=100, center=(100, 100), max_num_of_line=50):
        self.tools = Tools2D()
        self.data_df = pd.DataFrame()
        self.data_inter_df = pd.DataFrame()
        self.create_gird(sides=sides, origin_norm=origin_norm, shifted_distance=shifted_distance, gap=gap, center=center,
                                               max_num_of_line=max_num_of_line)
        self.interaction_data_point_location: dict[tuple[float | int]:list[int]] = {}  # 按坐标点聚合的线段id信息
        self.interaction_data_line_id: dict[tuple[int]:list[float | int]] = {}  # 按线段id聚合的坐标点信息
        # self.get_girds_interaction()
        # print(f'共有:{len(self.interaction_data_point_location)}个点')

    def get_girds_interaction(self):
        """
        查找两个line字典之间的所有焦点
        """
        tittles = self.data_df.columns
        girds_t = tittles[tittles.get_loc(0):] #内部line的id列表
        girds_dict = self.data_df.loc[:,girds_t].to_dict('index')
        girds_index = list(girds_dict.keys()) #index列表
        new_columns =[(index,num)for index in girds_index for num in girds_t]#列表表达式嵌套循环从右向左优先级

        # 创建一个字典用于批量构建 DataFrame
        inter_dict = {}
        for t_out in girds_index[:-1]:
            out_gird = girds_dict[t_out]
            for t_in in girds_index[girds_index.index(t_out) + 1:]:
                in_gird = girds_dict[t_in]
                # girds 中遍历每一条线
                for number_out, line_detail_out in out_gird.items():
                    for number_in, line_detail_in in in_gird.items():
                        interaction_point = self.tools.intersection_2line(line_detail_out, line_detail_in)
                        if interaction_point is not None:
                            if (t_out, number_out) not in inter_dict:
                                inter_dict[(t_out, number_out)] = {}
                            if (t_in, number_in) not in inter_dict:
                                inter_dict[(t_in, number_in)] = {}

                            # 将交互点加入到 inter_dict 对应的位置
                            inter_dict[(t_out, number_out)][(t_in, number_in)] = interaction_point
                            inter_dict[(t_in, number_in)][(t_out, number_out)] = interaction_point  # 对称点
        print(f'查找完毕{humanize.naturalsize(deep_get_size(inter_dict))}')
        # 将嵌套字典转换为 DataFrame
        inter_df = pd.DataFrame(inter_dict)
        print(f'格式转换完毕{humanize.naturalsize(inter_df.memory_usage(deep=True).sum())}')
        pd_print(inter_df)
        print('(2,0)and(1,1):',inter_df.loc[(2,0),(1,1)])

    def _sort_girds_interaction(self):
        # 指向1象限是x自小到大排列(+,+)=+,指向2象限是x自大到小排列(-,+)=-
        # 指向3象限是x自大到小排列(-,-)=-,指向4象限是x自小到大排列(+,-)=+
        # dy:         +                          +
        #             -                          -
        # 综上
        # 只需要判断 pen_origin_vector 的dx符号,为正就是从小到大,为负就是从大到小
        # 为0就判断dy的符号,为正就是dy从小到大,为负就是从大到小

        inter_data = self.interaction_data_point_location
        print(f'===待处理信息===\n{dict(islice(inter_data.items(),3))}...')

        # data = {
        #     'id': [1, 2, 3],
        #     'point': [[3, 30], [1, 10], [2, 20]]
        # }
        # df = pd.DataFrame(data)
        # # 使用 key 参数指定一个函数，该函数从每个元素中提取用于排序的值（索引 0）
        # sorted_df = df.sort_values(by='point', key=lambda col: col.apply(lambda p: p[0]))
        # print(sorted_df)

        reverse_data:dict = {}
        # line_id 例: (a,b) --> girds_data[a]['girds'][b]
        for point, line_id_list in inter_data.items():
            for line_id in line_id_list:

                if not isinstance(line_id, tuple):
                    line_id = tuple(line_id)  # 防止传入的是列表导致错误

                if line_id not in reverse_data:
                    reverse_data[line_id] = []
                reverse_data[line_id].append(point)

        for line_id, points in reverse_data.items():
            data_id, girds_id = line_id[0], line_id[1]
            line = self.girds_data[data_id]['girds'][girds_id]
            direction_vector = line['direction_vector']
            dx, dy = direction_vector

            points = np.array(points)
            if not dx == 0:
                sorted_indices = np.argsort(np.sign(dx) * points[:, 0])  # 根据x坐标
            elif not dy == 0:
                sorted_indices = np.argsort(np.sign(dy) * points[:, 1])  # 根据y坐标
            else:
                continue
            sorted_points = points[sorted_indices].tolist()
            reverse_data[line_id] = sorted_points


        self.interaction_data_line_id = reverse_data

        print(f'\n===倒字典排序===\nself.interaction_data_line_id:{dict(islice(reverse_data.items(), 1))}...')


    @staticmethod
    def get_tilling_information(gird_origin_vectors, vectors):
        """
        获得单个Tilling的形状
        返回一个顺时针的Tilling的边的集合,根据顺序可以拼接出闭合的多边形
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
            temp_list: list[tuple | list] = [[None]] * sides * 2

            for i, the_vector in enumerate(the_origin_vectors):
                if the_vector in vectors_set:
                    temp_list[2 * i] = the_vector
                    temp_list[(2 * i + sides) % (sides * 2)] = (-the_vector[0], -the_vector[1])
            tilling_vectors = [a_vector for a_vector in temp_list if a_vector[0] is not None]

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
        tilling_dict_positive = {}
        tilling_dict_negative = {}
        # {(tuple(vectors[0])): [tilling[-1], tilling[0]]}
        for t, vector in enumerate(tilling_vectors, start=0):
            if tuple(vector) in vectors_set:
                tilling_dict_positive[tuple(vector)] = [tilling[t - 1], tilling[t]]
            else:
                tilling_dict_negative[tuple(vector)] = [tilling[t - 1], tilling[t]]
        return tilling_dict_positive, tilling_dict_negative

    def splice_tilling(self, interaction_point_location, spliced_inter=()):
        """

        """
        tem = Tools2D()
        spliced_inter = [list(i) for i in list(spliced_inter)]
        data_point = self.interaction_data_point_location
        o_vector = [i['origin_vector'] for i in self.girds_data]
        if isinstance(interaction_point_location, list):
            interaction_point_location = tuple(interaction_point_location)
        print(f'splice_tilling输入:{interaction_point_location}')
        if not interaction_point_location in data_point:
            raise ValueError(f"interaction_data_point_location中未找到点{interaction_point_location}")

        inter_lines_index_num: list[int, int] = data_point[interaction_point_location]
        now_vector: list[tuple[int | float]] = [tuple(o_vector[i]) for i, _ in inter_lines_index_num]
        # 获取自己的tilling形状
        o_positive_sides, o_negative_sides = self.get_tilling_information(o_vector, now_vector)
        origin_tilling: dict[tuple:list[list]] = o_positive_sides | o_negative_sides
        return_list = list(origin_tilling.values())
        # 查询正方向的点和负方向的点
        data_line_id = self.interaction_data_line_id

        next_points_list: list[tuple[list, bool]] = []
        for line_id in inter_lines_index_num:
            list_index = data_line_id[line_id].index(list(interaction_point_location))
            # 查询字典中的前后,字典中已经按照线的方向顺序排好了
            _next: list[tuple[int, bool]] = [(1, True), (-1, False)]
            for i, b in _next:
                try:
                    next_point = data_line_id[line_id][list_index + i]
                except IndexError:
                    warnings.warn('超出范围')
                    continue
                if not any([next_point in spliced_inter, tuple(next_point) in spliced_inter]):
                    next_points_list.append((next_point, b))
                    # spliced_inter.append(next_point)

        return_info: list[dict] = []
        for next_point, is_positive in next_points_list:
            next_vectors = [tuple(o_vector[index]) for index, _ in data_point[tuple(next_point)]]
            next_positive_sides, next_negative_sides = self.get_tilling_information(o_vector, next_vectors)
            next_sides = next_positive_sides | next_negative_sides

            target_side = set(now_vector) & set(next_vectors)
            if len(target_side) == 1:
                target_side = target_side.pop()
            else:
                warnings.warn(f'存在不止一条共线,当前的拼块的向量信息:{now_vector},下一个拼块{next_vectors}')
                continue
                # target_side = random.choice(list(target_side))
                # raise ValueError(f"获取到不止一条的共线,无法拼接:{target_side}")

            if is_positive:
                up_sign = 1
            else:
                up_sign = -1
            # 因为是正方向, 正向量形成的点和下一个的负方向对齐,负方向反之 负方向对应的线和next正方向的对其

            collinear_in_now = origin_tilling[(up_sign * target_side[0], up_sign * target_side[1])]
            collinear_in_next = next_sides.pop((-up_sign * target_side[0], -up_sign * target_side[1]))

            # 因为方向相反,交叉求shift距离
            t_now, _ = collinear_in_now
            _, t_next = collinear_in_next
            shift_vector = [t_now[0] - t_next[0], t_now[1] - t_next[1]]
            return_info.append({'shifted': shift_vector, 'spliced_inter': next_point})
            new_seg_line_list = list(next_sides.values())
            for segment_line in new_seg_line_list:
                # 平移到指定位置来和now_tilling拼合
                return_list.append(tem.point_shift(segment_line, shift_vector))
        # print(spliced_inter)
        # print(f'splice_tilling:{return_list}')
        return return_info, return_list
    def create_tilling(self, start_inter_point: tuple, num=10):

        now_tilling = []
        used_points = []
        next_depth_points_info:list[dict] = [{'shifted': [0, 0], 'last_shifted': [0, 0], 'spliced_inter': start_inter_point}]

        for this_dict in next_depth_points_info:
            return_info, return_tilling = self.splice_tilling(this_dict['spliced_inter'], used_points)
            if not (return_info or return_tilling):
                warnings.warn('缺少返回值')
                continue
            used_points.append(this_dict['spliced_inter'])
            print(f'刚刚进行了splice_tilling:{this_dict['spliced_inter']},获得信息{return_info}')
            return_tilling_shifted = [Tools2D.point_shift(i, this_dict['last_shifted']) for i in return_tilling]
            now_tilling = now_tilling + return_tilling_shifted

            for next_point_dict in return_info:
                next_point_dict['last_shifted'] = Tools2D.point_shift(this_dict['last_shifted'],
                                                                      next_point_dict['shifted'])
            return_tilling_shifted = [Tools2D.point_shift(i, this_dict['last_shifted']) for i in return_tilling]
            now_tilling = now_tilling + return_tilling_shifted
            for next_point_dict in return_info:
                next_point_dict['last_shifted'] = Tools2D.point_shift(this_dict['last_shifted'],
                                                                      next_point_dict['shifted'])
                next_depth_points_info.append(next_point_dict)

            num = num - 1
            if num <= 0:
                break
        return now_tilling



    @staticmethod
    def create_origin_vector_numpy(sides, radius=10):
        """
        side:边的数量(顶点的数量)
        radius:几何对象的半径
        """
        if sides < 3:
            raise ValueError ("sides小于3,无法生成")
        angles_group = np.linspace(0, stop=2 * np.pi, num=sides, endpoint=False)
        # np.linspace 用于创建等间距的数值序列。 "linear space"（线性空间）
        x = np.cos(angles_group) * radius
        y = np.sin(angles_group) * radius
        back_nparray = np.column_stack([x, y])
        # all the input arrays must have same number of dimensions维度
        return back_nparray

    def create_gird(self, sides=5, origin_norm=80, shifted_distance=0, gap:int|list|tuple=100, center=(100, 100), max_num_of_line=50):
        """
        此函数用于创建一个指定参数的网格系统。

        参数:
        - sides: 网格的边数 (默认值为 5)。
        - origin_norm: 初始向量的模 (长度) (默认值为 80)。
        - shifted_distance: 向量 初始的平移距离 (默认值为 0)。
        - gap: gird内部的间距。可以是list,tuple指定每个girds的间距,int默认间距相等
        - center: 网格中心的坐标 (默认值为 (100, 100))。
        - max_num_of_line: 网格中的最大线条数 (默认值为 50)。
        返回bool:
           是否发生了项目改变,如果改变,需要重新完整的计算interaction
        """

        if not isinstance(gap,(list,tuple)):
            gap=[gap]*sides
        elif len(gap)!=sides:
            raise ValueError(f"gap输入错误:{gap}")

        # 创建一组origin_vectors
        vectors_origin = BruijnsSystem.create_origin_vector_numpy(sides, origin_norm)
        # 取vector的垂直向量vector_pen
        vectors_origin_pen = Tools2D.vector_group_rotate_np(vectors_origin, 90).tolist()
        vectors_origin = vectors_origin.tolist()

        # 定义有向直线origin_directed_line:0
        self.tools.reset()
        for d_v in vectors_origin_pen:
            self.tools.directed_line_drop(location_point=center, direction_vector=d_v)
        line_key_list = list(self.tools.line_dic.keys())
        for index, line_id in enumerate(line_key_list):  # 根据distance平移
            # TODO 此处模长可以不用以相同数值平移,可以存在长度差,应该再增加一个参数调整长度差
            distance_shift_vector = self.tools.vector_change_norm(vectors_origin[index],
                                                                  shifted_distance)
            self.tools.line_shift(line_id, distance_shift_vector, rewrite=True, drop=False)
        origin_directed_lines_list = list(self.tools.line_dic.values())

        #避免重新完整生成
        tittle = self.data_df.columns
        key_is_in = all(a_key in tittle for a_key in ['gap',0])
        end_num = (max_num_of_line - sides) // (2 * sides) + 1
        if key_is_in and origin_directed_lines_list == self.data_df.loc[:,0].tolist() and gap == self.data_df['gap'].tolist():
            is_main_changed = False
            if  vectors_origin != self.data_df['origin_vector'].tolist() :
                self.data_df['origin_vector'] = vectors_origin #norm发生变化,会导致这种情况
            now_num_list = tittle[tittle.get_loc(0):]
            now_num = max(now_num_list)
            if now_num >= end_num:
                del_tar = [num for num in now_num_list if abs(num)>end_num-1]
                print(f'当前项目减少,删除多余的line_num:{del_tar}')
                self.data_df.drop(columns=del_tar,inplace=True)
                start_num = end_num
            else:
                start_num = now_num + 1
                print(f'当前已创建:{now_num_list} start_num:{start_num}')
        else:
            is_main_changed = True
            self.data_df = pd.DataFrame()
            self.data_df['origin_vector'] = vectors_origin
            self.data_df['gap'] = gap
            self.data_df.loc[:, 0] = origin_directed_lines_list  # 创建origin_d_line
            start_num = 1

        #生成一个shift倍数的列表,准备遍历
        list_positive = np.arange(start_num, end_num)
        target_list = list_positive.tolist()+(-list_positive).tolist()
        self.data_df = self.data_df.reindex(columns=list(self.data_df.columns)+target_list, fill_value={})
        #=============================== main ===============================
        # 平移gird_0，构建平行网格gird
        for index, line_dict in self.data_df.loc[:, 0].to_dict().items():  # 遍历原始gird每一条线
            for i in target_list:
                o_v = self.data_df['origin_vector'][index]
                shift_distance = gap[index] * i
                shift_vector = self.tools.vector_change_norm(o_v, shift_distance)
                line_detail = self.tools.line_shift(line_dict, shift_vector, rewrite=False, drop=False)
                self.data_df.at[index,i] = line_detail  # 命名方式1,2,3...
        # =============================== main ===============================
        return is_main_changed

def pd_print(df:pd.DataFrame):
    """
       打印整个DataFrame，不论其大小。
    """
    print(tabulate(df, headers='keys', tablefmt='psql'))

def deep_get_size(obj, seen=None):
    """
    递归计算对象的深层内存大小 (单位: 字节)
    """
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        size += sum([deep_get_size(v, seen) + deep_get_size(k, seen) for k, v in obj.items()])
    elif isinstance(obj, (list, tuple, set, frozenset)):
        size += sum([deep_get_size(item, seen) for item in obj])
    # 可以根据需要添加其他容器类型的处理，例如自定义对象
    return size

if __name__ == "__main__":
    a=BruijnsSystem(sides=5, shifted_distance=10, max_num_of_line=450)
    pd_print(a.data_df)
    a.get_girds_interaction()
