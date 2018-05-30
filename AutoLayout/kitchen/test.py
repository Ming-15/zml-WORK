# -*- coding:utf-8 -*-
import random
from AutoLayout.kitchen.settings import *
import sympy.geometry as sge
import time
from AutoLayout.kitchen import utility
import AutoLayout.BaseClass as BaseClass
import AutoLayout.BaseModual as BaseModual
import AutoLayout.CommonElement as CommonElement
import AutoLayout.DY_Line as DY_Line
import AutoLayout.helpers as helpers
import AutoLayout.kitchen.Base as kb
import os,shutil
import math
import random
DOOR_LEN = 800
DOOR_OFF = 200


def set_window_boundary(win):
    # win_op_wall = helpers.get_opposite_bounds(win_wall,boundary)[0]
    p3 = win.seg.p1 - win.normal.p2 * 200
    p4 = win.seg.p2 - win.normal.p2 * 200
    win.set_boundary(BaseClass.DY_boundary(win.seg.p1, p3, p4, win.seg.p2))


def test4110(xlen, ylen, border_bool, win_type, door_type, save_name, type='L'):
    """
        border_bool    true false
        border_type    0: down; 1: left; 2: up; 3: right
        win_type       0: down; 1: left; 2: up; 3: right
        door_type(L)   0, 1: down right, down left;
                       2, 3: left down, left up;
                       4, 5: up left, up right;
                       6, 7: right up, right down;
        door_type(U)   0: down; 1: left; 2: up; 3: right
      """
    origin_x, origin_y = 0, 0
    p0 = sge.Point(origin_x, origin_y)
    p1 = sge.Point(p0.x, p0.y + ylen)
    p2 = sge.Point(p0.x + xlen, p0.y + ylen)
    p3 = sge.Point(p0.x + xlen, p0.y)

    kitch = kb.Kitchen()
    kitch.set_boundary(BaseClass.DY_boundary(p0, p1, p2, p3))

    if border_bool:
        border_type = random.randint(0, 4)
        if border_type == 0:
            kitch.add_border(DY_Line.Border(p0, p3))
        elif border_type == 1:
            kitch.add_border(DY_Line.Border(p0, p1))
        elif border_type == 2:
            kitch.add_border(DY_Line.Border(p1, p2))
        elif border_type == 3:
            kitch.add_border(DY_Line.Border(p2, p3))
    else:
        pass

    win_off_x, win_len_x = int(xlen * 0.2), int(xlen * 0.6)
    win_off_y, win_len_y = int(ylen * 0.2), int(ylen * 0.6)
    if win_type == 0:
        win_p0 = sge.Point(p3.x - win_off_x, p3.y)
        win_p1 = sge.Point(win_p0.x - win_len_x, win_p0.y)
        win = DY_Line.Window(win_p0, win_p1)
        set_window_boundary(win)
        kitch.add_window(win)
    elif win_type == 1:
        win_p0 = sge.Point(p0.x, p0.y + win_off_y)
        win_p1 = sge.Point(win_p0.x, win_p0.y + win_len_y)
        win = DY_Line.Window(win_p0, win_p1)
        set_window_boundary(win)
        kitch.add_window(win)
    elif win_type == 2:
        win_p0 = sge.Point(p0.x + win_off_x, p1.y)
        win_p1 = sge.Point(win_p0.x + win_len_x, win_p0.y)
        win = DY_Line.Window(win_p0, win_p1)
        set_window_boundary(win)
        kitch.add_window(win)
    elif win_type == 3:
        win_p0 = sge.Point(p2.x, p2.y - win_off_y)
        win_p1 = sge.Point(win_p0.x, win_p0.y - win_len_y)
        # kitch.add_window(DY_Line.Window(win_p0,win_p1))
        win = DY_Line.Window(win_p0, win_p1)
        set_window_boundary(win)
        kitch.add_window(win)

    dr = CommonElement.Door()
    for i in range(0, 3):
        if type == 'L':
            if door_type == 0:
                dr_p0 = sge.Point(p3.x - DOOR_LEN - DOOR_OFF, p3.y)
                dr_p1 = sge.Point(dr_p0.x + DOOR_LEN, dr_p0.y)
                dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)
            elif door_type == 1:
                dr_p0 = sge.Point(p0.x + DOOR_OFF, p0.y)
                dr_p1 = sge.Point(dr_p0.x + DOOR_LEN, p0.y)
                dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)
            elif door_type == 2:
                dr_p0 = sge.Point(p0.x, p0.y + DOOR_LEN + DOOR_OFF)
                dr_p1 = sge.Point(dr_p0.x, dr_p0.y - DOOR_LEN)
                dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)
            elif door_type == 3:
                dr_p0 = sge.Point(p1.x, p1.y - DOOR_OFF)
                dr_p1 = sge.Point(dr_p0.x, dr_p0.y - DOOR_LEN)
                dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)
            elif door_type == 4:
                dr_p0 = sge.Point(p1.x + DOOR_OFF + DOOR_LEN, p1.y)
                dr_p1 = sge.Point(dr_p0.x - DOOR_LEN, dr_p0.y)
                dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)
            elif door_type == 5:
                dr_p0 = sge.Point(p2.x - DOOR_OFF, p2.y)
                dr_p1 = sge.Point(dr_p0.x - DOOR_LEN, dr_p0.y)
                dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)
            elif door_type == 6:
                dr_p0 = sge.Point(p2.x, p2.y - DOOR_LEN - DOOR_OFF)
                dr_p1 = sge.Point(dr_p0.x, dr_p0.y + DOOR_LEN)
                dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)
            elif door_type == 7:
                dr_p0 = sge.Point(p3.x, p3.y + DOOR_OFF)
                dr_p1 = sge.Point(dr_p0.x, dr_p0.y + DOOR_LEN)
                dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)
        elif type == 'U':
            if door_type == 0:
                dr_p0 = sge.Point(p3.x - (p3.x + DOOR_LEN) / 2, p3.y)
                dr_p1 = sge.Point(dr_p0.x + DOOR_LEN, dr_p0.y)
                dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)
            elif door_type == 1:
                dr_p0 = sge.Point(p0.x, p0.y + (p1.y + DOOR_LEN) / 2)
                dr_p1 = sge.Point(dr_p0.x, dr_p0.y - DOOR_LEN)
                dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)
            elif door_type == 2:
                dr_p0 = sge.Point(p1.x + (p2.x + DOOR_LEN) / 2, p1.y)
                dr_p1 = sge.Point(dr_p0.x - DOOR_LEN, dr_p0.y)
                dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)
            elif door_type == 3:
                dr_p0 = sge.Point(p2.x, p2.y - (p2.y + DOOR_LEN) / 2)
                dr_p1 = sge.Point(dr_p0.x, dr_p0.y + DOOR_LEN)
                dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)

    kitch.add_door(dr)

    hou = BaseClass.House()
    fp = BaseModual.FloorPlan()
    fp.set_boundary(BaseClass.DY_boundary(p0, p1, p2, p3))
    fp.add_region(kitch)
    hou.add_floorplan(fp)
    kitch.run()
    kitch.draw(savename=save_name, show_flag=False)
    # helpers.save_house_to_xml(hou, save_name)


def batch_test(border_bool=False, type='L'):
    wall_step = 800
    root_path = 'E:\\kitchen_test\\'  # 文件路径
    if os.path.exists(root_path): shutil.rmtree(root_path)
    os.mkdir(root_path)

    # len_wid = [(1500, 2100), (1800, 2500), (2300, 3000),
    #            (3600, 3500), (2500, 1800), (3000, 2300)]
    save_path = r'E:\kitchen_test'
    dr_case = 0
    if type == 'L':
        dr_case = 8
    elif type == 'U':
        dr_case = 4

    cnt = 0
    if border_bool:
        for xlen in range(KITCHEN_MIN_LEN + 0, KITCHEN_MAX_LEN + wall_step, wall_step):
            print(range(KITCHEN_MIN_LEN + 0, KITCHEN_MAX_LEN + wall_step, wall_step))
            for ylen in range(KITCHEN_MIN_LEN + 0, KITCHEN_MAX_LEN + wall_step, wall_step):
                if xlen > KITCHEN_MAX_LEN: xlen = KITCHEN_MAX_LEN
                if ylen > KITCHEN_MAX_LEN: ylen = KITCHEN_MAX_LEN

                name = root_path + 'x' + str(xlen) + '_y_' + str(ylen)
                os.mkdir(name)
                name += '\\'

            for brd_type in range(4):
                for w_type in range(4):

                    if w_type == brd_type:
                        continue
                    for dr_type in range(dr_case):
                        tmpId = int(dr_type / 2)
                        if tmpId == w_type or tmpId == brd_type:
                            continue
                        save_name = name + 'wall' + str(cnt)
                        save_name = save_name + '_dr' + str(w_type)
                        save_name += '_win' + str(cnt) + '.jpg'
                        # save_name = save_path + '\\' + str(cnt) + '.xml'
                        test4110(xlen, ylen, True, w_type, dr_type, save_name, 'L')
                        cnt += 1
    else:
        for xlen in range(KITCHEN_MIN_LEN + 0, KITCHEN_MAX_LEN + wall_step, wall_step):
            for ylen in range(KITCHEN_MIN_LEN + 0, KITCHEN_MAX_LEN + wall_step, wall_step):
                if xlen > KITCHEN_MAX_LEN: xlen = KITCHEN_MAX_LEN
                if ylen > KITCHEN_MAX_LEN: ylen = KITCHEN_MAX_LEN
                name = root_path + 'x' + str(xlen) + '_y_' + str(ylen)
                os.mkdir(name)
                name += '\\'
            for w_type in range(4):
                for dr_type in range(dr_case):
                    save_name = name + 'wall' + str(cnt)
                    save_name = save_name + '_dr' + str(w_type)
                    save_name += '_win' + str(cnt) + '.jpg'
                    # save_name = save_path + '\\' + str(cnt) + '.xml'
                    print(save_name)
                    test4110(xlen, ylen, False, w_type, dr_type, save_name, 'L')
                    cnt += 1
                    print(cnt)


def test_u():
    origin_x, origin_y = 0, 0
    win_len = 1000
    win_step = win_len - 300
    wall_step = 800
    root_path = 'E:\\kitchen_test_xiugai\\'  # 文件路径
    if os.path.exists(root_path): shutil.rmtree(root_path)
    os.mkdir(root_path)
    r = 0  # 计算次数
    for xlen in range(KITCHEN_MIN_LEN + 0, KITCHEN_MAX_LEN + wall_step, wall_step):

        for ylen in range(KITCHEN_MIN_LEN + 0 + 1, KITCHEN_MAX_LEN + wall_step, wall_step):
            if xlen > KITCHEN_MAX_LEN: xlen = KITCHEN_MAX_LEN
            if ylen > KITCHEN_MAX_LEN: ylen = KITCHEN_MAX_LEN - 1

            p0 = sge.Point(origin_x, origin_y)
            p1 = sge.Point(p0.x, p0.y + ylen)
            p2 = sge.Point(p0.x + xlen, p0.y + ylen)
            p3 = sge.Point(p0.x + xlen, p0.y)

            kt_bound = BaseClass.DY_boundary(p0, p1, p2, p3)

            name = root_path + 'x' + str(xlen) + '_y_' + str(ylen)
            os.mkdir(name)
            name += '\\'

            for id_s, seg in enumerate(kt_bound.seg_list):

                # 放置门,每个边上测试3个门的位置
                # step = (seg.seg.length - DOOR_LEN) / 2
                step = 400  # 按一定的间隔布置门
                for i in range(int(DOOR_LEN / step), int(DOOR_LEN / step) + 5):
                    win_counter = 0
                    for id_s1, seg1 in enumerate(kt_bound.seg_list):
                        win_num = math.ceil(float(seg1.seg.length)) / win_step
                        for j in range(int(win_num)):
                            save_name = name + 'wall' + str(id_s)
                            save_name = save_name + '_dr' + str(i)
                            save_name += '_win' + str(win_counter) + '.jpg'
                            win_counter += 1

                            # 配置厨房
                            kt = kb.Kitchen()
                            kt.set_boundary(kt_bound)

                            # 配置门
                            dr = CommonElement.Door()
                            dp1 = seg.p1 + seg.dir.p2 * step * i
                            dp2 = dp1 + seg.dir.p2 * DOOR_LEN
                            if seg.seg.contains(dp1) and seg.seg.contains(dp2):
                            # if seg.seg.contains(dp1 and dp2):
                                # 选择布U型厨房
                                bl = BaseClass.DY_segment(dp1,dp2)
                                dr.set_pos(bl, DOOR_LEN)
                                kt.add_door(dr)
                                parll_wall_line = BaseClass.DY_segment(dr.backline.normal.p1,dr.backline.normal.p2)
                                parll_dr_wall = helpers.get_paralleled_line(parll_wall_line,kt_bound,type=BaseClass.DY_segment)
                                parll_wall = parll_dr_wall[0]
                                dis0 = helpers.get_min_dis_seg_boundary(parll_wall,dr.boundary)
                                parll_wall = parll_dr_wall[1]
                                dis1 = helpers.get_min_dis_seg_boundary(parll_wall,dr.boundary)
                                # if dis0 > CABINET_L and dis1 > CABINET_L:#U型测试文件
                                if dis0 > CABINET_L and dis1 > CABINET_L:#U型测试文件
                                # if dis0 <= CABINET_L or dis1 <= CABINET_L:#L型测试文件
                                    #配置窗
                                    if j is not win_num-1:
                                        wp1 = seg1.p1 + seg1.dir.p2 * win_step * j
                                        wp2 = wp1 + seg1.dir.p2 * win_len
                                    else:
                                        wp2 = seg1.p2
                                        wp1 = wp2 - seg1.dir.p2 * win_len
                                    win = DY_Line.Window(wp1, wp2)
                                    # 碰撞检测
                                    if dr.boundary.polygon.intersection(win.seg) != []:
                                        continue
                                    if dr.backline.seg.contains(wp1) or dr.backline.seg.contains(wp2):
                                        continue
                                    if win.seg.contains(dr.backline.p1) or win.seg.contains(dr.backline.p2):
                                        continue
                                    set_window_boundary(win)
                                    kt.add_window(win)

                                    kt.run()
                                    kt.draw(savename=save_name, show_flag=False)

                                    hou = BaseClass.House()
                                    fp = BaseModual.FloorPlan()
                                    fp.set_boundary(BaseClass.DY_boundary(p0, p1, p2, p3))
                                    fp.add_region(kt)
                                    hou.add_floorplan(fp)
                                    helpers.save_house_to_xml(hou,save_name+'.xml')
                                    r += 1
                                    print(r)




def test_one0():
    origin_x, origin_y = 0, 0
    wall_step = 500
    root_path = 'E:\\kitchen_test_one0_XXX\\'  # 文件路径
    if os.path.exists(root_path): shutil.rmtree(root_path)
    os.mkdir(root_path)
    r = 0#计算次数
    for xlen in range(D2_TH1 + 0, D2_TH2 + wall_step, wall_step):

        for ylen in range(D1_MIN + 0, D1_MAX + wall_step, wall_step):
            if xlen > D2_TH2: xlen = D2_TH2-1
            if ylen > D1_MAX: ylen = D1_MAX
            p0 = sge.Point(origin_x, origin_y)
            p1 = sge.Point(p0.x, p0.y + ylen)
            p2 = sge.Point(p0.x + xlen, p0.y + ylen)
            p3 = sge.Point(p0.x + xlen, p0.y)

            kt_bound = BaseClass.DY_boundary(p0,p1,p2,p3)

            name = root_path + 'x' + str(xlen) + '_y_' + str(ylen)
            os.mkdir(name)
            name += '\\'
            for id_s,seg in enumerate(kt_bound.seg_list):
                step = 150#按一定的间隔布置门
                for i in range(int(DOOR_LEN/step),int(DOOR_LEN/step)+8):
                    for id_s1,seg1 in enumerate(kt_bound.seg_list):
                        borders = DY_Line.Border(seg1.p1,seg1.p2)
                        save_name = name + 'wall' + str(id_s)
                        save_name = save_name + '_dr_' + str(i) + str('_')
                        save_name += str(time.time()) + str(str(id_s)+'_seg') + '.png'
                        #配置厨房
                        kt = kb.Kitchen()

                        kt.set_boundary(kt_bound)
                        result = utility.room_size_judgement(kt.boundary)
                        if seg1.seg.length == result[0] and seg1 is borders:
                            continue
                        # 添加虚边界
                        kt.add_border(borders)
                        # 配置门
                        dr = CommonElement.Door()
                        dp1 = seg.p1 + seg.dir.p2 * step * i
                        dp2 = dp1 + seg.dir.p2 * DOOR_LEN
                        bl = BaseClass.DY_segment(dp1,dp2)
                        if seg.seg.contains(dp1) and seg.seg.contains(dp2):
                            if borders.seg.contains(dp1) or borders.seg.contains(dp2):
                                continue
                            dr.set_pos(bl, DOOR_LEN)
                            kt.add_door(dr)
                        else:
                            continue
                        kt.run()
                        kt.draw(savename=save_name, show_flag=False)
                        # 生成匹配的xml文件
                        hou = BaseClass.House()
                        fp = BaseModual.FloorPlan()
                        fp.set_boundary(BaseClass.DY_boundary(p0, p1, p2, p3))
                        fp.add_region(kt)
                        hou.add_floorplan(fp)
                        helpers.save_house_to_xml(hou, save_name + '.xml')
                        r += 1
                        print(r)
def test_parallel():
    origin_x, origin_y = 0, 0
    wall_step = 300
    root_path = 'E:\\kitchen_parallel\\'  # 文件路径
    if os.path.exists(root_path): shutil.rmtree(root_path)
    os.mkdir(root_path)
    r = 0  # 计算次数
    for xlen in range(D2_TH2 + 0, D1_MAX + wall_step, wall_step):
        for ylen in range(D1_MIN, D1_MAX + wall_step, wall_step):
            if xlen > D1_MAX: xlen = D1_MAX
            if ylen > D1_MAX: ylen = D1_MAX
            p0 = sge.Point(origin_x, origin_y)
            p1 = sge.Point(p0.x, p0.y + ylen)
            p2 = sge.Point(p0.x + xlen, p0.y + ylen)
            p3 = sge.Point(p0.x + xlen, p0.y)
            kt_bound = BaseClass.DY_boundary(p0, p1, p2, p3)
            name = root_path + 'x' + str(xlen) + '_y_' + str(ylen)
            os.mkdir(name)
            name += '\\'
            for id_s,seg in enumerate(kt_bound.seg_list):
                step = 50#按一定的间隔布置门
                for i in range(3,21):#按照门间隔移动的次数
                    for id_s1,seg1 in enumerate(kt_bound.seg_list):
                        borders = DY_Line.Border(seg1.p1,seg1.p2)
                        save_name = name + 'wall' + str(id_s)
                        save_name = save_name + '_dr_' + str(i) + str('_')
                        save_name += str(time.time()) + str(str(id_s)+'_seg') + '.jpg'
                        #配置厨房
                        kt = kb.Kitchen()
                        kt.set_boundary(kt_bound)
                        kt.add_border(borders)
                        # 配置门
                        dr = CommonElement.Door()
                        dp1 = seg.p1 + seg.dir.p2 * step * i
                        dp2 = dp1 + seg.dir.p2 * DOOR_LEN
                        bl = BaseClass.DY_segment(dp1, dp2)
                        if not (seg1.seg.contains(dp2) and seg1.seg.contains(dp1)):
                            dr.set_pos(bl, DOOR_LEN)
                            dr_seg_list = []
                            for dr_seg in dr.boundary.seg_list:
                                if not dr_seg.line.is_parallel(dr.backline.line):
                                    dr_seg_list.append(dr_seg)
                            dr_bd = random.choice(dr_seg_list)
                            dr.set_body(dr_bd)
                            kt.add_door(dr)
                        else:
                            continue
                        result = utility.room_size_judgement(kt.boundary)
                        if dr.backline.line.is_parallel(borders.line) and borders.seg.length == result[-1]:
                            dis0, dis1, dis2, dis3 = utility.get_doorbackline_wall_dis(kt.boundary, dr)
                            if dis0 > CABINET_L and dis1 > CABINET_L:
                                kt.run()
                                kt.draw(savename=save_name, show_flag=False)
                                # 生成匹配的xml文件
                                hou = BaseClass.House()
                                fp = BaseModual.FloorPlan()
                                fp.set_boundary(BaseClass.DY_boundary(p0, p1, p2, p3))
                                fp.add_region(kt)
                                hou.add_floorplan(fp)
                                helpers.save_house_to_xml(hou, save_name + '.xml')
                                r += 1
                                print(r)

if __name__ == '__main__':
    pass


