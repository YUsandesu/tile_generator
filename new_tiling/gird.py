from the_control import *
from PY5_2DToolkit import *
from BruijnsSystem import BruijnsSystem

def setup():
    global gird_data
    py5.size(800, 600)
    py5.frame_rate(144)
    load()
    slider('sides', (50,py5.height-120), value=5, range_val=(3,15))
    slider('distance', location=(50,py5.height-90), value=15, range_val=(0,500))
    slider('zoom', location=(50,py5.height-60), value=150, range_val=(0,500))
    slider('num', location=(50,py5.height-30), size=(500,20), value=3, range_val=(0,500))
    gird_data = BruijnsSystem.create_gird(5, 15, gap=150, num_of_line=3, center=sd.screen_axis(0, 0))
    #print(f"初次生成the_gird:{the_gird}")
    # print("Here")
    # print(gird_data)
    # print("Here")

def draw():
    global gird_data

    back = slider_value()
    if back:
        gird_data = BruijnsSystem.create_gird(
            sides=back['sides'],
            shifted_distance=back['distance'],
            gap=back['zoom'],
            center=sd.screen_axis(0,0),
            num_of_line=back['num']
        )

    py5.background(255)

    the_lines_dict_list = [each_info['girds'] for each_info in gird_data] #取出每组gird
    the_origin_gird = [each_info['origin_directed_line'] for each_info in gird_data]
    the_vector = [each_info['origin_vector'] for each_info in gird_data]

    sd.screen_draw_vector(the_vector,sd.screen_axis(-150,150))#画出原始向量

    for times,line_dict in enumerate(the_lines_dict_list):
        sd.screen_draw_directed_line(line_dict,stroke_weight=3,color=color[times%len(color)])

    sd.screen_draw_directed_line(the_origin_gird,stroke_weight=5,color=py5.color(0,0,0,125))

    # inter_info=tilling.get_girds_interaction(gird_data)
    # points_list=list(inter_info.keys())
    # # print(points_list)
    # tem=Tools2D()
    # tem.point_drop_group(points_list)
    # screen_draw_points(tem.get_point_dic())
    sd.screen_print_fps()


if __name__ == "__main__":
    sd=Screen_draw(py5)
    color = [
        py5.color(255, 0, 0),
        py5.color(0, 255, 0),
        py5.color(0, 0, 255),
        py5.color(0, 255, 255),
        py5.color(255, 255, 0),
        py5.color(255, 0, 255),
        py5.color(125, 125, 0),
        py5.color(125, 0, 125),
        py5.color(0, 125, 125),
        py5.color(125, 125, 255),
        py5.color(125, 255, 125),
        py5.color(255, 125, 125),
        py5.color(125, 0, 255),
        py5.color(255, 0, 125),
        py5.color(255, 125, 0),
    ]  # 颜色常量

    # gird_data:list
    py5.run_sketch()




