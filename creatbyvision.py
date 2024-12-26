import py5_tools
from scipy.constants import point
py5_tools.add_jars('./jars')
import py5
from controlP5 import ControlP5, Slider
import YuSan_PY5_Toolscode as Yt
def setup():

    global cp5
    py5.size(400, 300)
    cp5 = ControlP5(py5.get_current_sketch())
    global altext
    altext=creat_new_textbox("alias",200,200)
    #altext = cp5.getController('alias')
    import textwrap
    altext.setText("asd")
    global newtext
    newtext= str(altext.getText())
    #altext.onEnter(on_textfield_enter)
    global pointA
    pointA=[0,0]

def creat_new_textbox(textboxname, x, y):
    table = cp5.addTextfield(textboxname)
    table.setPosition(x, y)
    table.setSize(100, 25)
    table.setValue(80)
    table.setAutoClear(False)
    return table

def key_pressed():
    #当文本框被按下回车时，自动丢失焦点（保存文本中内容）
    if py5.key == py5.ENTER and altext.isFocus():
        altext.setFocus(False)

def mouse_pressed():
    if py5.mouse_button==py5.LEFT:
        global moux
        global mouy
        global pointA
        pointA = [moux, mouy]
        print(pointA)
        print(Yt.tans_to_easyread(pointA))

def draw():
    py5.background(255) #粉刷
    global newtext
    global moux
    global mouy
    global pointA
    global A

    # 绘制坐标轴
    py5.stroke(0)
    py5.stroke_weight(2)


    # 绘制坐标轴刻度和标注
    Yt.draw_orgin_axes(20,20)

    moux=py5.mouse_x
    mouy=py5.mouse_y
    py5.stroke(0)
    if pointA != [0,0]:
        py5.stroke(0)
        py5.no_fill()
        py5.ellipse(pointA[0], pointA[1], 37, 37)
        py5.line(moux,mouy,pointA[0],pointA[1])
        #py5.point(pointA[0],pointA[1])
    #py5.background('#004477')
    #py5.stroke('#FFFFFF')绘制线改为白色
    py5.stroke_weight(3)#线粗细
    axis = 250


    # alias
    py5.fill(0)
    py5.text_size(20)
    py5.text_align(py5.CENTER)
    alias = altext.getText()
    if altext.isFocus() == False:
        newtext=str(alias)
        py5.text("text:" + newtext, axis, 450)
    else:
        py5.text("text:" + newtext, axis, 450)
    py5.no_fill()#绘制形状仅显示边框，而不填充任何颜色。


#12/24
py5.run_sketch()