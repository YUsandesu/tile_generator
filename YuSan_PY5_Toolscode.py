import py5
from conda.gateways.repodata import RepoInterface
from docutils.utils.math.latex2mathml import letters
import random

pointdic={}
letterlist = [chr(i) for i in range(65, 91)]  # ASCII 65-90 对应 A-Z
nowletterlist=letterlist[:]

#print(letterslist)
def draw_orgin_axes(fangda=10,step=10,textstep=1,textsize=13,suojin=30):
    global fangdaxishu
    fangdaxishu = fangda
    tick_size = 5  # 刻度线长度
    lasttext = 0
    py5.text_size(textsize)
    Xzero=py5.width//2
    Yzero=py5.height//2
    Xmax=py5.width-suojin
    Xmin=0+suojin
    Ymax=0+suojin
    Ymin=py5.height-suojin
    global orgcenter
    orgcenter = [Xzero,Yzero]
    #绘制X轴
    py5.stroke(0)
    py5.stroke_weight(2)  # 线粗细
    py5.line(Xmin,Yzero,Xmax,Yzero)
    #绘制Y轴
    py5.stroke(0)
    py5.stroke_weight(2)  # 线粗细
    py5.line(Xzero,Ymin,Xzero,Ymax)
    #绘制X轴刻度和标注
    q=textstep*step//2
    for i in range(step, Xmax // 2, step):
        py5.stroke(0,0,0,100)
        py5.stroke_weight(2)  # 线粗细
        py5.fill(0,0,0,100)
        py5.text_align(py5.CENTER)
        py5.line(Xzero + i, Yzero, Xzero + i, Yzero - tick_size)
        py5.line(Xzero - i, Yzero, Xzero - i, Yzero - tick_size)
        if i == q+ textstep*step or i==q or textstep % 2 !=0:
            q = i
            if (Xzero + i)-lasttext<=py5.text_width(str(-i//fangda)):
                print("skip")
            else:
                py5.line(Xzero + i, Yzero, Xzero + i, Yzero - tick_size)
                py5.line(Xzero - i, Yzero, Xzero - i, Yzero - tick_size)
                py5.text(str(-i//fangda), Xzero - i, Yzero + tick_size + textsize // 2 + 2)
                py5.text(str(i//fangda), Xzero + i, Yzero + tick_size + textsize // 2 + 2)  # 添加数字标注
                lasttext = Xzero + i




    for i in range(step, Ymin // 2, step):  # 从中心点开始向两端绘制刻度

        py5.stroke(0, 0, 0, 100)
        py5.stroke_weight(2)  # 线粗细
        py5.fill(0, 0, 0, 100)
        py5.text_align(py5.RIGHT)

        py5.line(Xzero, Yzero - i, Xzero + tick_size, Yzero - i)
        py5.line(Xzero, Yzero + i, Xzero + tick_size, Yzero + i)
        panduanzhedang=abs((Yzero + tick_size + textsize // 2 + 2)-(Yzero + i + 5))
        #print(panduanzhedang)
        if panduanzhedang<= textsize//2:
            py5.text(str(i//fangda), Xzero - 5, Yzero - i + 5)
            continue
        py5.text(str(i//fangda), Xzero - 5, Yzero - i + 5)
        py5.text(str(-i//fangda), Xzero - 5, Yzero + i + 5)
#绘制一个坐标系【fangda】是放大比例，step是间隔多少绘制一个刻度，texttstep是间隔显示
#suojin是画面两边缩进不画线

def list_depth(lst):
            if not isinstance(lst, list):
                # 如果当前不是列表，层数为 0
                return 0
            if not lst:
                # 如果列表是空的，层数为 1（只有一层）
                return 1
            # 递归判断每个元素的嵌套深度，并取最大值
            return 1 + max(list_depth(item) for item in lst)

def tans_to_easyread (listxy):
    if list_depth(listxy)==1 and len(listxy)==2:
        newvecty =(orgcenter[1]-listxy[1])/ fangdaxishu
        newvectx=(listxy[0]-orgcenter[0])/fangdaxishu
        repoint = [newvectx,newvecty]
        return repoint
    else:
        print(listxy)
        raise ValueError("Data must be a list[x,y]")  # 抛出 ValueError 异常
#如果格式不会会报错

def droppoint_in_note(apoint):
    global letterlist
    global nowletterlist
    global pointdic
    if len(nowletterlist)==0:
        if len(letterlist[-1])==1:
            moreletterlist=[f"{chr(i)}1" for i in range(65, 91)]
            letterlist=letterlist+moreletterlist
            nowletterlist=moreletterlist
        else:
            morenum=str(int(letterlist[-1][1:])+1)
            moreletterlist = [chr(i)+morenum for i in range(65, 91)]
            letterlist = letterlist + moreletterlist
            nowletterlist = moreletterlist


    if list_depth(apoint)==1 and len(apoint)==2:
        lessletter=list(set(letterlist)-set(nowletterlist))
        back = nowletterlist[0]
        if lessletter == []:
            pointdic[nowletterlist[0]] = apoint
            del nowletterlist[0]
            return back
        else:
            pointdic[nowletterlist[0]] = apoint

            del nowletterlist[0]
            return back
    else:
        raise ValueError("Data must be a list[x,y]")  # 抛出 ValueError 异常
#如果格式不会会报错

def removepoint_by_letter(aletter):
    global pointdic
    global nowletterlist

    if aletter not in pointdic:
        return "cant find point"
    del pointdic[aletter]
    if len(aletter)==1:
        num = ord(aletter) - 65
    else:
        num = (ord(aletter[0]) - 65)+65* int(aletter[1:])
    if len(nowletterlist) > num:
        while ord(nowletterlist[num][0])+int(nowletterlist[num][1:]) >= ord(aletter[0])+int(aletter[:1]):
                num = num - 1
                if num == 0:
                    break
        nowletterlist.insert(num, aletter)
    else:
        nowletterlist.insert(0, aletter)
def removepoint_by_xy(listxy):
    target_value = listxy
    # 找到所有键
    keys = [k for k, v in pointdic.items() if v == target_value]
    if keys != None:
        removepoint_by_letter(keys[-1])
    else:
        return ("mei zhao dao")
#如果找不到会有返回值

#接下来
#1.把线段储存下来
#2.把线条（函数直线）储存下来

#测试
def ceshiyixia():
    e = random.choices(range(1, 300), k=7000)
    for i in range(7000):
        back = droppoint_in_note([random.randint(1, 1000), random.randint(1, 1000)])
        print(back)
        if random.randint(0, 1) == 1:
            next = chr(random.randint(65, 90)) + str(e[i])
            back = removepoint_by_letter(next)
            print("del", next)
            if back != None:
                print(next + back)
        if random.randint(0, 1) == 0:
            next = chr(random.randint(65, 90)) + str(e[i])
            if next in pointdic:
                back = removepoint_by_xy(pointdic[next])
                print("pointdelmode"+next)
            if back != None:
                print(next + back)
    print(pointdic)
    print(nowletterlist)
    print(len(pointdic.keys()))


#ceshiyixia()
