import py5_tools
py5_tools.add_jars('../jars')
from YuSan_PY5_Toolscode import *
from the_control import *
# import tilling
color=[py5.color(255,0,0),
           py5.color(0,255,0),
           py5.color(0,0,255),
           py5.color(0,255,255),
           py5.color(255,255,0),
           py5.color(255,0,255),
           py5.color(125,125,0),
           py5.color(125,0,125),
           py5.color(0,125,125),
           py5.color(125, 125, 255),
           py5.color(125, 255, 125),
           py5.color(255, 125, 125),
           py5.color(125, 0, 255),
           py5.color(255, 0, 125),
           py5.color(255, 125, 0),
           ] #颜色常量


def create_gird(sides, shifted_distance=0, gap=100, center=(100, 100), num_of_line=50):
    """
    此函数用于创建一组网格系统
    distance：初始向量取垂直线以后，相互远离的距离。
    zoom：每条网格线相隔的距离
    返回一个列表，每个列表中包含一个方向的平行网格线，由所有网格线组成一个gird
    """

    tools = Tools2D()
    back_list = []

    # 在【0，0】创建一个多边形,返回点集到vector
    vectors_origin = tools.regular_polygon(sides=sides, side_length=30)
    back_list = [{'origin_vector':o_v} for o_v in vectors_origin]

    # 取vector的垂直向量vector_pen
    vectors_origin_pen = [tools.vector_rotate(the_vector, 90) for the_vector in vectors_origin]
    for t,p_o_v in enumerate(vectors_origin_pen):
        back_list[t]['pen_origin_vector']=p_o_v

    #定义有向直线:
    for d_v in vectors_origin_pen:
        tools.directed_line_drop(location_point=center,direction_vector=d_v)

    origin_directed_lines = tools.get_line_dic()
    origin_directed_lines_id = list(origin_directed_lines.keys())

    for times,origin_line_id in enumerate(origin_directed_lines_id):
        #按照vector的方向,改变vector的模长-->获得平移向量distance_vector
        # TODO 此处模长可以不用以相同数值平移,可以存在长度差,应该再增加一个参数调整长度差
        distance_shift_vector = tools.vector_change_norm(vectors_origin[times], shifted_distance)
        back_list[times]['shift_vector_based_distance']=distance_shift_vector
        tools.line_shift(origin_line_id,distance_shift_vector,rewrite=True,drop=False)

    origin_directed_lines = list(tools.get_line_dic().values()) #取出的直线数据,准备平移
    for t,o_d_line in enumerate(origin_directed_lines):
        back_list[t]['origin_directed_line']=o_d_line
    tools.reset() #清除内容

    # 平移gird_0，构建平行网格gird
    for t, line_dict in enumerate(origin_directed_lines):#遍历原始gird每一条线
        back_list[t]['girds'] = {0:back_list[t]['origin_directed_line']}
        for the_time,i in enumerate(range(1, (num_of_line - 1) // 2 + 1)):# (num_of_line-1)是因为去掉原始line的1,
            # 最后+1是因为range不包括最后一项

            # vector_origin的顺序和origin_lines的方向是一致的, 长度取zoom的倍数即可
            positive_vector = tools.vector_change_norm(vectors_origin[t], gap * i)
            negative_vector = tools.vector_change_norm(vectors_origin[t], gap * -i)

            #和origin_vector同方向的为正,反方向的为负
            line_positive_detail = tools.line_shift(line_dict,positive_vector,rewrite=False, drop=False)
            line_negative_detail = tools.line_shift(line_dict,negative_vector,rewrite=False, drop=False)

            back_list[t]['girds'][the_time+1] = line_positive_detail #命名方式1,2,3...
            back_list[t]['girds'][-(the_time+1)] = line_negative_detail #-1,-2,-3...

    print(f'\nback_list:\n')
    for t,i in enumerate(back_list):
        print(f'\n{t}:\n{i}')
    print(back_list)
    return back_list


def setup():
    global gird_data
    py5.size(800,600)
    py5.frame_rate(144)
    load()
    slider('sides',[50,py5.height-120],value=5,range=[3,15])
    slider('distance',location=[50,py5.height-90],value=15,range=[0,500])
    slider('zoom',location=[50,py5.height-60],value=150,range=[0,500])
    slider('num',location=[50,py5.height-30],size=[500,20],value=3,range=[0,500])
    gird_data = create_gird(5, 15, gap=150, num_of_line=3, center=screen_axis(0, 0))
    #print(f"初次生成the_gird:{the_gird}")

def draw():
    global gird_data

    back = slider_value()
    if back is not None:
        gird_data=create_gird(sides=back['sides'],
                              shifted_distance=back['distance'],
                              gap=back['zoom'],
                              center=screen_axis(0,0),
                              num_of_line=back['num'])

    py5.background(255)


    the_lines_dict_list = [each_info['girds'] for each_info in gird_data] #取出每组gird
    the_origin_gird = [each_info['origin_directed_line'] for each_info in gird_data]
    the_vector = [each_info['origin_vector'] for each_info in gird_data]

    screen_draw_vector(the_vector,screen_axis(-150,150))#画出原始向量

    for times,line_dict in enumerate(the_lines_dict_list):
        screen_draw_directed_line(line_dict,stroke_weight=3,color=color[times%len(color)])

    screen_draw_directed_line(the_origin_gird,stroke_weight=5,color=py5.color(0,0,0,125))

    # inter_info=tilling.get_girds_interaction(gird_data)
    # points_list=list(inter_info.keys())
    # # print(points_list)
    # tem=Tools2D()
    # tem.point_drop_group(points_list)
    # screen_draw_points(tem.get_point_dic())
    screen_print_fps()


if __name__ == "__main__":
    gird_data:list
    py5.run_sketch()



