#—*— coding: utf-8 _*_
import AutoLayout.childrenroom
import AutoLayout.CommonElement
from AutoLayout import BaseClass, CommonElement
from AutoLayout.childrenroom.Base import *
import os
import shutil
import math


def set_window_boundary(win):
    # win_op_wall = helpers.get_opposite_bounds(win_wall,boundary)[0]
    p3 = win.seg.p1 - win.normal.p2 * 200
    p4 = win.seg.p2 - win.normal.p2 * 200
    win.set_boundary(BaseClass.DY_boundary(win.seg.p1, p3, p4, win.seg.p2))


def test411():
    wall_step = 800
    p0_x, p0_y = 0, 0
    root_path = 'D:\\temp\\'
    win_len = 1000
    win_step = win_len - 100
    dr_len = 900

    if os.path.exists(root_path): shutil.rmtree(root_path)
    os.mkdir(root_path)

    for x in range(CHILDED_MIN_LEN + 0, CHILDBED_MAX_LEN + wall_step, wall_step):
        for y in range(CHILDED_MIN_LEN + 0, CHILDBED_MAX_LEN + wall_step, wall_step):

            if x > CHILDBED_MAX_LEN: x = CHILDBED_MAX_LEN
            if y > CHILDBED_MAX_LEN: y = CHILDBED_MAX_LEN

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
                            # 配置儿童房

                            mb = Childrenroom()
                            mb.set_boundary(mb_bound)
                            # 配置门
                            dr = CommonElement.Door()
                            dp1 = seg.p1 + seg.dir.p2 * step * i
                            dp2 = dp1 + seg.dir.p2 * dr_len
                            bl = DY_segment(dp1, dp2)
                            dr.set_pos(bl, dr_len)
                            mb.add_door(dr)
                            # print(mb.ele_list)
                            # 配置窗
                            if j is not win_num-1:
                                wp1 = seg1.p1 + seg1.dir.p2*win_step*j
                                wp2 = wp1 + seg1.dir.p2*win_len
                            else:
                                wp2 = seg1.p2
                                wp1 = wp2 - seg1.dir.p2*win_len
                            win = Window(wp1, wp2)
                            set_window_boundary(win)

                            if dr.backline.seg.contains(wp1) or dr.backline.seg.contains(wp2):
                                continue
                            if win.seg.contains(dr.backline.p1) or win.seg.contains(dr.backline.p2):
                                continue

                            mb.add_window(win)

                            if x == 3000 and y == 3800 and id_s == 0 and i == 0 and win_counter == 17:
                                a = 0

                            # # for win_b in win.boundary:
                            # if dr.backline.normal.is_parallel(win.normal):
                            mb.run()

                            mb.draw(savename=save_name, show_flag=False)
