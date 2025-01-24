from os import remove

import numpy as np
import py5
from collections import defaultdict
import math
import random

from docutils.utils.math.latex2mathml import letters
from py5 import point
from sympy.series.gruntz import rewrite


class Tools2D:
    """
    有向线段（Directed Segment）：它是一个具体的几何对象，表示从一个起点到一个终点的线段，并且明确指出了方向（从起点到终点）。
    """
    def __init__(self):
        self.point_dic = {}  # 存储点的字典
        self.Segmentline_dic = {}  # 存储线段的字典
        self.surface_dic = {}  # 存储面的字典
        self.line_dic = {}  # 存储直线的字典
        self.reverse_point_dic = defaultdict(list) #创建储存点的反字典 便于倒查
        # 初始化字母表
        self.alphabetize_Capital = [chr(i) for i in range(65, 91)]  # ASCII 65-90 对应 A-Z
        self.alphabetize = [chr(i) for i in range(97, 123)]  # ASCII 范围 97 到 122
        # 初始化字母队列和索引
        self.letter_queue = self.alphabetize.copy()  # [a,b,c...z]
        self.letter_queue_capital = self.alphabetize_Capital.copy()  # [A,B,C,D...Z]
        self.letter_index = 0  # 字母的后缀序列
        self.letter_index_capital = 0  # 字母的后缀序列
    def clear_letter_mem_capital(self, used):
        """
        清理内存用
        输入已经使用的点的字母代号
        返回一个字典 每个代号对应一个新的名字
        """
        back_dic = {}
        if len(self.letter_queue) < len(used) * 2:
            return None
        for i in used:
            self.back_letter_capital(i)
        new_letter_index = []
        for i in used:
            new_letter = self.extract_letter_capital()
            new_letter_index.append(self.separate_letter(new_letter)[1])
            back_dic[i] = new_letter
        the_max_index = max(new_letter_index)  # 例如最大的是Z100 那么返回100
        for l, the_letter in enumerate(self.letter_queue_capital):
            the_ascii, the_index = self.separate_letter(the_letter)
            if the_index > the_max_index and the_ascii == ord('A'):
                # 如果是A开头的 例如当前遍历A100 我们的max是99 那么就通过
                # 当前遍历B99 我们的max是99 那么因为不是A开头的就会跳过 并且99<100
                del self.letter_queue_capital[l:]
                self.letter_index_capital = the_index - 1
                break
        return back_dic
    def extract_letter_capital(self):
        if not self.letter_queue_capital:
            # 如果字母队列中不够用了
            self.letter_queue_capital.extend([l + str(self.letter_index_capital + 1) for l in self.alphabetize_Capital])
            self.letter_index_capital += 1
        return self.letter_queue_capital.pop(0)  # 删除队列中的第一项并返回
    def back_letter_capital(self, letter):
        the_letter_ascii, the_letter_index = self.separate_letter(letter)
        for list_i, i in enumerate(self.letter_queue_capital):
            i_ascii, i_index = self.separate_letter(i)
            if i_index < the_letter_index:
                # 输入A100 当前查找到A51 列表为[A50,A51,...,A99]
                continue  # 此时应该跳过,寻找下一个
            if i_index == the_letter_index:
                # 输入F10 当前查找到A10 列表为[A10,B10,C10,D10]
                if i_ascii < the_letter_ascii:
                    continue
                if i_ascii > the_letter_ascii:  # 输入F10 当前查找为G10 那么应该插入在G前面
                    self.letter_queue_capital.insert(list_i, letter)  # 当前索引为i_index 插入会把当前项往后推移
                    return
            if i_index > the_letter_index:  # 当前输入A10 列表为[A12,A13,A14...]
                self.letter_queue_capital.insert(list_i, letter)  # 此时插入在当前项(之前)就可以
                return
        # 如果能到达此处 输入A100 当前查找到A51 列表为[A50,A51,...,A99]应该加入到末尾
        self.letter_queue_capital.append(letter)
    def apply_letter_capital(self, letter):
        """
        申请一个指定字母,并从字母表中删除它,成功返回True
        """
        the_ascii, the_index = self.separate_letter(letter)
        if the_index > self.letter_index_capital:
            print("开始创建")
            for i in range(the_index - self.letter_index_capital):
                # 例如输入 A5 当前序号为3:[B3,C3....Z3]在添加两个循环(5-3) 得到[B3...Z5]
                self.letter_queue_capital.extend(
                    [l + str(self.letter_index_capital + 1) for l in self.alphabetize_Capital])
                self.letter_index_capital += 1
        if letter in self.letter_queue_capital:
            self.letter_queue_capital.remove(letter)
            return True
        raise ValueError(f"发生错误,队列为{self.letter_queue_capital},输入值为{letter}")

    #获取大写字母代号
    def clear_letter_mem(self, used):
        back_dic = {}
        if len(self.letter_queue) < len(used) * 2:
            return None
        for i in used:
            self.back_letter(i)
        new_letter_index = []
        for i in used:
            new_letter = self.extract_letter()
            new_letter_index.append(self.separate_letter(new_letter)[1])
            back_dic[i] = new_letter
        the_max_index = max(new_letter_index)  # 例如最大的是Z100 那么返回100
        for l, the_letter in enumerate(self.letter_queue):
            the_ascii, the_index = self.separate_letter(the_letter)
            if the_index > the_max_index and the_ascii == ord('a'):
                # 如果是A开头的 例如当前遍历A100 我们的max是99 那么就通过
                # 当前遍历B99 我们的max是99 那么因为不是A开头的就会跳过 并且99<100
                del self.letter_queue[l:]
                self.letter_index = the_index - 1
                break
        return back_dic
    def extract_letter(self):
        """
        返回提取的字母
        同时从字母表中删除
        """
        if not self.letter_queue:
            # 如果字母队列中不够用了
            self.letter_queue.extend([l + str(self.letter_index + 1) for l in self.alphabetize])
            self.letter_index += 1
        return self.letter_queue.pop(0)  # 删除队列中的第一项并返回
    def back_letter(self, letter):
        the_letter_ascii, the_letter_index = self.separate_letter(letter)
        for list_i, i in enumerate(self.letter_queue):
            i_ascii, i_index = self.separate_letter(i)
            if i_index < the_letter_index:
                # 输入A100 当前查找到A51 列表为[A50,A51,...,A99]
                continue  # 此时应该跳过,寻找下一个
            if i_index == the_letter_index:
                # 输入F10 当前查找到A10 列表为[A10,B10,C10,D10]
                if i_ascii < the_letter_ascii:
                    continue
                if i_ascii > the_letter_ascii:  # 输入F10 当前查找为G10 那么应该插入在G前面
                    self.letter_queue.insert(list_i, letter)  # 当前索引为i_index 插入会把当前项往后推移
                    return
            if i_index > the_letter_index:  # 当前输入A10 列表为[A12,A13,A14...]
                self.letter_queue.insert(list_i, letter)  # 此时插入在当前项(之前)就可以
                return
        # 如果能到达此处 输入A100 当前查找到A51 列表为[A50,A51,...,A99]应该加入到末尾
        self.letter_queue.append(letter)
    def separate_letter(self, letter):
        """
        将输入拆分为两部分:
        第一个字符的ASCII值,数字的int值
        """
        the_letter_index = letter[1:]  # 从'a100'中切片得到index'100' 如果'a' 返回的是''
        the_letter_ascii = ord(letter[0])
        if the_letter_index != '':
            the_letter_index = int(the_letter_index)
        else:
            the_letter_index = 0
        return the_letter_ascii, the_letter_index
    # 获取小写字母代号
    def get_point_dic(self):
        return self.point_dic
    def get_Segmentline_dic(self):
        return self.Segmentline_dic
    def get_line_dic(self):
        return self.line_dic
    def get_surface_dic(self):
        return self.surface_dic

    # ================点线面存取操作================
    # ////////////《点操作》////////////
    def point_drop(self, point_xy,specified=None):
        """
        如果point_xy格式不对会报错
        在reverse_pointdic创建一个(x,y)作为key的倒字典便于搜索
        pecified: 可以输入一个指定字符作为point的名称代号 NONE为自动指定
        :return: 返回新创建point的字母代号 例如：A
        """
        if not self.list_depth(point_xy) == 1 and len(point_xy) == 2:
            raise ValueError(f"输入的坐标异常,为:{point_xy}")  #输入格式[x,y]
        if specified is not None:
            if not isinstance(specified,str):
                raise ValueError(f"指定点名称错误,为:{specified}")  # 输入格式[x,y]
            letter = specified
            if specified in self.point_dic:
                #当前指定的已经创建,进行覆盖操作(先删除再申请)
                self.point_remove_by_letter(specified)
            self.apply_letter_capital(specified)#申请指定点
        else:
            letter = self.extract_letter_capital()
            #未指定点,自动指定一个点
        self.point_dic[letter] = point_xy #加入字典
        self.reverse_point_dic[tuple(point_xy)].append(letter) #加入反字典
        return letter
    def distance_2_points_matrix(self,Apoint,Bpoint):
        """
        矩阵方法求norm 使用的是np矩阵
        """
        A=self.point_get_info(Apoint)['location']
        B=self.point_get_info(Bpoint)['location']
        np_A = np.array(A)
        np_B = np.array(B)
        return np.linalg.norm(np_A - np_B)
    def distance_2_points(self,point1, point2):
        """
        计算两个点之间的距离 经典平方根方法

        参数:
        point1: 通用,既可以是'代号'也可是(x,y)
        point2: 通用,既可以是'代号'也可是(x,y)
        返回:
        两点之间的距离
        """
        x1, y1 = self.point_get_info(point1)['location']
        x2, y2 = self.point_get_info(point2)['location']
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    def point_remove_by_letter(self, aletter):
        """
        删除指定字母对应的点，并将其重新插入到 nowletterlist 中。
        失败返回 False。
        """
        self.back_letter_capital(aletter)
        value=self.point_dic[aletter]
        del self.point_dic[aletter]
        if len(self.reverse_point_dic[tuple(value)])>1:
            #如果列表中内容超过一项,那么有多个点名称同时存在
            re_write=self.reverse_point_dic[tuple(value)]
            re_write.remove(aletter) #从其中删除指定代号
            self.reverse_point_dic[tuple(value)]=re_write #重新覆写回去
        elif len(self.reverse_point_dic[tuple(value)])==1:
            del self.reverse_point_dic[tuple(value)]
        else:
            raise ValueError("删除reverse_pointdic时,发送未知错误")
    def point_remove_by_xy(self, point_xy):
        """
        通过调用point_get_info调用point_remove_by_letter
        失败返回False
        """
        info=self.point_get_info(point_xy)
        if info['letter'] is not None:
            return self.point_remove_by_letter(info['letter'])
        else:
            return False
    def point_drop_group(self, point_xy_group):
        """
        循环调用 point_drop
        :param point_xy_group: [a,b][c,d][e,f]格式不会会报错
        :return: 返回一个代号列表[A,B,C,D]
        """
        back = []
        for i in point_xy_group:
            if not isinstance(i, list):
                if not isinstance(i, tuple):
                    raise ValueError("data is not list or tuple")
            if len(i) == 2:
                back.append(self.point_drop(i))
            else:
                raise ValueError("data is not:([x,y],(x,y),(x,y))")
        return back
    def point_get_info(self, point_xy_or_letter):
        """
        无论输入的是 (x,y) or 字符代号
        统一返回一个字典 包括'type':返回'letter'或者'point_xy'
        'letter':字母代号 如果未找到此项会返回None
        'location':坐标值[x,y]
        如果读取失败(参数输入错误)返回False
        """
        back_dict = {}
        if isinstance(point_xy_or_letter, str) and point_xy_or_letter:
            if point_xy_or_letter not in self.point_dic.keys():
                #输入的字母不在字典中
                return False
            detail_point = self.point_dic[point_xy_or_letter]
            point_x = detail_point[0]
            point_y = detail_point[1]
            letter = point_xy_or_letter
            input_type = 'letter'
        elif isinstance(point_xy_or_letter, (list, tuple, np.ndarray)) and len(point_xy_or_letter) == 2:
            point_x = point_xy_or_letter[0]
            point_y = point_xy_or_letter[1]
            input_type = 'point_xy'
            if tuple(point_xy_or_letter) in self.reverse_point_dic:
                letter = self.reverse_point_dic[tuple(point_xy_or_letter)]
            else:
                letter = None
        else:
            raise ValueError(f"未知错误,输入的点是{point_xy_or_letter}")
        back_dict['type']=input_type
        back_dict['letter']=letter
        back_dict['location']=[point_x,point_y]
        return back_dict
    def point_shift_vector(self, point, vector_Direct, distance):
            """
            point接受点的列表,也接受一个单独的点
            vector仅表示方向
            distance表示移动的距离
            """
            if vector_Direct[0] == 0 and vector_Direct[1] == 0:
                return point

            def shift_point(point, way):
                """
                point:点坐标
                way:路径,一个列表[x,y],第一个是x坐标,第二个是y坐标
                """
                p_x, p_y = point[0], point[1]
                s_x, s_y = way[0], way[1]
                back_x = p_x + s_x
                back_y = p_y + s_y
                return [back_x, back_y]

            depth = self.list_depth(point)
            # 求倍数
            multiple = distance / math.sqrt(vector_Direct[0] ** 2 + vector_Direct[1] ** 2)
            way = [vector_Direct[0] * multiple, vector_Direct[1] * multiple]
            if depth == 1 and len(point) == 2:
                # 输入的是一个点
                back = shift_point(point, way)
                return back
            elif depth == 2:
                # 输入的是一组点
                point_group = []
                for p in point:
                    point_group.append(shift_point(p, way))
                return point_group
            else:
                raise ValueError(f"错误,可能是输入格式不对,point:{point}")

    # ////////////《线操作》////////////
    def Segmentline_drop_by_2pointletter(self, Aletter, Bletter, floor=0, color=py5.color(0, 0, 0, 255), strokeweight=3,
                                         visible=True):
        """
        :param floor: 图层高度
        :param color: 只接受py5.color()之后的数值 否则后面绘制会出错
        :param visible: 是否可视，在绘制辅助线时候可以设置为=False
        """
        inf = {}
        inf["location"] = [list(self.point_dic[Aletter]), list(self.point_dic[Bletter])]

        inf["floor"] = floor
        inf["color"] = color
        inf["stroke_weight"] = strokeweight
        inf["visible"] = visible
        self.Segmentline_dic[Aletter + "-" + Bletter] = inf
    def Segmentline_drop_by_2pointxy(self, Apoint, Bpoint, floor=0, color=py5.color(0, 0, 0, 255), strokeweight=3,
                                     visible=True):
        """
            :param floor: 图层高度
            :param color: 只接受py5.color()之后的数值 否则后面绘制会出错
            :param visible: 是否可视，在绘制辅助线时候可以设置为=False
            :return: 返回一个Chain
            """
        Aletter = self.point_drop(Apoint)
        Bletter = self.point_drop(Bpoint)
        self.Segmentline_drop_by_2pointletter(Aletter, Bletter, floor, color, strokeweight, visible)
        return Aletter + "-" + Bletter

    def Segmentline_remove_by_chain(self, chain):
        del self.Segmentline_dic[chain]

    def line_drop(self, k, b, a=1, temp=False):
        """
        保存一个函数：ay=kx+b
        如果字典detaildic中有'a'键: a肯定是0 k肯定是-1(自动化简) 储存的是x=b 是一个垂直线
        如果字典中 k=0 是y=b 是一个水平线
        :param a: 如果a不是1或0 会报错/#/内容:认定输入的是ay+bx+k=0
        :param temp: 如果为True 那么不创建到字典中 仅返回一个kba字典
        :return: temp=False 返回一个字母代号 例如：a temp=True 不创建到字典中 仅返回一个kba字典
        """
        detaildic = {}
        if a == 0 and k == 0:
            raise ValueError("a和k不能同时为0，请检查输入")
        if a == 0:
            strline = f"x={b / -k}"
            detaildic['str'] = strline
            detaildic['b'] = b / k
            detaildic['k'] = -1
            detaildic['a'] = 0
        if k == 0:
            strline = f"y={b}"
            detaildic['str'] = strline
            detaildic['k'] = 0
            detaildic['b'] = b
        if a == 1 and k != 0:
            if b > 0:
                strline = f"y={k}x+{b}"
            elif b < 0:
                strline = f"y={k}x-{b}"
            elif b == 0:
                strline = f"y={k}x"
            detaildic['str'] = strline
            detaildic['k'] = k
            detaildic['b'] = b
        if a != 0 and a != 1 and a is not None:
            raise ValueError(f"输入不符合要求,a只能是0或1,当前输入:{a}")
            # # ay+bx+c=0
            # k = b / a
            # b = k / a
            # if b > 0:
            #     strline = f"y={k}x+{b}"
            # elif b < 0:
            #     strline = f"y={k}x-{b}"
            # elif b == 0:
            #     strline = f"y={k}x"
            #
            # detaildic['str'] = strline
            # detaildic['k'] = k
            # detaildic['b'] = b
        if temp == True:
            return detaildic
        newletter = self.extract_letter()
        self.line_dic[newletter] = detaildic
        return newletter

    def line_remove(self, letter):
        """
        删除线
        失败返回False
        """
        if letter in self.line_dic:
            del self.line_dic[letter]
            self.back_letter(letter)
        else:
            return False

    def line_to_Segmentline(self, line, x_range=None, y_range=None, floor=0, color=py5.color(0, 0, 0, 255), strokeweight=3,
                            visible=True):
        inputvalue = {'floor': floor, 'color': color, 'strokeweight': strokeweight, 'visible': visible}

        def xrange_to_Segline(range):
            range_min = range[0]
            range_max = range[1]
            back = self.Segmentline_drop_by_2pointxy(
                Apoint=[range_min, self.line_solve(line, x=range_min)],
                Bpoint=[range_max, self.line_solve(line, x=range_max)],
                **inputvalue
            )
            return back

        if x_range is None and y_range is None:
            #如果没有提供取值范围,就使用屏幕范围
            # x_range = [0, py5.width]
            # y_range = [0, py5.height]
            # y_to_x_min = self.line_solve(line, y_range[0])
            # y_to_x_max = self.line_solve(line, y_range[1])
            # y_to_x_range = [y_to_x_min, y_to_x_max]
            # new_range_x = self.get_inter_range(x_range, y_to_x_range)
            # return xrange_to_Segline(new_range_x)
            raise ValueError("没有提供取值范围")
        if x_range is not None and y_range is None:
            #如果提供了x范围
            xmin = min(x_range[0], x_range[1])
            xmax = max(x_range[0], x_range[1])
            if xmin == xmax:
                raise ValueError(f"输入的范围{x_range}有误,是一个点而不是范围")
            return xrange_to_Segline([xmin, xmax])
        if y_range is not None and x_range is None:
            #如果提供的是y的范围,那么就换算成x的范围
            if y_range[0] == y_range[1]:
                raise ValueError(f"输入的范围{y_range}有误,是一个点而不是范围")
            x1 = self.line_solve(line, y=y_range[0])
            x2 = self.line_solve(line, y=y_range[1])
            xmin = min(x1, x2)
            xmax = max(x1, x2)
            return xrange_to_Segline([xmin, xmax])
        if x_range is not None and y_range is not None:
            #如果都提供了,就把y也换算成x的范围,然后调用get_inter_range找到交集
            y_to_x_min = self.line_solve(line, y=y_range[0])
            y_to_x_max = self.line_solve(line, y=y_range[1])
            y_to_x_range = [y_to_x_min, y_to_x_max]
            new_range_x = self.get_inter_range(x_range, y_to_x_range)
            if new_range_x is None:
                raise ValueError(f"获取{x_range}和{y_to_x_range}交集失败")
            if new_range_x[0] == new_range_x[1]:
                raise ValueError(f"输入的范围{x_range}有误,是一个点而不是范围")
            return xrange_to_Segline(new_range_x)

    def line_solve(self, line_letter_or_detaildic, x=None, y=None):
        """
        给定x或y，解决一个函数问题y=kx+b
        :param line_letter_or_detaildic: 直线的标识字母 例：a,或者一个包含详细信息的字典
        a只能接受0或1
        """
        if isinstance(line_letter_or_detaildic, dict):
            detail_dic = line_letter_or_detaildic
        else:
            if not line_letter_or_detaildic in self.line_dic:
                raise ValueError("没有找到直线，直线还未创建")
            detail_dic = self.line_dic[line_letter_or_detaildic]

        if x == None and y == None:
            raise ValueError("x，y都没有输入值 无法计算")

        if 'a' in detail_dic:
            the_a = detail_dic['a']
        else:
            the_a = 1

        the_b, the_k = detail_dic['b'], detail_dic['k']
        if y == None:
            if the_a == 0:
                raise ValueError("无法计算，因为a=0时0y=kx+b 无法计算y")
            # 计算y
            return the_k * x + the_b
        if x == None:
            # 计算x
            if the_k == 0:
                raise ValueError("无法计算，因为k=0时y=0x+b 无法计算x")
            return (y - the_b) / the_k

    def line_solve_general(self, a=1, y=None, k=None, x=None, b=None, A_point=None, B_point=None):
        """
        使用矩阵方法求解线性方程 ay = kx + b 或根据两点 (x1, y1) 和 (x2, y2) 计算 k 和 b。
        参数：
            a, y, k, x, b: 任意提供 ay = kx + b 的四个变量，求解第五个变量。
            A_point, B_point: 提供两点，求解 k 和 b，即使 x1 == x2 时也可以通过 a = 0 处理。
        返回：
            结果字典，包含已求解的变量及其值。
            当 a=0 且 k 都未给出时，函数将默认返回 k=1 ，即方程 x=-b
        """
        if a != 1 and a != 0:
            # 如果存在a值任意的话，把函数当作ay+kx+b=0来处理
            a = -a  # 我把这里添加了相反数是因为结尾输出的时候 是按照ay=kx+b书写的 所以-ay+kx+b=0
        # 1. 根据两点计算 k 和 b
        if A_point is not None and B_point is not None:
            if any(i is not None for i in (y, k, x, b)) and a != 1:
                raise ValueError("输入两点时候 请不要提供其它参数")
            if len(A_point) != 2 or len(B_point) != 2:
                raise ValueError("点格式不符合规范，A_point 和 B_point 应为 (x, y) 形式的元组或列表")
            x1, y1 = A_point
            x2, y2 = B_point
            if x1 == x2:  # 特殊情况：x1 == x2，垂直线
                return {
                    "a": 0,  # y 的系数为 0
                    "k": -1,  # 假设 k = -1
                    "b": x1,  # b = x1
                }
            else:  # 正常情况，使用矩阵方程计算 k 和 b
                A = np.array([[x1, 1], [x2, 1]])
                B = np.array([y1, y2])
                result = np.linalg.solve(A, B)
                return {"a": 1, "k": result[0], "b": result[1]}

        # 2. 特殊情况：a = 0
        if a == 0:
            # 方程退化为 kx + b = 0
            if k == 0:
                raise ValueError("0x+b=0")
            if k is not None and b is not None:
                return {"x": -b / k}
            elif x is not None:
                if k is None:
                    # 默认 k = 1
                    k = 1
                return {"b": -k * x}
            elif b is not None:
                if k is None:
                    # 默认 k = 1
                    k = 1
                return {"x": -b / k}
            else:
                raise ValueError("如果既没有 k，也没有 b，无解")

        # 3. 确保 y = kx + b 中有3个已知变量
        inputs = {"y": y, "k": k, "x": x, "b": b}
        known_values = {key: value for key, value in inputs.items() if value is not None}
        if len(known_values) != 3:
            raise ValueError("必须提供 y = kx + b 的3个变量才能求解")

        # 4. 根据未知变量求解，添加除零保护
        elif y is None:
            return {"y": (k * x + b) / a}
        elif k is None:
            if x == 0:
                raise ZeroDivisionError("x 不能为零")
            return {"k": (a * y - b) / x}
        elif x is None:
            if k == 0:
                raise ZeroDivisionError("k 不能为零")
            return {"x": (a * y - b) / k}
        elif b is None:
            return {"b": a * y - k * x}

        # 如果所有变量都已知，直接返回
        return known_values

    def intersection_2_Segmentline_Matrix(self, Aline, Bline):
        """
        使用矩阵方法 numpy 计算两条线段的交点
        :param A1: 线段 A 的起点 (x1, y1)
        :param A2: 线段 A 的终点 (x2, y2)
        :param B1: 线段 B 的起点 (x3, y3)
        :param B2: 线段 B 的终点 (x4, y4)
        :return: 交点坐标 (x, y)，如果没有交点返回 None
        """
        x1, y1 = Aline[0]
        x2, y2 = Aline[1]
        x3, y3 = Bline[0]
        x4, y4 = Bline[1]

        # 创建系数矩阵 A@缩小量=b
        A = np.array([[x2 - x1, x3 - x4], [y2 - y1, y3 - y4]])
        b = np.array([x3 - x1, y3 - y1])

        # 计算行列式
        det = np.linalg.det(A)

        # 判断是否平行或共线
        if abs(det) < 1e-10:  # 行列式接近 0，表示两条线段平行或共线
            return None

        # 解线性方程组
        t, s = np.linalg.solve(A, b)

        # 判断参数 t 和 s 是否在 [0, 1] 范围内
        if 0 <= t <= 1 and 0 <= s <= 1:
            # 计算交点坐标
            intersection_x = x1 + t * (x2 - x1)
            intersection_y = y1 + t * (y2 - y1)
            return (intersection_x, intersection_y)

        return None  # 如果 t 或 s 不在范围内，则没有交点

    def intersection_2_Segmentline(self, A_seg_Chain_or_2pointxy, B_seg_Chain_or_2pointxy):
        """
        返回 None 则没有交点
        可以混用Chain和2pointxy
        :param A_seg_Chain_or_2pointxy: 可以是Chain，也可以是列表：[ [a,b] , [c,d] ]
        :param B_seg_Chain_or_2pointxy: 可以是Chain，也可以是列表：[ [a,b] , [c,d] ]
        """
        # 判断输入格式
        if isinstance(A_seg_Chain_or_2pointxy, str):
            local_A = self.Segmentline_dic[A_seg_Chain_or_2pointxy]['location']
            Ax1, Ay1 = local_A[0]
            Ax2, Ay2 = local_A[1]
        else:
            Ax1, Ay1 = A_seg_Chain_or_2pointxy[0]
            Ax2, Ay2 = A_seg_Chain_or_2pointxy[1]
        if isinstance(B_seg_Chain_or_2pointxy, str):
            local_B = self.Segmentline_dic[B_seg_Chain_or_2pointxy]['location']
            Bx1, By1 = local_B[0]
            Bx2, By2 = local_B[1]
        else:
            Bx1, By1 = B_seg_Chain_or_2pointxy[0]
            Bx2, By2 = B_seg_Chain_or_2pointxy[1]

        # 特殊输入情况 防止报错
        if Bx1 == Bx2 and By1 == By2 and Ax1 == Ax2 and Ay1 == Ay2:
            # raise ValueError('输入了一个点')
            return Ax1, Ay1
        if Bx1 == Bx2 and By1 == By2:
            # raise ValueError('B线是一个点')
            temp_line_letter = self.Segmentline_to_line([A_seg_Chain_or_2pointxy[0], A_seg_Chain_or_2pointxy[1]])
            if By1 == self.line_solve(temp_line_letter, x=Bx1) and Bx1 == self.line_solve(temp_line_letter, y=By1):
                self.line_remove(temp_line_letter)
                return Bx1, By1
            else:
                self.line_remove(temp_line_letter)
                return None
        if Ax1 == Ax2 and Ay1 == Ay2:
            # raise ValueError('A线是一个点')
            temp_line_letter = self.Segmentline_to_line([B_seg_Chain_or_2pointxy[0], B_seg_Chain_or_2pointxy[1]])
            if Ay1 == self.line_solve(temp_line_letter, x=Ax1) and Ax1 == self.line_solve(temp_line_letter, y=Ay1):
                self.line_remove(temp_line_letter)
                return Ax1, Ay1
            else:
                self.line_remove(temp_line_letter)
                return None

        # 检查线段投影范围是否重叠（快速排除法）
        rangeX = max(min(Ax1, Ax2), min(Bx1, Bx2)), min(max(Ax1, Ax2), max(Bx1, Bx2))
        rangeY = max(min(Ay1, Ay2), min(By1, By2)), min(max(Ay1, Ay2), max(By1, By2))
        if rangeX[0] > rangeX[1] or rangeY[0] > rangeY[1]:
            return None  # 没有重叠，线段不可能相交

        # 计算直线的斜率和截距
        if Ax1 == Ax2:  # 第一条线和y轴水平
            k_A, b_A = None, Ax1
        else:
            k_A = (Ay1 - Ay2) / (Ax1 - Ax2)
            b_A = Ay1 - k_A * Ax1
        if Bx1 == Bx2:  # 第二条线和y轴水平
            k_B, b_B = None, Bx1
        else:
            k_B = (By1 - By2) / (Bx1 - Bx2)
            b_B = By1 - k_B * Bx1

        # 检查是否平行
        if k_A is not None and k_B is not None:  # 两条线都不是垂直线
            if abs(k_A - k_B) < 1e-10:  # 斜率相等，平行，不可能有交点
                return None
            # 计算交点
            x = (b_B - b_A) / (k_A - k_B)
            y = k_A * x + b_A
        elif k_A is None:  # 第一条线垂直
            x = Ax1
            y = k_B * Ax1 + b_B
        elif k_B is None:  # 第二条线垂直
            x = b_B
            y = k_A * x + b_A

        # 检查交点是否在两条线段的范围内
        if rangeX[0] <= x <= rangeX[1] and rangeY[0] <= y <= rangeY[1]:
            return x, y
        else:
            return None  # 交点不在线段范围内

    def intersection_line_and_Segmentline(self, segline_chain, line='a'):
        """
        经典方法 查找两条线段交点，无交点返回None
        """
        Aletter, Bletter = segline_chain.split('-')
        A = self.point_dic[Aletter]
        B = self.point_dic[Bletter]
        Ax, Ay = A
        Bx, By = B
        seg_rangeX, seg_rangeY = [min([Ax, Bx]), max([Ax, Bx])], [min([Ay, By]), max([Ay, By])]

        # 根据投影判断是否可能存在交点
        if not 'a' in self.line_dic[line]:
            if self.line_dic[line]['k'] != 0:
                line_shadow_y1 = self.line_dic[line]['k'] * seg_rangeX[0] + self.line_dic[line]['b']
                line_shadow_y2 = self.line_dic[line]['k'] * seg_rangeX[1] + self.line_dic[line]['b']
                line_shadow_Rangey = [min([line_shadow_y1, line_shadow_y2]), max([line_shadow_y1, line_shadow_y2])]
                line_shadow_x1 = (seg_rangeY[0] - self.line_dic[line]['b']) / self.line_dic[line]['k']
                line_shadow_x2 = (seg_rangeY[1] - self.line_dic[line]['b']) / self.line_dic[line]['k']
                line_shadow_Rangex = [min([line_shadow_x1, line_shadow_x2]), max([line_shadow_x1, line_shadow_x2])]
                final_range_x = [max(line_shadow_Rangex[0], seg_rangeX[0]), min(line_shadow_Rangex[1], seg_rangeX[1])]
                final_range_y = [max(line_shadow_Rangey[0], seg_rangeY[0]), min(line_shadow_Rangey[1], seg_rangeY[1])]
                if final_range_x[0] > final_range_x[1] or final_range_y[0] > final_range_y[1]:
                    # 范围无效 不存在交点
                    return None
                else:
                    if final_range_x[0] == final_range_x[1] and final_range_y[0] == final_range_y[1]:
                        # raise ValueError('范围仅为一个点')
                        print('范围仅为一个点')
                        letter_theline = self.Segmentline_to_line(segline_chain)
                        if self.line_solve(letter_theline, x=final_range_x[0]) == final_range_y[0]:
                            # 如果把点的x坐标带入直线中，得到的y值刚好是点的y坐标

                            return [final_range_x[0], final_range_y[0]]
                        else:
                            return None
                    temp_Ax, temp_Bx = final_range_x[0], final_range_x[1]
                    temp_Ay = self.line_solve(line, x=temp_Ax)
                    temp_By = self.line_solve(line, x=temp_Bx)
                    temp_A, temp_B = [temp_Ax, temp_Ay], [temp_Bx, temp_By]
                    inter_point = self.intersection_2_Segmentline([temp_A, temp_B], [A, B])
                    return inter_point
            else:
                # k=0时候，y=b 只需要比较线段的y范围是否包含b
                if seg_rangeY[0] <= self.line_dic[line]['b'] <= seg_rangeY[1]:
                    value_y = self.line_dic[line]['b']
                    the_line = self.Segmentline_to_line(segline_chain)
                    value_x = self.line_solve(the_line, y=value_y)
                    return [value_x, value_y]
                else:
                    return None
        else:
            if self.line_dic[line]['k'] != 0:
                raise ValueError("a=0 且 k=0 ：输入的是一个点而不是线")
            # a=0时候,x=b/-k 是一条垂直线 只需要比较线段的x范围是否包含b/-k
            if seg_rangeY[0] <= self.line_dic[line]['b'] / -self.line_dic[line]['k'] <= seg_rangeY[1]:
                value_x = self.line_dic[line]['b'] / -self.line_dic[line]['k']
                the_line = self.Segmentline_to_line(segline_chain)
                value_y = self.line_solve(the_line, x=value_x)
                return [value_x, value_y]
            else:
                return None

    def intersection_2line(self, Aline_letter_or_kba_dic, Bline_letter_or_kba_dic):
        """
        :param Aline_letter_or_kba_dic: 可以是代号，也可以是save_line(temp=true)的返回值：一个包含k，b，a的字典
        :param Bline_letter_or_kba_dic: 可以是代号，也可以是save_line(temp=true)的返回值：一个包含k，b，a的字典
        """
        x = None
        y = None

        if isinstance(Aline_letter_or_kba_dic, str):
            detail_dicA = self.line_dic[Aline_letter_or_kba_dic]
        else:
            detail_dicA = Aline_letter_or_kba_dic
        if isinstance(Bline_letter_or_kba_dic, str):
            detail_dicB = self.line_dic[Bline_letter_or_kba_dic]
        else:
            detail_dicB = Bline_letter_or_kba_dic
        k_A = detail_dicA['k']
        b_A = detail_dicA['b']
        k_B = detail_dicB['k']
        b_B = detail_dicB['b']
        if 'a' in detail_dicA:
            x = b_A / k_A
        if 'a' in detail_dicB:
            if x is not None:
                return None
            x = b_B / k_B
        # y1=k_A*x+b_A
        # y2=k_B*x+b_B
        if k_A == k_B:
            return None
        if x is None:
            x = (b_B - b_A) / (k_A - k_B)
        y = k_A * x + b_A
        return [x, y]

    def Segmentline_shadow_on_axis(self, Chain_or_2pointxy):
        """
        求一条线段分别在x轴和y轴的投影
        :param Chain_or_2pointxy: 既可以是A-B形式 也可以是[x,y][x,y]
        :return: 返回一个列表，包含两个范围[[x_min, x_max], [y_min, y_max]]
        """
        if isinstance(Chain_or_2pointxy, str):
            A_pointlist = self.Segmentline_dic[Chain_or_2pointxy]['location']
            x1, y1 = A_pointlist[0]
            x2, y2 = A_pointlist[1]
        else:
            x1, y1 = Chain_or_2pointxy[0]
            x2, y2 = Chain_or_2pointxy[1]
        x_range = [min(x1, x2), max(x1, x2)]
        y_range = [min(y1, y2), max(y1, y2)]
        return [x_range, y_range]

    def Segmentline_to_line(self, chain_or_2pointxy, back_range=False, temp=False):
        """
        :param chain_or_2pointxy: 既可以是一个ChainA-B也可以是列表[[Ax,Ay], [Bx,By]]
        :return: 返回一个代号, 例如：a
        详细信息储存在字典line_dic[a]中
        如果back_range 额外返回一个列表[[xmin,xmax],[ymin,ymax]]

        """
        if isinstance(chain_or_2pointxy, str):
            Aletter, Bletter = chain_or_2pointxy.split('-')
            x1, x2 = self.point_dic[Aletter][0], self.point_dic[Bletter][0]
            y1, y2 = self.point_dic[Aletter][1], self.point_dic[Bletter][1]
        else:
            x1, y1 = chain_or_2pointxy[0]
            x2, y2 = chain_or_2pointxy[1]

        if x1 == x2 and y1 == y2:
            raise ValueError('is not a line,this is a point')
        if x1 == x2:
            a = 0
            b = x1
            k = -1
        else:
            a = 1
        if y1 == y2:
            k = 0
            b = y1
        if x1 != x2 and y1 != y2:
            k = (y1 - y2) / (x1 - x2)
            b = y1 - k * x1
        back = self.line_drop(k, b, a, temp)
        if back_range is True:
            range = self.Segmentline_shadow_on_axis(chain_or_2pointxy)
            back = back, range

        return back

    def line_chain_or_dic(self,line_chain_or_dic):
        """
        此方法无论输入的是dict还是'代号'
        统一会返回dict
        如果失败(输入的格式错误) 返回False
        """
        if isinstance(line_chain_or_dic, str):
            detail_line_dic = self.line_dic[line_chain_or_dic]
        elif isinstance(line_chain_or_dic, dict):
            detail_line_dic = line_chain_or_dic
        else:
            return False
        return detail_line_dic

    def distance_point_to_line(self,point,line):
        #linedic例子:{'a': {'str': 'y=3x+100', 'k': 3, 'b': 100}}
        point = self.point_get_info(point)['location'] #只获取第一项,也就是位置信息
        if point is False:
            raise ValueError(f'point输入的参数{point}错误')
        point_x = point[0]
        point_y = point[1]
        detail_line_dic = line_chain_or_dic(line)
        if detail_line_dic is False:
            raise ValueError(f'line输入的参数{line}错误')

        if detail_line_dic['k']==0:
            #输入的line是一条水平线
            return abs(detail_line_dic[b]-point_y)
        if 'a' in detail_line_dic:
            #输入的是一条垂直线
            #存在a键的时候 a必定为0 且k必定为-1(line_drop中就是这么规定的)
            return abs(detail_line_dic[b] - point_x)
        k_orth = -1 / detail_line_dic['k']
        # 斜率是-1/k的时候垂直
        result=self.line_solve_general(a=1, k=k_orth, x=point_x, y=point_y)
        b=result['b']
        line_orth_dic = self.line_drop(temp=True,k=k_orth,b=b,a=1)
        point = [point_x, point_y]
        point_inter = self.intersection_2line(line_orth_dic, detail_line_dic)
        return self.distance_2_points(point,point_inter)


    # ////////////《面操作》////////////
    def intersection_line_and_surface(self,line,surface):
        """
        line:通用型,chain和2pointxy皆可
        """
        the_line = self.line_chain_or_dic(line)
    def surface_spilt_by_line(self, surface_chain, line_params):
        self.surface_chain_to_Segline_group(surface_chain)

    def surface_drop_by_chain(self, chain_of_point, floor=0, color=py5.color(200, 200, 20, 255), fill=False, stroke=None,
                              stroke_color=py5.color(0, 0, 0)):
        """
        【center】会自动生成在参数字典中：重心:是所有顶点坐标的平均值
        这里输入的链是不一定需要收尾相接的,如果不相接会自动补全
        """
        surf_pointgroup = []
        alist_of_point = chain_of_point.split('-')
        for aletter in alist_of_point:
            point_xy = self.point_dic.get(aletter, 0)
            if point_xy != 0:
                surf_pointgroup.append(point_xy)
            else:
                return "false:cant find point by letter"
        self.surface_chain_to_Segline_group(chain_of_point,visible=False) #确保线段都创建了
        nowdic = {}
        nowdic['floor'] = floor
        all_x, all_y = 0, 0
        for x, y in surf_pointgroup:
            all_x, all_y = all_x + x, all_y + y
        center = [all_x / len(surf_pointgroup), all_y / len(surf_pointgroup)]
        nowdic['center'] = center
        nowdic['local'] = surf_pointgroup
        nowdic['color'] = color
        nowdic['fill'] = fill
        nowdic['stroke'] = stroke
        nowdic['stroke_color'] = stroke_color
        self.surface_dic[chain_of_point] = nowdic
        return surf_pointgroup

    def surface_drop_by_pointlist(self, apointlist, floor=0, color=py5.color(200, 200, 20, 255), fill=False, stroke=None,
                                  stroke_color=py5.color(0, 0, 0)):
        """
        这里输入的链是不需要收尾相接的,如果不相接会自动补全
        """
        theletter = self.point_drop_group(apointlist)
        chain = "-".join(theletter)
        self.surface_drop_by_chain(chain, floor, color, fill, stroke, stroke_color)


    def surface_chain_to_Segline_group(self, chain,floor=0, color=py5.color(0, 0, 0, 255), strokeweight=3,
                                         visible=True):
        """
        给定一个字符串A-B-C,返回[A-B][B-C][C-A](返回的是首尾相接的,输入的不一定需要收尾相接)
        如果seglinedic中不存在这个线段 那么就会自动创建
        :param chain: 文本型，一个字符串 例：A-B-C
        :return: [A-B][B-C][C-A]
        """
        nodes = chain.split("-")  # 将链式结构分解为节点列表["A", "B", "C"]
        # 生成相邻对
        pairs = [(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)]
        if nodes[0] != nodes[-1]:
            # 如果第一个点和最后一个点不一致,加入首尾连接
            pairs.append((nodes[-1], nodes[0]))  # 结果: [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A')]
        formatted_pairs = [f"{a}-{b}" for a, b in pairs]
        for i in formatted_pairs:
            # 检查是否已经创建了线段 如果不存在就创建线段
            if i in self.Segmentline_dic in self.Segmentline_dic:
                continue
            else:
                q = i.split('-')
                self.Segmentline_drop_by_2pointletter(q[0], q[1],floor=floor,color=color,strokeweight=strokeweight,visible=visible)
        return formatted_pairs

    def is_point_in_surface(self, polx, P):
        """
           polx接受列表型 也接受非齐次坐标矩阵
           判断点 P 是否在 polx 中（包括在边上）
           polx: 多边形的顶点矩阵 [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
           P: 点的坐标 [x, y]
           return: 'inside' 如果点在内部, 'on_edge' 如果点在边上, 'outside' 如果点在外部
        """

        # 应当检查符号chain，给定的四边形是否已经闭合，若已经闭合 不可以用下文的
        # polx[(i + 1) % len(polx)]
        # 而应该改用
        # polx[i+1]
        def cross_product(A, B, P):
            # 计算叉积
            A = np.array(A)
            B = np.array(B)
            P = np.array(P)
            AB = B - A
            AP = P - A
            return np.cross(AB, AP)

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




    # ////////////《常用操作》////////////
    def list_depth(self,lst):
        if not isinstance(lst, (list,tuple)):
            # 如果当前不是列表，层数为 0
            return 0
        if not lst:
            # 如果列表是空的，层数为 1（只有一层）
            return 1
        # 递归判断每个元素的嵌套深度，并取最大值
        return 1 + max(self.list_depth(item) for item in lst)

    def get_inter_range(self, a=None, b=None):
        def get_range(interval):
            # 提取范围的辅助函数
            return min(interval[0], interval[1]), max(interval[0], interval[1])

        if a is not None and b is not None:
            if len(a) == 2 and len(b) == 2:
                amin, amax = get_range(a)
                bmin, bmax = get_range(b)
                new_max = min(amax, bmax)
                new_min = max(amin, bmin)
                # 检查是否有交集
                if new_min <= new_max:
                    return [new_min, new_max]
                else:
                    return None  # 无交集
            else:
                raise ValueError(f"输入{a}或{b}不是[x,y]形式")
        elif a is not None:
            if len(a) == 2:
                return list(get_range(a))
            else:
                raise ValueError(f"输入{a}不是[x,y]形式")
        elif b is not None:
            if len(b) == 2:
                return list(get_range(b))
            else:
                raise ValueError(f"输入{b}不是[x,y]形式")
        else:
            return None  # a 和 b 都为 None

    def SurfChain_to_HomoMatrix(self, Chain):
        """
        给定平面字符串表示 返回一个齐次坐标矩阵
        """
        print(self.surface_dic[Chain]['local'])
        vertices = np.array(self.surface_dic[Chain]['local'])
        homogeneous_vertices = np.hstack([vertices, np.ones((vertices.shape[0], 1))])
        return homogeneous_vertices

    def HomoMatrix_to_local(self, matrix):
        """
        给定齐次坐标矩阵 返回非齐次坐标矩阵 列表型np.array
        """
        cartesian_vertices = matrix[:, :-1]
        return cartesian_vertices
    # =========================================

def screen_draw_surface(surfacedic,floor):
    surface_drawed={}
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

def screen_draw_SegmentLine(SegmentLine_dic, floor):
    for key, val in SegmentLine_dic.items():
        if val['floor']!=floor:
            continue
        if val['visible']==False:
            continue
        color=val['color']
        py5.stroke(color)
        strokeweigh=val['stroke_weight']
        py5.stroke_weight(strokeweigh)
        local_group=[a for i in val['location'] for a in i]
        py5.line(*local_group)

def screen_draw_lines(linedic,color=py5.color(10,10,0,255),stroke_weight=3):
    screen_info=screen_get_info()
    x_range,y_range=screen_info['x_range'],screen_info['y_range']
    tem=Tools2D()
    for key,de_dic in linedic.items():
        tem.line_to_Segmentline(de_dic,x_range=x_range,y_range=y_range)
    py5.stroke(color)
    py5.stroke_weight(stroke_weight)
    line_todraw=[]
    for key, value in tem.Segmentline_dic.items():
        #整理输入参数格式,py5.line需要的格式[[x1 y1 x2 y2] [...]]
        a_point,b_point=value['location'][0],value['location'][1]
        the_line=a_point+b_point
        line_todraw.append(the_line)
    py5.lines(np.array(line_todraw, dtype=np.float32))

def screen_draw(f=3, Seglinedic=None, surfdic=None):
    """
    f是绘制的图层数
    """
    if surfdic is None and Seglinedic is None:
        raise ValueError ('没有输入surfdic或者seglinedic,无法绘制')
    for i in range(f):
        if surfdic is not None:
            screen_draw_surface(surfdic, i)
        if Seglinedic is not None:
            screen_draw_SegmentLine(Seglinedic, i)

def screen_print_fps():
    py5.fill(0)  # 设置文本颜色为黑色
    py5.text_size(16)  # 设置文本大小
    frame=py5.get_frame_rate()
    py5.text(f"FPS: {frame}", 10, 30)

def screen_get_info():
    """
    返回一个关于屏幕详细信息的字典
    包含:
    x_range,y_range
    rect:屏幕矩形(首尾相接)
    center:屏幕中心
    """
    in_dic={}
    right_top=[py5.width,0]
    right_down=[py5.width,py5.height]
    left_top=[0,0]
    left_down=[0,py5.height]
    x_range = [0, py5.width]
    y_range = [0, py5.height]
    in_dic['x_range']=x_range
    in_dic['y_range'] = y_range
    in_dic['rect'] = [left_top,right_top,right_down,left_down,left_top]
    in_dic['center']=[py5.width/2,py5.height/2]
    return in_dic

def screen_axis(x=0,y=0):
    """
    从屏幕中心建立坐标系,输入x,y 返回py5的正确坐标
    """
    x=py5.width/2+x
    y=py5.height/2+y
    return [x,y]

def test_random_point(creat_num=1500,del_num=1000,num=10):
    """
    随机创建一些点,返回point_dic
    creat_num:随机创建点数量
    del_num:随机删除点数量
    num:循环以上过程次数
    """
    p=Tools2D()
    for n in range(num):
        for i in range(creat_num):
            p.point_drop([random.randint(0, 10), random.randint(0, 10)])
        for i in range(del_num):
            p_letter = list(p.point_dic.keys())
            p.point_remove_by_letter(random.choice(p_letter))
    return p.point_dic

def test_random_segline(number=100):
    """
    随机生成number条线段
    返回线段字典Segmentline_dic
    """
    lines = Tools2D()
    for i in range(number):
        A = [random.randint(0, 400), random.randint(0, 300)]
        B = [random.randint(0, 400), random.randint(0, 300)]
        color = py5.color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        # print(A,"/n",B)
        lines.Segmentline_drop_by_2pointxy(Apoint=A, Bpoint=B, color=color)
    # print(lines.get_Segmentline_dic())
    return lines.get_Segmentline_dic()

def test_line_in_extreme(num=500):
    lines = Tools2D()
    for i in range(num):
        a = random.randint(-3, 3)
        k = random.randint(-3, 3)
        if a==0 and k==0:
            continue
        lines.line_drop(k=k, b=random.randint(-100, 100), a=a)
    return lines.get_line_dic()
