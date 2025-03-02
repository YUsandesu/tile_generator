from the_control import *
from YuSan_PY5_Toolscode import *
import pandas as pd

class BruijnsTilling:
    def __init__(self,girds_data=None,sides=5,shifted_distance=50,gap=100,center=(100, 100),num_of_line=15):
        if girds_data:
            self.girds_data = girds_data
        else:
            self.girds_data = self.create_gird(sides=sides,shifted_distance=shifted_distance,gap=gap,center=center,num_of_line=num_of_line)
        self.interaction_data_point_location: dict[tuple[float | int]:list[int]] ={} # 按坐标点聚合的线段id信息
        self.interaction_data_line_id: dict[tuple[int]:list[float | int]] ={} # 按线段id聚合的坐标点信息
        self.get_girds_interaction()
        print(f'共有:{len(self.interaction_data_point_location)}个点')


    def get_girds_interaction(self):
        """
        查找两个line字典之间的所有焦点
        输入值:((vector):{0:line_dict,1:xx,-1:xx},():{0:xx,1:xx,-1:xx})
        输出值:{ (p_x,p_y):[{v:v,n:n},{v_info}],[_x,_y]:[...],.. }
        最后自动按照向量方向来排序(从反方向-->正方向排队)
        """
        from YuSan_PY5_Toolscode import Tools2D
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
            temp_list:list[tuple|list] = [[None]] * sides * 2

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
        #{(tuple(vectors[0])): [tilling[-1], tilling[0]]}
        for t, vector in enumerate(tilling_vectors, start=0):
            if tuple(vector) in vectors_set:
                tilling_dict_positive[tuple(vector)] = [tilling[t - 1], tilling[t]]
            else:
                tilling_dict_negative[tuple(vector)] = [tilling[t - 1], tilling[t]]
        return tilling_dict_positive,tilling_dict_negative

    # def get_next_

    def splice_tilling(self,interaction_point_location,spliced_inter=()):
        """

        """
        # <think>一个交点具有两个向量,相应的具有:四个方向
        tem = Tools2D()
        spliced_inter=[list(i)for i in list(spliced_inter)]
        data_point = self.interaction_data_point_location
        o_vector = [i['origin_vector'] for i in self.girds_data]
        if isinstance(interaction_point_location,list):
            interaction_point_location=tuple(interaction_point_location)
        print(f'splice_tilling输入:{interaction_point_location}')
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
            _next:list[tuple[int, bool]] = [(1,True),(-1,False)]
            for i,b in _next:
                try:next_point = data_line_id[line_id][list_index+i]
                except IndexError:
                    warnings.warn('超出范围')
                    continue
                if not any([next_point in spliced_inter,tuple(next_point) in spliced_inter]):
                    next_points_list.append((next_point,b))
                    # spliced_inter.append(next_point)

        return_info:list[dict] = []
        for next_point,is_positive in next_points_list:
            next_vectors = [tuple(o_vector[index]) for index,_ in data_point[tuple(next_point)]]
            next_positive_sides,next_negative_sides = self.get_tilling_information(o_vector,next_vectors)
            next_sides = next_positive_sides|next_negative_sides

            target_side = set(now_vector)&set(next_vectors)
            if len(target_side)==1:
                target_side = target_side.pop()
            else:
                warnings.warn(f'当前的拼块的向量信息:{now_vector},下一个拼块{next_vectors}')
                continue
                # target_side = random.choice(list(target_side))
                # raise ValueError(f"获取到不止一条的共线,无法拼接:{target_side}")

            if is_positive:up_sign = 1
            else:up_sign = -1
            # 因为是正方向, 正向量形成的点和下一个的负方向对齐,负方向反之 负方向对应的线和next正方向的对其

            collinear_in_now =  origin_tilling[(up_sign*target_side[0],up_sign*target_side[1])]
            collinear_in_next = next_sides.pop( (-up_sign*target_side[0], -up_sign*target_side[1]) )

            #因为方向相反,交叉求shift距离
            t_now, _ = collinear_in_now
            _,t_next = collinear_in_next
            shift_vector = [t_now[0] - t_next[0], t_now[1] - t_next[1]]
            return_info.append({'shifted':shift_vector,'spliced_inter':next_point})
            new_seg_line_list = list(next_sides.values())
            for segment_line in new_seg_line_list:
                #平移到指定位置来和now_tilling拼合
                return_list.append(tem.point_shift(segment_line, shift_vector))
        # print(spliced_inter)
        # print(f'splice_tilling:{return_list}')
        return  return_info,return_list

    def create_tilling(self,start_inter_point:tuple,num=10):

        now_tilling = []
        used_points = []
        next_depth_points_info = [{'shifted':[0,0],'last_shifted':[0,0],'spliced_inter':start_inter_point}]

        for this_dict in next_depth_points_info:
            return_info,return_tilling = self.splice_tilling(this_dict['spliced_inter'],used_points)
            if not (return_info or return_tilling):
                warnings.warn('缺少返回值')
                continue
            used_points.append(this_dict['spliced_inter'])
            print(f'刚刚进行了splice_tilling:{this_dict['spliced_inter']},获得信息{return_info}')
            return_tilling_shifted = [Tools2D.point_shift(i, this_dict['last_shifted']) for i in return_tilling]
            now_tilling = now_tilling + return_tilling_shifted

            for next_point_dict in return_info:
                next_point_dict['last_shifted']=Tools2D.point_shift(this_dict['last_shifted'],next_point_dict['shifted'])
            return_tilling_shifted = [Tools2D.point_shift(i, this_dict['last_shifted']) for i in return_tilling]
            now_tilling = now_tilling + return_tilling_shifted
            for next_point_dict in return_info:
                next_point_dict['last_shifted']=Tools2D.point_shift(this_dict['last_shifted'],next_point_dict['shifted'])
                next_depth_points_info.append(next_point_dict)

            num = num -1
            if num <= 0:
                break
        return now_tilling

    # shifted_distance default value?
    @staticmethod
    def create_gird(sides, shifted_distance=0, gap=100, center=(100, 100), num_of_line=50):
        """
        此函数用于创建一组网格系统
        distance：初始向量取垂直线以后，相互远离的距离。
        zoom：每条网格线相隔的距离
        返回一个列表，每个列表中包含一个方向的平行网格线，由所有网格线组成一个gird
        """

        tools = Tools2D()
        # return_girds_data = []

        # 在【0，0】创建一个多边形,返回点集到vector
        vectors_origin = tools.regular_polygon(sides=sides, side_length=30)
        return_girds_data = [{'origin_vector': o_v} for o_v in vectors_origin]
        
        # numpy, scipy, pandas
        return_girds_df = pd.DataFrame(return_girds_data)

        # 取vector的垂直向量vector_pen
        vectors_origin_np = np.asarray(vectors_origin)
        
        theta = np.deg2rad(90)
        rotation_matrix = np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta), np.cos(theta)]
        ])
        print('-' * 40)
        print((rotation_matrix @ vectors_origin_np.T).T)
        print(vectors_origin_np @ rotation_matrix.T)
        print('-' * 40)
        vectors_origin_pen = [tools.vector_rotate(the_vector, 90) for the_vector in vectors_origin]
        print('-' * 40)
        print(vectors_origin_pen)
        print('-' * 40)
        
        # for t, p_o_v in enumerate(vectors_origin_pen):
        #     return_girds_data[t]['pen_origin_vector'] = p_o_v

        return_girds_df['pen_origin_vector'] = (vectors_origin_np @ rotation_matrix.T).tolist() 

        # 定义有向直线:
        for d_v in vectors_origin_pen:
            tools.directed_line_drop(location_point=center, direction_vector=d_v)

        # origin_directed_lines = tools.get_line_dic()
        origin_directed_lines = tools.line_dic
        origin_directed_lines_id = list(origin_directed_lines.keys())
        
        ## origin_directed_lines_id and origin_directed_lines can be obtained from origin_directed_lines.items()
        # origin_directed_lines_id = []
        # origin_directed_lines_temp = []
        # for key, value in origin_directed_lines.items():
        #     origin_directed_lines_id.append(key)
        #     origin_directed_lines_temp.append(value)

        # origin_vector.index == vectors_origin[times]
        temp_result = []
        for times, origin_line_id in enumerate(origin_directed_lines_id):
            # 按照vector的方向,改变vector的模长-->获得平移向量distance_vector
            # TODO 此处模长可以不用以相同数值平移,可以存在长度差,应该再增加一个参数调整长度差
            distance_shift_vector = tools.vector_change_norm(vectors_origin[times], shifted_distance)
            temp_result.append(distance_shift_vector)
            # return_girds_data[times]['shift_vector_based_distance'] = distance_shift_vector
            tools.line_shift(origin_line_id, distance_shift_vector, rewrite=True, drop=False)
        return_girds_df['shift_vector_based_distance'] = temp_result # enumerate can be removed

        origin_directed_lines = list(origin_directed_lines.values())  # 取出的直线数据,准备平移
        for t, o_d_line in enumerate(origin_directed_lines):
            return_girds_data[t]['origin_directed_line'] = o_d_line
        return_girds_df['origin_directed_line'] = origin_directed_lines 
        print(return_girds_df.head())
        # -------------------------------------------------------------------------------------------------- #    
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

def setup():
    py5.size(500, 500)
    s_v= screen_axis(0,0)
    for seg_line in tilling_data:
        A_P,B_P=tool.point_shift(seg_line,s_v)
        tool.Segmentline_drop(A_P, B_P)
    load()
    slider('num1', [50, py5.height - 120], value=0, range_val=[0, 10],size=[400,30])
    slider('num2', [50, py5.height - 80], value=0, range_val=[0, 1000], size=[400, 30])
def draw():
    global  tilling_data
    s_v = screen_axis(0, 0)
    py5.background(155)
    back = slider_value()
    if back is not None:
        tool.reset()
        tilling_data = till.create_tilling(the_p, num=back['num1']+back['num2'])
        for seg_line in tilling_data:
            A_P, B_P = tool.point_shift(seg_line, s_v)
            tool.Segmentline_drop(A_P, B_P,color=py5.color(0,0,0,90))

    screen_draw_SegmentLine(tool.get_Segmentline_dic(),0)

if __name__ == "__main__":
    tool = Tools2D()
    till = BruijnsTilling(sides=5, num_of_line=30)
    the_p = till.interaction_data_line_id[(0, 0)][60]
    print(f'选取交点:{the_p}')
    tilling_data = till.create_tilling(the_p, num=0)
    py5.run_sketch()
