import AutoLayout.main_bedroom as main_bedroom
import AutoLayout.CommonElement as CommonElement
from AutoLayout.main_bedroom.Base import *
import os
import shutil
import math

def test411_single():
    p0_x, p0_y = 1000, 1000
    x_width, y_width = 4600, 4600
    save_name = r'E:\mb.jpg'

    p1 = Point2D(p0_x, p0_y)
    p2 = Point2D(p1.x, p1.y + y_width)
    p3 = Point2D(p2.x + x_width, p2.y)
    p4 = Point2D(p3.x, p3.y - y_width)

    mb_bound = DY_boundary(p1, p2, p3, p4)

    mb = main_bedroom.Base.MainBedroom()
    mb.set_boundary(mb_bound)

    dr_len = 850
    dr_bl_p1 = p1
    # dr_bl_p1 = p1 + mb_bound.seg_list[0].dir.p2 * y_width / 2
    # dr_bl_p1 = p1 + mb_bound.seg_list[0].dir.p2 * (y_width-850)
    dr_bl_p2 = dr_bl_p1 + mb_bound.seg_list[0].dir.p2*850
    dr = CommonElement.Door()
    bl = DY_segment(dr_bl_p1, dr_bl_p2)
    dr.set_pos(bl, dr_len)

    win_len = 1000
    # w_bl_p1 = p1
    # w_bl_p2 = w_bl_p1 + mb_bound.seg_list[0].dir.p2 * win_len

    # w_bl_p1 = p1
    # w_bl_p2 = w_bl_p1 - mb_bound.seg_list[3].dir.p2 * win_len

    w_bl_p1 = p2
    # w_bl_p1 = dr_bl_p1
    w_bl_p2 = w_bl_p1 + mb_bound.seg_list[1].dir.p2 * win_len

    win = Window(w_bl_p1, w_bl_p2)

    mb.add_window(win)
    mb.add_door(dr)
    try:
        mb.check_floor_plan()
    except Exception as e:
        print(e.args[0])
    # finally:
    #     print('finally')
    mb.run()
    mb.draw(savename=save_name)

def test411():
    wall_step = 800
    p0_x, p0_y = 1000, 1000
    root_path = 'E:\\temp\\'
    win_len = 1000
    win_step = win_len - 100
    dr_len = 850

    if os.path.exists(root_path): shutil.rmtree(root_path)
    os.mkdir(root_path)

    for x in range(MAINBED_MIN_LEN + 0, MAINBED_MAX_LEN + wall_step, wall_step):
        for y in range(MAINBED_MIN_LEN + 0, MAINBED_MAX_LEN + wall_step, wall_step):

            if x > MAINBED_MAX_LEN: x = MAINBED_MAX_LEN
            if y > MAINBED_MAX_LEN: y = MAINBED_MAX_LEN

            p1 = Point2D(p0_x, p0_y)
            p2 = Point2D(p1.x, p1.y + y)
            p3 = Point2D(p2.x + x, p2.y)
            p4 = Point2D(p3.x, p3.y - y)

            mb_bound = DY_boundary(p1, p2, p3, p4)

            name = root_path + 'x' + str(x) + '_y_' + str(y)

            os.mkdir(name)
            name += '\\'

            for id_s, seg in enumerate(mb_bound.seg_list):
                # 放置door: 每个边界测试3个门的位置
                step = (seg.seg.length - dr_len) / 2
                for i in range(0, 3):
                    win_counter = 0
                    for id_s1, seg1 in enumerate(mb_bound.seg_list):
                        win_num = math.ceil(float(seg1.seg.length)/win_step)
                        for j in range(win_num):
                            save_name = name + 'wall' + str(id_s)
                            save_name = save_name + '_dr' + str(i)
                            save_name += '_win' + str(win_counter) + '.jpg'
                            win_counter += 1
                            # 配置主卧

                            mb = MainBedroom()
                            mb.set_boundary(mb_bound)
                            # 配置门
                            dr = Door()
                            dp1 = seg.p1 + seg.dir.p2 * step * i
                            dp2 = dp1 + seg.dir.p2 * dr_len
                            bl = DY_segment(dp1, dp2)
                            dr.set_pos(bl, dr_len)
                            mb.add_door(dr)
                            # 配置窗
                            if j is not win_num-1:
                                wp1 = seg1.p1 + seg1.dir.p2*win_step*j
                                wp2 = wp1 + seg1.dir.p2*win_len
                            else:
                                wp2 = seg1.p2
                                wp1 = wp2 - seg1.dir.p2*win_len
                            win = Window(wp1, wp2)

                            if dr.backline.seg.contains(wp1) or dr.backline.seg.contains(wp2):
                                continue
                            if win.seg.contains(dr.backline.p1) or win.seg.contains(dr.backline.p2):
                                continue

                            mb.add_window(win)

                            if x == 3000 and y == 3800 and id_s == 0 and i == 0 and win_counter == 17:
                                a = 0

                            mb.run()

                            mb.draw(savename=save_name, show_flag=False)


def test611_single():
    p0_x, p0_y = 1000, 1000
    x_width, y_width, gap_width, gap_len = 4100, 4500, 1000, 1200
    save_name = r'E:\mb.jpg'

    p1 = Point2D(p0_x, p0_y)
    p2 = Point2D(p1.x, p1.y + y_width)
    p3 = Point2D(p2.x + x_width, p2.y)
    p4 = Point2D(p3.x, p3.y - y_width + gap_width)
    p5 = Point2D(p4.x + gap_len, p4.y)
    p6 = Point2D(p5.x, p5.y - gap_width)

    mb_bound = DY_boundary(p1, p2, p3, p4, p5, p6)

    mb = main_bedroom.Base.MainBedroom()
    mb.set_boundary(mb_bound)

    dr_len = 850
    dr_bl_p1 = p6
    dr_bl_p2 = dr_bl_p1 - mb_bound.seg_list[4].dir.p2*850
    dr = CommonElement.Door()
    bl = DY_segment(dr_bl_p2, dr_bl_p1)
    dr.set_pos(bl, dr_len)

    win_len = 2000
    w_bl_p1 = p2
    w_bl_p2 = w_bl_p1 + mb_bound.seg_list[1].dir.p2 * win_len
    win = Window(w_bl_p1, w_bl_p2)

    mb.add_window(win)
    mb.add_door(dr)

    # mb.flipup()
    # figure, ax = plt.subplots()
    # mb.draw(savename=r'E:\\tmp.jpg', show_flag=False)
    # exit()

    mb.run()
    mb.draw(savename=save_name, show_flag=False)




