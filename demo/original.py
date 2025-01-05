import turtle
import math
# import keyboard
# from isort.profiles import black
import numpy as np
# from textdistance import overlap

def distance(point1, point2):
    """
    计算两个点之间的距离

    参数:
    point1: 第一个点的坐标 (x1, y1)
    point2: 第二个点的坐标 (x2, y2)

    返回:
    两点之间的距离
    """
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
def draw_bezier_curve(lengg, stjiaodu, t):
    # 定义控制点
    P0 = np.array([0, 0])
    P1 = np.array([100/300*lengg, -120/300*lengg])
    P2 = np.array([150/300*lengg, 200/300*lengg])
    P3 = np.array([lengg, 0])

    # 定义贝塞尔曲线的函数
    def bezier(t, P0, P1, P2, P3):
        return (1 - t) ** 3 * P0 + 3 * (1 - t) ** 2 * t * P1 + 3 * (1 - t) * t ** 2 * P2 + t ** 3 * P3

    # 生成参数 t 的值
    t_values = np.linspace(0, 1, 8)

    # 计算贝塞尔曲线的点
    bezier_points = np.array([bezier(t, P0, P1, P2, P3) for t in t_values])
    points_as_tuples = [tuple(point) for point in bezier_points]

    # 计算每段的距离和相对角度
    sveangdis = []
    current_angle = 0  # 初始角度为 0
    for i in range(len(points_as_tuples) - 1):
        # 计算当前点到下一个点的坐标差值
        delta_x = points_as_tuples[i + 1][0] - points_as_tuples[i][0]
        delta_y = points_as_tuples[i + 1][1] - points_as_tuples[i][1]

        # 计算两点之间的距离
        distance = math.dist(points_as_tuples[i], points_as_tuples[i + 1])

        # 计算该段的绝对角度（相对于 x 轴正方向）
        angle_radians = math.atan2(delta_y, delta_x)
        angle_degrees = math.degrees(angle_radians)

        # 计算相对角度差
        relative_angle = angle_degrees - current_angle
        sveangdis.append((relative_angle, distance))

        # 更新当前角度
        current_angle = angle_degrees

    # 设置乌龟初始角度
    t.setheading(stjiaodu)

    # 让乌龟 t 按照 sveangdis 中的角度和距离前进
    for angle, distance in sveangdis:
        if angle > 0:
            t.left(angle)  # 向左旋转
        else:
            t.right(-angle)  # 向右旋转（angle 是负值）

        t.forward(distance)

# 设置屏幕
screen = turtle.Screen()
screen.bgcolor("white")


# 创建第一个乌龟
t1 = turtle.Turtle()
t1.color("blue")
t1.speed(0)  # 设置速度为最快
t1.dot(20, "red") #显示原点
#50x50x50的等边三角形 所以高的计算方法如下：
hS = round(50 * math.sin(math.radians(60)),1)

#从原点向前走一个等边三角形的高 画出第一个blackpot
t1.setheading(90)
t1.forward(hS)
t1.dot(20, "black")
blackpot = []
printblackpotword = 1
t1.write(printblackpotword, move=False, align='left', font=('Arial', 20, 'normal'))
print("精度2位数坐标：",round(t1.position()[0],2),round(t1.position()[1],2))
print("turtle二维：",t1.position())
readyaddpot=(round(t1.position()[0],2),round(t1.position()[1],2))
blackpot.append(readyaddpot)
print("元组列表，精度两位：",blackpot)
cishu=0
nowhead = t1.heading()

#keyboard.wait("space")
for cishu in range (6):
  printblackpotword = printblackpotword+1
  print("即将打印数字：",printblackpotword)
  t1.goto(blackpot[0])
  t1.setheading(nowhead-60*cishu)
  t1.forward(2*hS)
  t1.write(printblackpotword, move=False, align='left', font=('Arial', 20, 'normal'))
  t1.dot(20, "black")
  readyaddpot = (round(t1.position()[0], 2), round(t1.position()[1], 2))
  blackpot.append(readyaddpot)
  print("元组列表，精度两位：", blackpot)
  print(blackpot)

print ("即将开始选中新的黑洞中心",blackpot[1])
#keyboard.wait("space")
saveblackpot =blackpot[1]
t1.goto(blackpot[1])
t1.setheading(90)
t1.forward(2*hS)
newhead =t1.heading()
#keyboard.wait("space")
gotopot = (round(t1.position()[0], 2), round(t1.position()[1], 2))
for cishu in range (7):
  print("rang:", cishu)
  if gotopot in blackpot:
      print("skp第",cishu,)
  else:
      readyaddpot = (round(t1.position()[0], 2), round(t1.position()[1], 2))
      blackpot.append(readyaddpot)
      printblackpotword = printblackpotword + 1
      print("即将打印数字：", printblackpotword)
      t1.dot(20, "black")
      t1.write(printblackpotword, move=False, align='left', font=('Arial', 20, 'normal'))

  t1.goto(blackpot[1])
  t1.setheading(nowhead - 60 * cishu)
  t1.forward(2 * hS)
  gotopot = (round(t1.position()[0], 2), round(t1.position()[1], 2))


def select_blackhole_center(index):
    global printblackpotword
    # 确保输入的index在blackpot数组的有效范围内
    if index >= len(blackpot):
        print(f"索引 {index} 超出范围，blackpot 数组的长度为 {len(blackpot)}")
        return

    print("即将开始选中新的黑洞中心", blackpot[index])

    # 保存黑洞中心位置
    saveblackpot = blackpot[index]
    t1.penup()
    t1.goto(blackpot[index])
    t1.pendown()
    t1.setheading(90)
    t1.forward(2 * hS)

    # 记录当前的朝向
    newhead = t1.heading()

    # 获取当前位置的坐标
    gotopot = (round(t1.position()[0], 2), round(t1.position()[1], 2))

    # 用于生成数字的变量
    #printblackpotword = 10

    # 执行循环操作
    for cishu in range(7):
        print("rang:", cishu)
        if gotopot in blackpot:
            print("skp第", cishu)
        else:
            # 添加新的黑洞坐标
            readyaddpot = (round(t1.position()[0], 2), round(t1.position()[1], 2))
            blackpot.append(readyaddpot)
            printblackpotword += 1
            print("即将打印数字：", printblackpotword)
            t1.dot(20, "black")
            t1.write(printblackpotword, move=False, align='left', font=('Arial', 20, 'normal'))

        # 更新位置与朝向
        t1.goto(blackpot[index])
        t1.setheading(newhead - 60 * cishu)
        t1.forward(2 * hS)
        gotopot = (round(t1.position()[0], 2), round(t1.position()[1], 2))


# 调用示例
for fuzhi in range(5):
 select_blackhole_center(2+fuzhi)# 例如，选取blackpot数组的第1个元素
print(blackpot)
#keyboard.wait("space")
#----------------------------------------------
#接下来是绘制部分
#----------------------------------------------
t1.reset()
t1.hideturtle()
# 创建第二个乌龟
t2 = turtle.Turtle()
t2.color("pink")
t2.pensize(3)
t2.speed(0)  # 设置速度为最快
t2.penup ()
t2.goto (50/2,0)
t2.dot(20)
global savepkd
savepkd = []
global savebld
savebld = []
savepkd.append((round(t2.position()[0], 2), round(t2.position()[1], 2)))
t2.goto(-50/2,0)
t2.dot(20,"blue")
savebld.append((round(t2.position()[0], 2), round(t2.position()[1], 2)))
t2.goto(blackpot[1-1])
t2.dot(20,"black")
t2.goto(50/2,0)
t2.goto(blackpot[1-1])
t2.pendown()
#绘制第二个粉色点
def check_and_draw(blackpot):
    # 设置初始朝向
    t2.setheading(0)
    print("初始朝向:", t2.heading())
    t2.penup()
    t2.goto(blackpot)
    t2.dot (20,"black")
    t2.pendown()
    # 旋转和前进循环
    for _ in range(6):  # 每次旋转60度，循环6次完成360度

        t2.left(60)  # 每次旋转60度
        memt2lef = t2.heading()
        draw_bezier_curve(50,t2.heading(),t2)  # 前进50单位
        #t2.forward (50)
        t2.setheading(memt2lef)

        # 遍历 savepkd 数组并检查距离条件
        for spa in range(len(savepkd)):
            current_position = (round(t2.position()[0], 2), round(t2.position()[1], 2))
            dist = round(distance(savepkd[spa], current_position), 2)
            print("实际距离:", dist)

            # 检查是否在 savebld 或 savepkd 中
            if current_position in savebld or current_position in savepkd:
                print("位置已存在")
                t2.goto(current_position) #只划线
                t2.penup()
                t2.goto(blackpot)  # 回到 blackpot 位置
                t2.pendown()
                break

            # 检查距离条件
            if dist == round(2 * hS, 2):
                t2.dot(20)  # 画一个点
                t2.penup()
                t2.goto(blackpot)  # 回到 blackpot 位置
                t2.pendown()
                savepkd.append(current_position)
                break
        else:
            # 如果没有找到符合条件的点，画蓝色点
            print("目标距离:", round(2 * hS, 2))
            print("符合距离条件:", dist == round(2 * hS, 2))
            t2.dot(20, "blue")
            savebld.append(current_position)
            t2.penup()
            t2.goto(blackpot)  # 回到 blackpot 位置
            t2.pendown()

# 示例调用
for cada in range(19):
    check_and_draw(blackpot[cada])
'''
t2.setheading (0)
print(t2.heading())
for _ in range(6):  # 每次旋转60度，循环6次完成360度
    t2.left(60)  # 每次旋转60度
    t2.forward(50)  # 前进50单位
    #keyboard.wait("space")
    # 遍历 savepkd 数组并检查距离条件
    for spa in range(len(savepkd)):

        current_position = (round(t2.position()[0], 2), round(t2.position()[1], 2))
        dist = round(distance(savepkd[spa], current_position),2)
        print("实际为",dist)
        if current_position in savebld:
            print("havehave")
            t2.goto(blackpot[0])
            break
        if current_position in savepkd:
            print("havehave")
            t2.goto(blackpot[0])
            break

        if dist == round(2 * hS, 2):
            t2.dot(20)  # 画一个点
            t2.goto(blackpot[0])
            savepkd.append((round(t2.position()[0], 2), round(t2.position()[1], 2)))
            break
    else:
        # 如果没有找到符合条件的点，画蓝点
        print("应当为：",round(2 * hS, 2))
        print(distance(savepkd[spa], current_position) == round(2 * hS, 2))
        t2.dot(20, "blue")
        savebld.append((round(t2.position()[0], 2), round(t2.position()[1], 2)))
        t2.goto(blackpot[0])

# 返回到 blackpot 的第一个点
''


''
# 追踪绘制的步数
step1 = 0
step2 = 0

# 定义第一个乌龟的绘制函数
def draw_spiral_step():
    global step1
    if step1 < 50:  # 限制绘制的步数
        t1.forward(step1 * 2)
        t1.right(90)
        step1 += 1
        screen.ontimer(draw_spiral_step, 100)  # 延时100毫秒后再次调用自己

# 定义第二个乌龟的绘制函数
def draw_circle_step():
    global step2
    if step2 < 100:  # 限制绘制的步数
        t2.forward(2)  # 每次向前走2个像素
        t2.right(3.6)  # 每次旋转3.6度 (一圈共100步)
        step2 += 1
        screen.ontimer(draw_circle_step, 100)
'''
turtle.done()