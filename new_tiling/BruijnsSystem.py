import random
import sys
import time

from new_tiling.PY5_2DToolkit import Tools2D
import numpy as np
import pandas as pd
import warnings
from itertools import islice,product
from tabulate import tabulate
import humanize


class BruijnsSystem:
    def __init__(self, sides=5, origin_norm=80, shifted_distance=0, gap=100, center=(100, 100), max_num_of_line=50):
        self.tools = Tools2D()
        self.data_df = pd.DataFrame()
        self.inter_df = pd.DataFrame()
        self.sorted_df = pd.DataFrame()
        self.map_pd = pd.DataFrame

    def get_girds_interaction(self,rebuild=True):
        """
        查找所有焦点
            此方法用于查找并计算不同 'gird' （网格线组）之间所有线段的交点。
            它遍历数据 DataFrame 中表示不同 'gird' 的列，并两两比较 'gird' 内的线段，
            使用 `intersection_2line` 方法计算线段交点。
            所有找到的交点将被存储在临时字典中，并最终转换为 DataFrame 格式。
        参数:
            rebuild:是否重新完整重建inter_df,可以传入create_gird的返回值
        self.inter_df:
            包含线段交点信息的 DataFrame.列和索引均为多级索引.
            第一级索引表示 'gird' 的索引，第二级索引表示该层gird中有向直线的编号(line_num)。
            值表示交点坐标[float,float]。可以通过.loc[(index,num),(index,num)]查询任意两条线的交点
        """
        df_col = self.data_df.columns
        d_col = df_col[df_col.get_loc(0):]  # line的id列表

        # 生成当前所有线段标识符（index, num）
        col = list(product(range(len(self.data_df)), d_col))
        # 获取对应的线段数据
        lines_np = self.data_df.loc[:, d_col].to_numpy().flatten()
        lines = lines_np.tolist()

        if rebuild:
            inter_inf = np.around(self.tools.inter_line_group_np(lines_a=lines, lines_b=lines), 10)
            self.inter_df = pd.DataFrame(inter_inf.tolist(), columns=col, index=col)
            pd_print(self.inter_df)
        else:
            last_col = self.inter_df.columns.tolist()
            last_num = len(last_col)
            now_num = len(col)
            if now_num>last_num:
                last_col_np = np.array(last_col)
                col_np = np.array(col)

                last_col_np_mat = last_col_np[:,np.newaxis,:] #nx1x2
                col_np_mat  = col_np[np.newaxis,:,:] #1xmx2

                col_mask = (last_col_np_mat==col_np_mat).all(axis=2).any(axis=0) #nxmx2 得到的是col_np_mat的mask
                index = np.where(~col_mask)[0]

                new_col = [c for t,c in enumerate(col) if t in index] #因为列名必须是数组形式,只能这么转换回来.
                lines_new= lines_np[index].tolist()

                inter_inf = np.around(
                    self.tools.inter_line_group_np(lines_a=lines, lines_b=lines_new), 10
                )
                new_df = pd.DataFrame(inter_inf.tolist(), index=col, columns=new_col)

                # 合并 new_df 与 new_df.T，生成一个包含两边信息的 DataFrame
                symmetric_new_df = new_df.combine_first(new_df.T)

                # 只用一次 combine_first 更新 self.inter_df
                self.inter_df = self.inter_df.combine_first(symmetric_new_df)

            else:
                tar_i = set(last_col) - set(col)
                tar_i = list(tar_i)
                self.inter_df.drop(index=tar_i,columns=tar_i,inplace=True)
    def _sort_girds_interaction(self):
        """
        Bruijns 系统中基于交点建立网格线邻接关系的关键预处理步骤。
        `self.inter_sorted_df` 中排序和组织的交点数据支持后续依赖网格网络有序遍历的算法，如路径查找、图构建或网格连通性特征提取。

        排序逻辑:
            - 主排序键: 交点坐标 (x, y)。利用 `numpy.unique` 默认排序，按 x 坐标升序，x 相等时按 y 升序。
            - 方向调整: 对于 x 方向分量为负，或 x 分量为零且 y 分量为负的线段，排序顺序反转，确保与预期遍历方向一致。

        输出数据结构 (`self.inter_sorted_df`):
            一个 pandas DataFrame，其中:
                - 列: 网格线标识符（元组）。
                - 值: 按线段方向排序的交点信息列表，每项为以下之一:
                    - `None`: 占位符，用于保持 DataFrame 形状。
                    - `[line_index]`: 单条线在此点相交。
                    - `[line_index_1, line_index_2, ...]`: 多条线在此点相交。
        """
        def get_direction(l_id:tuple)->tuple:
            """
            根据direction_vector来确定直线走向。
            定义如下：
            - +x, +y（x递增）
            - -x, +y（x递减）
            - -x, -y（x递减）
            - +x, -y（x递增）
            该函数返回一个包含向量 x 和 y 分量符号的元组，用于指示向量在其象限中的方向。

            参数:
            line_tuple (tuple): 包含线条索引的元组。

            返回:
            tuple: 一个包含方向向量 x 和 y 分量符号（sx, sy）的元组。
            """
            line_dict = self.data_df.loc[l_id[0],l_id[1]]
            d_vector = line_dict['direction_vector']
            return np.sign(d_vector[0]),np.sign(d_vector[1])
        inter_data = self.inter_df

        lines_index = inter_data.index
        inter_dict = inter_data.to_dict(orient='list')  # 这里可以加.apply(map)把nan换成二维的[nan,nan]
        walk_dict = {}

        data_col = self.data_df.columns
        line_list = data_col[data_col.get_loc(0):]  # line的id列表
        min_deep:int = len(inter_data)-len(line_list)

        for line_id,inter_list in inter_dict.items():
            arr = np.array(inter_list)
            s_x,s_y=get_direction(line_id)
            queue_p,indices,counts = np.unique(arr, axis=0, return_index=True, return_counts=True)
            # queue_p: 排序后的队列 (去重, 默认以 [x,y] 中的 x 排序, 如果相同, 以 y 排序)
            # indices: queue_p 中元素在原数组 arr 中的序号
            # counts: 每个元素在 arr 中出现的次数
            # 获取没有nan的序号
            valid_mask = np.where(~np.isnan(queue_p).any(axis=1))

            # 同时过滤三个数组
            queue_p = queue_p[valid_mask]  # 过滤后的唯一值坐标
            indices = indices[valid_mask]  # 过滤后的首次出现索引
            counts = counts[valid_mask]  # 过滤后的计数 (形状与queue_p一致)

            same_v = queue_p[counts>1] #取具有重复的点[x,y]
            same_id = indices[counts>1] #重复点的id

            same_id_dict = {
                s_id: np.where((arr == s_v).all(axis=1))[0] #{same_id: line值的index序号}
                for s_id, s_v in zip(same_id, same_v)
            }

            if s_x<0 or (s_x==0 and s_y<0):
                #这两种情况需要取倒序
                indices = indices[::-1]

            walk_dict[line_id] = [
                [lines_index[i]] if i not in same_id_dict
                else [lines_index[e] for e in same_id_dict[i]]
                for i in indices
            ] + [np.nan]* (min_deep-len(indices)) #防止长度不一致.

        self.sorted_df = pd.DataFrame(walk_dict)

    def _vector_map_pd(self)->None:
        """
        根据输入数据data_df中的origin_vector列，计算并生成一个DataFrame。
        DataFrame: 'origin_id','mirror_id','vector'。

        :attributes:
            walking (list): 存储计算后的向量映射关系，包括时钟编号、原始编号、镜像编号和向量。

        调用示例:
        调用示例,查找6的mirror_index:
        self.map_pd.loc[6].index.get_level_values('mirror_id')[0]
        查找mirror_id=5 的 index:
        self.map_pd.xs(5, level='mirror_id').index.get_level_values('origin_id')[0]
        """
        # xs全称是"cross-section"，用于从DataFrame中提取特定的横截面数据。
        # 它通常用于多层索引（MultiIndex），允许通过指定某个索引级别和值来快速选择数据，无需手动拆分索引。

        the_origin_vectors = self.data_df['origin_vector'].to_dict()
        sides = len(the_origin_vectors)

        walking: list = [] # clock_id,origin_id,mirror_id,vector
        if sides % 2 != 0:  # 奇数
            mirror_vector = np.array(list(the_origin_vectors.values()))
            mirror_vector = (-mirror_vector).tolist()
            for index, the_vector in the_origin_vectors.items():
                # 例：sides = 5
                # 圆被分成5个等分，并且存在另外5个镜像等分，总共10个分区
                # 这种排列是由于180°旋转对称导致的
                # 计算：360度/10 = 36度 -> 180度/36度 = 5
                # 索引镜像：列表长度为10，原索引 i 镜像到 (i + 镜像间隔:sides) % 总等分数:sides * 2
                # 例如: 0, 2, 4, 6, 8 分别镜像到: 5, 7, 9, 1, 3
                # 值: 1, 2, 3, 4, 5 分别变为: -1, -2, -3, -4, -5
                walking.append(
                    [index * 2, index, index + sides, the_vector])
                walking.append([(index * 2+ sides) % (sides * 2), index + 5, index, mirror_vector[index]])
            self.map_pd = pd.DataFrame(walking, columns=['clock_id','origin_id','mirror_id','vector'])
            self.map_pd.set_index(['clock_id','origin_id','mirror_id'], inplace=True)
            self.map_pd.sort_index(level='clock_id',inplace=True)
            self.map_pd.index = self.map_pd.index.droplevel('clock_id')
        else:
            # 例: sides = 6 时，向量 0 和 3, 1 和 4, 2 和 5 互为正对
            # 为了避免在初始状态 (shift_distance = 0) 下，walking 和 walking_mirror 选取到重复的向量
            # walking_mirror 的选取需要排除 walking 中已有的向量，并选择 "对位" 的向量
            # "对位" 的向量通过 (i + 镜像间隔:sides//2) % 总等分数:sides 计算得到，它指向与 index 索引向量正对的位置
            walking = [[index, (index + sides // 2) % sides, the_vector]
                       for index, the_vector in the_origin_vectors.items()]
            self.map_pd = pd.DataFrame(walking, columns=['origin_id', 'mirror_id', 'vector'])
            self.map_pd.set_index(['origin_id', 'mirror_id'], inplace=True)

    def _get_tilling_shape(self, vectors_id_list):
        """
        Get the shape of a single tiling pattern.

        这个函数计算并返回一个字典,将vector IDs映射到对应的坐标点,这些坐标点按顺时针顺序形成一个闭合多边形。

        Args:
            vectors_id_list: 一个id列表

        Returns:
            dict: 一个字典,将vector IDs 映射到segment。
                  坐标点是通过vector的累加和计算得到的,形成一个闭合多边形。
                  格式: {vector_id: segment。}
                  其中segment。是一个[x, y]坐标的列表
        """
        enable_map = self.map_pd[(self.map_pd.index.get_level_values('origin_id').isin(vectors_id_list)) | (self.map_pd.index.get_level_values('mirror_id').isin(vectors_id_list))]
        enable_vectors = enable_map['vector'].tolist()
        enable_id = enable_map.index.get_level_values('origin_id').tolist()
        # enable_vectors只是移动的路径,需要绘制成坐标点
        cumulative_sum = np.cumsum(np.array(enable_vectors), axis=0)
        tilling = Tools2D.reduce_errors_np(cumulative_sum,max_value=False).tolist()# 防止出现无穷小数
        return {enable_id[t]:i for t,i in enumerate(tilling)}

    def get_start_p(self)->tuple[tuple,int]:
        """
        函数功能:
            从 self.inter_df 中筛选出列名第一个元素为 0 的列，
            然后计算这些列中各行与坐标 [100, 100] 的欧几里得距离，
            最后返回距离最小值对应的 (行索引, 列名称)。

        返回:
            (row_index, column_name) -> tuple[tuple,tuple]
        """

        # 将所有列名转换为 NumPy 数组
        p_col = self.inter_df.columns.to_numpy()

        # 创建一个向量化函数，用于获取列名的第一个元素
        # 假设列名可迭代并且第一个元素可以被索引到
        extract_first_elem = np.vectorize(lambda x: x[0])

        # 提取所有列名中的第一个元素
        first_elements = extract_first_elem(p_col)

        # 在 first_elements 中查找等于 0 的索引位置
        indices = np.where(first_elements == 0)

        # 根据索引拿到对应的列名，转换为列表
        target_columns = p_col[indices].tolist()

        # 获取这些目标列的数据并转换为 NumPy 数组
        data_array = np.array(self.inter_df.loc[:, target_columns].to_numpy().tolist())

        # 计算与点 [100, 100] 的欧几里得距离（按行计算）
        distances = np.linalg.norm(data_array - np.array([100, 100]), axis=-1)

        # 获取距离最小值在展平后的索引位置
        flat_min_index = np.nanargmin(distances)

        # 将展平索引转换为 (行, 列) 的二维索引
        min_row_idx, min_col_idx = np.unravel_index(flat_min_index, distances.shape)

        # 获取对应的行索引和列名
        row_index = self.inter_df.index[min_row_idx]
        col_name = target_columns[min_col_idx]

        s_i = np.where(self.sorted_df.loc[:, col_name].apply(lambda x: row_index in x if isinstance(x, list) else False))
        print(f'start:{col_name,s_i[0][0]}')
        # 返回最小值对应的 (行索引, 列名称)
        return col_name,int(s_i[0][0])


    def walk_in_line(self,loc:list[tuple[int, int] | int]):
        """
        loc的形式: [line_id,index(在sorted_df中的index)]
        """
        self._vector_map_pd()
        id_tup,index =loc
        # 定义要筛选的列表
        my_list: list = self.sorted_df.loc[index,id_tup]
        print('my_list',my_list)
        o_n = self.sorted_df.loc[[index+1,index-1],id_tup].tolist()
        # mr = self.map_pd.xs(id_tup[0], level='origin_id').index.get_level_values('mirror_id')[0]
        # print(mr)
        # next_way = {id_tup[0]:o_n[0]+[id_tup],mr:o_n[0]+[id_tup]}
        next_way = {id_tup: o_n}
        print('o_nex_all',next_way)
        for i in my_list:
            print('开始查找',i)
            s_i=np.where(self.sorted_df.loc[:,i].dropna().apply(lambda x:id_tup in x))[0][0]
            #TODO 这里要判断s_i是否=0 不然会超出范围
            next_walk = self.sorted_df.loc[[s_i+1,s_i-1],i].to_list() #有时候因为没有生成新的 出现nan值
            next_way[i]= next_walk
            # mr = self.map_pd.xs(i[0], level='origin_id').index.get_level_values('mirror_id')[0]
            # next_way[mr] = next_walk[1]+[i]
        print('next_way:',next_way)

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
        o_positive_sides, o_negative_sides = self._get_tilling_shape(o_vector, now_vector)
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
            next_positive_sides, next_negative_sides = self._get_tilling_shape(o_vector, next_vectors)
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
        return Tools2D.reduce_errors_np(back_nparray)

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
                if 0 in del_tar:del_tar.remove(0) #TODO 这里有点蠢
                # print(f'当前项目减少,删除多余的line_num:{del_tar}')
                self.data_df.drop(columns=del_tar,inplace=True)
                start_num = end_num
            else:
                start_num = now_num + 1
                # print(f'当前已创建:{now_num_list} start_num:{start_num}')
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

    def get_gird_lines_list(self):
        tittle = self.data_df.columns
        now_num_list = tittle[tittle.get_loc(0):]
        return self.data_df.loc[:, now_num_list].values.tolist()

def pd_print(df: pd.DataFrame, max_length=20, multi_index=False):
    """
    打印整个DataFrame，不论其大小，长值会被从中间缩略显示。

    :param df: 需要打印的 DataFrame
    :param max_length: 字符串的最大显示长度
    :param multi_index: 是否显示多级索引
    """

    def truncate_middle(val):
        # def format_float(n):
        #     if isinstance(n, float):
        #         rounded = round(n, 2)
        #         # 去掉末尾的无用零和小数点
        #         str_val = f"{rounded:.2f}".rstrip('0').rstrip('.')
        #         # 如果原数值在最后一个有效位数之后还有更多小数，加上'..'
        #         if len(f"{n:.15f}".split('.')[-1].rstrip('0')) > 2:
        #             return f"{str_val}.."
        #         return str_val
        #     return n
        #
        # if isinstance(val, (list, tuple, np.ndarray)):
        #     formatted_val = [format_float(n) for n in val]
        #     # 将所有元素转换为字符串然后拼成一个字符串，并用 [] 包起来
        #     val_str = "[" + ", ".join(map(str, formatted_val)) + "]"
        #
        #     return val_str
        val_str = str(val)
        if len(val_str) > max_length:
            half_length = (max_length - 3) // 2
            return val_str[:half_length] + '...' + val_str[-half_length:]
        return val_str
    df_shortened = df.apply(lambda col: col.map(lambda x: truncate_middle(x)))
    if multi_index:
        df_shortened.reset_index(inplace=True)
        print(tabulate(df_shortened, headers='keys', tablefmt="pretty", showindex=False))
    else:
        print(tabulate(df_shortened, headers='keys', tablefmt="pretty")) #orgtbl #presto #pretty #github

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
    a=BruijnsSystem()

    a.create_gird(sides=5,max_num_of_line=20,shifted_distance=0)
    a.get_girds_interaction()
    a.create_gird(sides=5, max_num_of_line=100, shifted_distance=0)
    a.get_girds_interaction(rebuild=False)
    pd_print(a.inter_df)
    a._sort_girds_interaction()
    a.get_start_p()
    pd_print(a.sorted_df, max_length=1000)
    a.walk_in_line([(0, -5),15])
    # print(a.inter_df.at[(2, 0), (4, 0)])
    # print(a.inter_df.at[(2, 0), (3, 0)])
    # print(a.inter_df.at[(2, 0), (1, 0)])
    #
    # print(a.inter_df.at[(2, -5), (0, 3)])
    # print(a.inter_df.at[(4, 5), (0, 3)])

    # print(a.map_pd.index.get_level_values('mirror_index'))
    # example_point = a.inter_df.loc[(0,1),(1,1)]


    # print())
    # print(example_point)
