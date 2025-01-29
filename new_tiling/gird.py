import py5_tools
py5_tools.add_jars('../jars')
from YuSan_PY5_Toolscode import *
from the_control import *


def create_gird(sides,distance=0,zoom=100,center=[100,100],line_num=50):
    """
    distance：初始向量取垂直线以后，相互远离的距离。
    zoom：每条网格线相隔的距离
    返回一个列表，每个列表中包含一个方向的平行网格线，由所有网格线组成一个gird
    """
    global vector
    global gird
    # distance = [distance for i in range(sides)]
    #print(distance)
    pv = Tools2D()
    # 在【0，0】创建一个多边形,返回点集到vector
    vector = pv.regular_polygon(sides=sides, side_length=30)
    # 取vector的垂直向量vector_pen
    vector_pen = pv.vector_rotate(vector, 90)

    o_gird = Tools2D()
    for times,i in enumerate(vector_pen):
        # 把vector_pen换成直线,直线要经过center
        the_line=o_gird.vector_to_line(i, center)
        #按照原始向量方向平移distance距离
        distance_vector = o_gird.vector_change_norm(vector[times],distance)
        o_gird.line_shift(the_line,distance_vector,rewrite=True,drop=False)

    gird_0 = o_gird.get_line_dic()

    gird=[] #为每一个组平行网格创建一个对象
    num=len(gird_0.keys())
    for i in range(num):
        gird.append(Tools2D())

    # 平移gird_0，构建平行网格
    for t, (letter, line_detail) in enumerate(gird_0.items()):
        direction_vector = vector[t]  # 平移方向为vector
        for i in range(0, line_num//2):
            # 用vector_change_norm拉伸向量长度
            gird[t].line_shift(line_detail,
                            gird[t].vector_change_norm(direction_vector,zoom* i),
                                                       rewrite=False, drop=True)
            gird[t].line_shift(line_detail,
                            gird[t].vector_change_norm(direction_vector, zoom* -i),
                                                       rewrite=False, drop=True)

    #返回平行网络
    back_list=[]
    for times,i in enumerate(gird):
        back_list.append(i.get_line_dic())
    return back_list

def setup():
    global the_gird
    py5.size(800,600)
    py5.frame_rate(144)
    load()
    slider('sides',[50,py5.height-120],value=5,range=[3,15])
    slider('distance',location=[50,py5.height-90],value=15,range=[0,500])
    slider('zoom',location=[50,py5.height-60],value=150,range=[0,500])
    slider('num',location=[50,py5.height-30],size=[500,20],value=50,range=[0,500])
    the_gird = create_gird(5, 15, zoom=150, line_num=50,center=screen_axis(0,0))
def draw():
    global the_gird
    back = slider_value()
    if back is not None:
        the_gird=create_gird(sides=back['sides'],
                             distance=back['distance'],
                             zoom=back['zoom'],
                             center=screen_axis(0,0),
                             line_num=back['num'])
    py5.background(255)
    screen_draw_vector(vector,screen_axis(-50,-50))
    for i in the_gird:
        screen_draw_lines(i)
    screen_print_fps()

if __name__ == "__main__":
    the_gird:list
    py5.run_sketch()



