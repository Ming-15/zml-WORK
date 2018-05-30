# _*_ coding:utf-8 _*_
from AutoLayout.BaseModual import *
from AutoLayout.livingroom.settings import *
from AutoLayout.BaseClass import *
from AutoLayout.livingroom.utility import *
from AutoLayout.livingroom.Element import *
from AutoLayout.settings import *
from AutoLayout.DY_Line import *
import AutoLayout.CommonElement as CommonElement
import random
import AutoLayout.main_bedroom.utility as mb_uti
import math
import pandas as pd
from AutoLayout.helpers import *

class Livingroom(Region):
    def __int__(self):
        super(Livingroom, self).__init__()
        self.main_win_wall = None
        self.main_curtain = None
    def run(self):
        (xmin, ymin, xmax, ymax) = self.boundary.polygon.bounds
        xlen = xmax - xmin
        ylen = ymax - ymin

        if xlen > LIVINGROOM_MAX_LEN or xlen < LIVINGROOM_MIN_LEN or \
            ylen > LIVINGROOM_MAX_LEN or ylen < LIVINGROOM_MIN_LEN:
            self.run_lv_any()
            return True
        if abs(self.boundary.polygon.area) < LIVINGROOM_MIN_LEN * LIVINGROOM_MIN_LEN:
            self.run_lv_any()
            return True

        arrangement_dict = {
            (4, 0, 1, 1): self.run4011, # 顶点4，门0，窗1，虚边界1
            (4, 1, 1, 1): self.run4111, # 顶点4，门1，窗1，虚边界1
            # (4, 1, 0, 2): self.run4102  # 顶点4，门1，窗0，虚边界2
            #uodo something else
        }

        key = (len(self.boundary.polygon.vertices), self.doors,
               self.windows, self.borders)

        if not arrangement_dict.get(key, False):
            # raise Exception("warning:客厅暂时不支持这种户型")
            self.run_lv_any()
        res = arrangement_dict.get(key)()

    # ***************************************run_lv_any****************************************
    def run_lv_any(self):
        wall_list = []
        bor_list = []
        win_list = []
        dr_list = []
        win_length = []
        bor_length = []
        bor_flag = False
        dr_flag = False
        win_flag = False
        bal_flag = False
        avoid_area = []
        self.virtual_boundary = get_virtual_boundary(self.boundary)

        for i in self.ele_list:
            if isinstance(i, CommonElement.Door):
                dr = i
                dr_flag = True
                dr_list.append(dr)
                d = dr_win_in_virtual_boundary(dr, self.virtual_boundary)
                avoid_area.append(d)
        for door in dr_list:
            if 'Balcony' in door.connect_list:
                bal_flag = True
                wall_list = ele_connect_wall(door.backline, self.virtual_boundary)

        for l in self.line_list:
            if isinstance(l, Border):
                border = l
                # print(border.connect_list, 111)
                bor_flag = True
                bor_length.append(border.seg.length)
                bor_list.append(border)

                for seg in self.virtual_boundary.seg_list:
                    if seg.seg.contains(border.seg):
                        avoid_area.append(border)

        for bor in bor_list:
            if 'Balcony' in bor.connect_list:
                bal_flag = True
                wall_list = ele_connect_wall(bor, self.virtual_boundary)
        for l in self.line_list:
            if isinstance(l, Window):
                win = l
                win_flag = True
                win_list.append(win)
                win_length.append(win.seg.length)

        if bal_flag == False:
            if win_flag:
                main_wall_list = []
                for w in win_list:
                    if w.seg.length == max(win_length):
                        main_win = w
                        # 在主窗处放置窗帘
                        window, self.main_curtain, self.main_win_wall = \
                            arrange_main_curtain(main_win, self.line_list, self.ele_list, self.virtual_boundary)
                for seg in self.virtual_boundary.seg_list:
                    if seg.line.is_parallel(main_win.line):
                        main_wall_list.append(seg)
                # distance方法必须是线到点的距离,顺序不可变
                dis0 = main_wall_list[0].seg.distance(main_win.seg.midpoint)
                dis1 = main_wall_list[1].seg.distance(main_win.seg.midpoint)

                if dis0 < dis1:
                    main_wall = main_wall_list[0]
                else:
                    main_wall = main_wall_list[1]

            else:
                if bor_flag:
                    for bor in bor_list:
                        if bor.seg.length == max(bor_length):
                            main_bor = bor
                for seg in self.virtual_boundary.seg_list:
                    if seg.seg.contains(main_bor.seg):
                        main_wall = seg

        else:
            main_wall = wall_list[0]
            if win_flag:
                main_wall_list = []
                for w in win_list:
                    if w.seg.length == max(win_length):
                        main_win = w
                        # 在主窗处放置窗帘
                        window, self.main_curtain, self.main_win_wall = \
                            arrange_main_curtain(main_win, self.line_list, self.ele_list, self.virtual_boundary)
        tv_sofa_wall = get_adjacent_bounds(main_wall, self.virtual_boundary)

        tv_sofa_wall_1 = tv_sofa_area_wall(tv_sofa_wall[0], self.boundary)
        tv_sofa_wall_2 = tv_sofa_area_wall(tv_sofa_wall[1], self.boundary)
        for avoid in avoid_area:
            if avoid == None:
                avoid_area.remove(None)
        tv_sofa_wall_list_1 = []
        tv_sofa_wall_list_1_length = []
        tv_sofa_wall_list_2 = []
        tv_sofa_wall_list_2_length = []
        for avoid in avoid_area:
            if tv_sofa_wall_1.seg.contains(avoid.seg):
                tv_sofa_wall_1 = update_tv_sofa_wall(tv_sofa_wall_1, avoid, main_wall, main_wall.normal)
                tv_sofa_wall_list_1.append(tv_sofa_wall_1)
                tv_sofa_wall_list_1_length.append(tv_sofa_wall_1.seg.length)
            if tv_sofa_wall_2.seg.contains(avoid.seg):
                tv_sofa_wall_2 = update_tv_sofa_wall(tv_sofa_wall_2, avoid, main_wall, main_wall.normal)
                tv_sofa_wall_list_2.append(tv_sofa_wall_2)
                tv_sofa_wall_list_2_length.append(tv_sofa_wall_2.seg.length)

        for seg in tv_sofa_wall_list_1:
            if seg.seg.length == min(tv_sofa_wall_list_1_length):
                tv_sofa_wall_1 = seg
        for seg in tv_sofa_wall_list_2:
            if seg.seg.length == min(tv_sofa_wall_list_2_length):
                tv_sofa_wall_2 = seg

        if tv_sofa_wall_1.seg.length >= tv_sofa_wall_2.seg.length:
            TV_wall = tv_sofa_wall_2
            TV_wall.normal = tv_sofa_wall[1].normal
            sofa_wall = tv_sofa_wall_1
            sofa_wall.normal = tv_sofa_wall[0].normal
        elif tv_sofa_wall_1.seg.length < tv_sofa_wall_2.seg.length:
            TV_wall = tv_sofa_wall_1
            TV_wall.normal = tv_sofa_wall[0].normal
            sofa_wall = tv_sofa_wall_2
            sofa_wall.normal = tv_sofa_wall[1].normal

        if TV_wall.seg.length < LIVINGROOM_TV_BENCH_WIDTH[0] or sofa_wall.seg.length < SOFAL_L1_L2[2200]:
            sofa_wall = main_wall
            for seg in self.virtual_boundary.seg_list:
                if main_wall.line.is_parallel(seg.line) and seg is not main_wall:
                    TV_wall = seg
        rand = random.random()
        TV_wall_len = TV_wall.seg.length
        TVbench_w_lst = [w for w in LIVINGROOM_TV_BENCH_WIDTH if w < TV_wall_len]
        TVbench_width = LIVINGROOM_TV_BENCH_WIDTH[get_idx_probability(TVbench_w_lst, rand)]
        # 放置电视柜
        mid = Point2D(int(TV_wall.seg.midpoint.x), int(TV_wall.seg.midpoint.y))
        p1 = mid + TV_wall.dir.p2 * int(TVbench_width / 2)
        p2 = mid - TV_wall.dir.p2 * int(TVbench_width / 2)

        p1, p2 = DY_segment.get_p1_p2_from_normal(TV_wall.normal, p1, p2)
        bl = DY_segment(p1, p2)
        TVben = TVbench(bl)
        self.ele_list.append(TVben)
        # 配置沙发茶几区
        side_dis = get_adjacent_bounds(main_wall, self.virtual_boundary)[0].seg.length
        if sofa_wall is main_wall:
            TV_tea_dis = side_dis - TVben.len - DIS_TVBEN_TEA_MIN
        else:
            TV_tea_dis = main_wall.seg.length - TVben.len - DIS_TVBEN_TEA_MIN

        if TV_tea_dis > SOFAANDTEA_MAX_LEN:
            sofa_tea_len = SOFAANDTEA_MAX_LEN
        else:
            sofa_tea_len = TV_tea_dis
        if win_flag:
            if TV_wall.seg.intersection(self.main_curtain.boundary.polygon) != []:
                sofa_tea_width = TV_wall.seg.length - self.main_curtain.len
            else:
                sofa_tea_width = TV_wall.seg.length
        else:
            sofa_tea_width = TV_wall.seg.length
        if sofa_wall is main_wall:
            if side_dis > SOFAANDTEA_MAX_LEN * 2:
                side_dis = SOFAANDTEA_MAX_LEN * 2
            mid_sofa = (mid + TV_wall.normal.p2 * (side_dis))
        else:
            mid_sofa = (mid + TV_wall.normal.p2 * (main_wall.seg.length))
        p1 = mid_sofa + sofa_wall.dir.p2 * (sofa_tea_width / 2)
        # p2 = p1 + main_wall.normal.p2 * sofa_tea_width
        p2 = mid_sofa - sofa_wall.dir.p2 * (sofa_tea_width / 2)
        p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_wall.normal, p1, p2)
        bl = DY_segment(p1, p2)
        if win_flag:
            if self.main_curtain.boundary.polygon.intersection(bl.seg) != []:
                mid_sofa = mid_sofa - TV_wall.normal.p2 * self.main_curtain.len
                p1 = mid_sofa + sofa_wall.dir.p2 * (sofa_tea_width / 2)
                p2 = mid_sofa - sofa_wall.dir.p2 * (sofa_tea_width / 2)
                p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_wall.normal, p1, p2)
                bl = DY_segment(p1, p2)
        sofa_tea_area = Sofa_Tea_area()
        sofa_tea_area.set_pos(bl, sofa_tea_len)
        self.ele_list.append(sofa_tea_area)
        sofa_tea_area.run()
        '''
        躺椅部分暂时不放
        dis = sofa_tea_area.frontline.line.distance(TVben.frontline.line.p1)
        if dis > RECLINERS_WIDTH_LEN[1]:
            if win_flag:
                    p1_list = sofa_tea_area.frontline.line.intersection(self.main_curtain.frontline.line)
                    if p1_list != []:
                        p1 = p1_list[0]
                    else:
                        p1 = sofa_tea_area.frontline.seg.p1
            else:
                p1 = sofa_tea_area.frontline.seg.p1
            if sofa_wall is main_wall:
                p2 = p1 + get_adjacent_bounds(main_wall, self.virtual_boundary)[0].normal.p2 * RECLINERS_WIDTH_LEN[0]

            else:
                p2 = p1 + main_wall.normal.p2 * RECLINERS_WIDTH_LEN[0]
            p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_tea_area.backline.normal, p1, p2)
            bl = DY_segment(p1, p2)
            re = CommonElement.Recliner(bl)
            self.ele_list.append(re)
        '''
        return True
# **************************************(4,0,1,1)#begin#*******************************************************
    def run4011(self):
        for l in self.line_list:
            if isinstance(l, Window):
                win_normal = l.normal
            if isinstance(l, Border):
                bord_normal = l.normal
        if win_normal.is_parallel(bord_normal):
            self.run4011_parallel()
        elif win_normal.is_perpendicular(bord_normal):
            self.run4011_perpendicular()
            # print("perpendicular")

        return True

    def run4011_parallel(self):
        # 放置窗帘
        self.win_list, self.main_curtain, self.main_win_wall = \
            mb_uti.arrange_main_curtain(self.line_list, self.ele_list)
        # 选择一边界放置电视柜
        # 如果虚边界是完整边界，随机选择与窗平行的墙体放置电视柜
        # 如果不是，通过和虚边界重合的边界，离虚边界较近的墙体放置电视柜
        rand = random.random()
        border_list = [b for b in self.line_list if isinstance(b, Border)]
        border_bound = [s for s in self.boundary.seg_list if s.seg.contains(border_list[0].seg)]
        TV_wall = get_adjacent_bounds(self.main_win_wall, self.boundary)
        if border_list[0].seg != border_bound[0].seg:
            border_mid = border_list[0].seg.midpoint
            dis0 = TV_wall[0].line.distance(border_mid)
            dis1 = TV_wall[1].line.distance(border_mid)
            if dis0 < dis1:
                TV_wall = TV_wall[0]
            else:
                TV_wall = TV_wall[1]
        else:
            TV_wall = TV_wall[math.floor(rand * 2)]
        # 按一定几率选择电视柜的宽度
        TV_wall_len = TV_wall.seg.length - self.main_curtain.len
        TVbench_w_lst = [w for w in LIVINGROOM_TV_BENCH_WIDTH if w < TV_wall_len]
        TVbench_width = LIVINGROOM_TV_BENCH_WIDTH[get_idx_probability(TVbench_w_lst, rand)]
        self.run4011_common(TV_wall, TVbench_width)

    def run4011_perpendicular(self):
        # 放置窗帘
        self.win_list, self.main_curtain, self.main_win_wall = \
            mb_uti.arrange_main_curtain(self.line_list, self.ele_list)
        # 选择非虚拟边界的一面墙放置电视柜
        TV_wall_list = get_adjacent_bounds(self.main_win_wall, self.boundary)
        border_list = [b for b in self.line_list if isinstance(b, Border)]
        for w in TV_wall_list:
            if w.seg.contains(border_list[0].seg) is False:
                TV_wall = w
        # 按一定几率选择电视柜的宽度
        rand = random.random()
        TV_wall_len = TV_wall.seg.length - self.main_curtain.len
        TVbench_w_lst = [w for w in LIVINGROOM_TV_BENCH_WIDTH if w < TV_wall_len]
        TVbench_width = LIVINGROOM_TV_BENCH_WIDTH[get_idx_probability(TVbench_w_lst, rand)]
        self.run4011_common(TV_wall, TVbench_width)

    def run4011_common(self, TV_wall, TVbench_width):
        # 放置电视柜
        mid = Point2D(int(TV_wall.seg.midpoint.x),int(TV_wall.seg.midpoint.y))
        # mid = TV_wall.seg.midpoint
        p1 = mid + TV_wall.dir.p2 * int(TVbench_width/2)
        p2 = mid - TV_wall.dir.p2 * int(TVbench_width/2)

        p1, p2 = DY_segment.get_p1_p2_from_normal(TV_wall.normal,p1,p2)
        bl = DY_segment(p1, p2)
        TVben = TVbench(bl)
        self.ele_list.append(TVben)
        # 配置沙发茶几区
        TV_tea_dis = self.main_win_wall.seg.length - TVben.len - DIS_TVBEN_TEA_MIN
        if TV_tea_dis > SOFAANDTEA_MAX_LEN:
            sofa_tea_len = SOFAANDTEA_MAX_LEN
        else:
            sofa_tea_len = TV_tea_dis
        sofa_tea_width = TV_wall.seg.length - self.main_curtain.len
        sofa_wall = get_adjacent_bounds(self.main_win_wall, self.boundary)
        sofa_wall = [wall for wall in sofa_wall if wall.seg != TV_wall.seg][0]
        p1 = self.main_curtain.frontline.line.intersection(sofa_wall.line)[0]
        p2 = p1 + self.main_win_wall.normal.p2 * sofa_tea_width
        p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_wall.normal, p1, p2)
        bl = DY_segment(p1, p2)
        sofa_tea_area = Sofa_Tea_area()
        sofa_tea_area.set_pos(bl, sofa_tea_len)
        self.ele_list.append(sofa_tea_area)
        sofa_tea_area.run()

        # 配置躺椅
        dis = sofa_tea_area.frontline.line.distance(TVben.frontline.line.p1)
        if dis > RECLINERS_WIDTH_LEN[1]:
            p1 = sofa_tea_area.frontline.line.intersection(self.main_curtain.frontline.line)[0]
            p2 = p1 + self.main_win_wall.normal.p2 * RECLINERS_WIDTH_LEN[0]
            p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_tea_area.backline.normal, p1, p2)
            bl = DY_segment(p1, p2)
            re = CommonElement.Recliner(bl)
            self.ele_list.append(re)

        return True

    # **************************************(4,0,1,1)#end#*********************************************************
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
    #**************************************(4,1,1,1)#begin#********************************************************
    def run4111(self):
       # try:
        for l in self.line_list:
            if isinstance(l, Window):
                win_normal = l.normal
            if isinstance(l, Border):
                 bord_normal = l.normal
        for d in self.ele_list:  # 获取门的points
            if isinstance(d, CommonElement.Door):
                door = d
        if win_normal.is_parallel(bord_normal):
            self.run_4111_parallel(door)
            # print("parallel case now")
        elif win_normal.is_perpendicular(bord_normal):
            self.run_4111_perpendicular(door)
            # print("perpendicular case now")

        return True

    def run_4111_parallel(self,door):
        # 放置窗帘
        self.win_list, self.main_curtain, self.main_win_wall = \
            mb_uti.arrange_main_curtain(self.line_list, self.ele_list)
        # for d in self.ele_list:  # 获取门的points
        #     if isinstance(d, CommonElement.Door):
        door_points = door.point_list
        # 电视柜会被确定放在门所在墙上
        rand = random.random()
        border_list = [b for b in self.line_list if isinstance(b, Border)]
        border_bound = [s for s in self.boundary.seg_list if s.seg.contains(border_list[0].seg)]
        TV_wall = get_adjacent_bounds(self.main_win_wall, self.boundary)

        if TV_wall[0].line.distance(door_points[0]) \
            < TV_wall[1].line.distance(door_points[0]):
            TV_wall = TV_wall[0]
        else:
            TV_wall = TV_wall[1]
        adj_TVwalls = get_adjacent_bounds(TV_wall, self.boundary)
        d1 = adj_TVwalls[0].line.distance(door.backline.p1)
        d2 = adj_TVwalls[0].line.distance(door.backline.p2)
        d3 = adj_TVwalls[1].line.distance(door.backline.p1)
        d4 = adj_TVwalls[1].line.distance(door.backline.p2)
        d_door_wall_min = min(d1, d2, d3, d4)
        # 按一定几率选择电视柜的宽度
        TV_wall_len = TV_wall.seg.length - self.main_curtain.len - DOUBLE_LEN - d_door_wall_min
        TVbench_w_lst = [w for w in LIVINGROOM_TV_BENCH_WIDTH if w < TV_wall_len]
        # idx = get_idx_probability(TVbench_w_lst, rand)
        # if idx >= 1:
        #     TVbench_width = LIVINGROOM_TV_BENCH_WIDTH[idx - 1]
        # else:
        #     TVbench_width = LIVINGROOM_TV_BENCH_WIDTH[idx]
        TVbench_width = LIVINGROOM_TV_BENCH_WIDTH[get_idx_probability(TVbench_w_lst, rand)]#rand
        self.run4111_common_parallel(TV_wall, TVbench_width)

    def run_4111_perpendicular(self,door):

        # 放置窗帘
        self.win_list, self.main_curtain, self.main_win_wall = \
            mb_uti.arrange_main_curtain(self.line_list, self.ele_list)
        # 选择非虚拟边界的一面墙放置电视柜,可以确定电视柜在border对面
        TV_wall_list = get_adjacent_bounds(self.main_win_wall, self.boundary)
        border_list = [b for b in self.line_list if isinstance(b, Border)]
        for w in TV_wall_list:
            if w.seg.contains(border_list[0].seg) is False:
                TV_wall = w
        adj_TVwalls = get_adjacent_bounds(TV_wall,self.boundary)
        d1 = adj_TVwalls[0].line.distance(door.backline.p1)
        d2 = adj_TVwalls[0].line.distance(door.backline.p2)
        d3 = adj_TVwalls[1].line.distance(door.backline.p1)
        d4 = adj_TVwalls[1].line.distance(door.backline.p2)
        d_door_wall_min = min(d1,d2,d3,d4)
        # 按一定几率选择电视柜的宽度&需要考虑门的加入以及门与墙的边距
        rand = random.random()
        TV_wall_len = TV_wall.seg.length - self.main_curtain.len - DOUBLE_LEN - d_door_wall_min
        TVbench_w_lst = [w for w in LIVINGROOM_TV_BENCH_WIDTH if w < TV_wall_len]
        # idx = get_idx_probability(TVbench_w_lst, rand)#此方法并不完全cover
        # if idx >= 1:
        #     TVbench_width = LIVINGROOM_TV_BENCH_WIDTH[idx - 1]
        # else:
        #     TVbench_width = LIVINGROOM_TV_BENCH_WIDTH[idx]
        TVbench_width = LIVINGROOM_TV_BENCH_WIDTH[get_idx_probability(TVbench_w_lst, rand)]  # rand
        self.run4111_common_perpendicular(TV_wall, TVbench_width,d_door_wall_min)

    def run4111_common_parallel(self, TV_wall, TVbench_width):
        # 放置电视柜
        # 先获取门的位置判断其靠窗户还是远离窗户
        for d in self.ele_list:  # 获取门的points and backline
            if isinstance(d, CommonElement.Door):
                door_points = d.point_list
                door_backline = d.backline
        op_borders = get_opposite_bounds(self.main_win_wall,self.boundary)
        is_recliners = False
        mid_point = Point2D(int(TV_wall.seg.midpoint.x), int(TV_wall.seg.midpoint.y))
        if self.main_win_wall.line.distance(door_points[0]) \
                > op_borders[0].line.distance(door_points[0]):
            # mid = TV_wall.seg.midpoint - self.main_win_wall.normal.p2 * int(DOUBLE_LEN / 2 - CURTAIN_LEN/2)
            mid = mid_point - self.main_win_wall.normal.p2 * int(DOUBLE_LEN / 2 )
            is_recliners = True
        else:
            # mid = TV_wall.seg.midpoint + self.main_win_wall.normal.p2 * int(DOUBLE_LEN / 2 + CURTAIN_LEN/2)
            mid = mid_point + self.main_win_wall.normal.p2 * int(DOUBLE_LEN / 2 )
            is_recliners = False
        p1 = mid + TV_wall.dir.p2 * int(TVbench_width/2)
        p2 = mid - TV_wall.dir.p2 * int(TVbench_width/2)
        p1, p2 = DY_segment.get_p1_p2_from_normal(TV_wall.normal,p1,p2)
        bl = DY_segment(p1, p2)
        TVben = TVbench(bl)
        self.ele_list.append(TVben)
        # 配置沙发茶几区
        TV_tea_dis = self.main_win_wall.seg.length - TVben.len - DIS_TVBEN_TEA_MIN
        if TV_tea_dis > SOFAANDTEA_MAX_LEN:
            sofa_tea_len = SOFAANDTEA_MAX_LEN
        else:
            sofa_tea_len = TV_tea_dis
        sofa_tea_width = TV_wall.seg.length - self.main_curtain.len - DOUBLE_LEN
        sofa_wall = get_adjacent_bounds(self.main_win_wall, self.boundary)
        sofa_wall = [wall for wall in sofa_wall if wall.seg != TV_wall.seg][0]
        if is_recliners:
            p1 = self.main_curtain.frontline.line.intersection(sofa_wall.line)[0]
            p2 = p1 + self.main_win_wall.normal.p2 * sofa_tea_width
            p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_wall.normal, p1, p2)
            bl = DY_segment(p1, p2)
        else:
            # p1 = self.main_curtain.frontline.line.intersection(sofa_wall.line)[0]-(0,DOUBLE_LEN)
            p1 = op_borders[0].line.intersection(sofa_wall.line)[0]
            p2 = p1 - self.main_win_wall.normal.p2 * sofa_tea_width
            p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_wall.normal, p1, p2)
            bl = DY_segment(p1, p2)
        sofa_tea_area = Sofa_Tea_area()
        sofa_tea_area.set_pos(bl, sofa_tea_len)
        self.ele_list.append(sofa_tea_area)
        sofa_tea_area.run()

        # 配置躺椅
        if is_recliners:
            dis = sofa_tea_area.frontline.line.distance(TVben.frontline.line.p1)
            if dis > RECLINERS_WIDTH_LEN[1]:
                p1 = sofa_tea_area.frontline.line.intersection(self.main_curtain.frontline.line)[0]
                p2 = p1 + self.main_win_wall.normal.p2 * RECLINERS_WIDTH_LEN[0]
                p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_tea_area.backline.normal, p1, p2)
                bl = DY_segment(p1, p2)
                re = CommonElement.Recliner(bl)
                self.ele_list.append(re)
        else:
            pass

        return True
    
    def run4111_common_perpendicular(self, TV_wall, TVbench_width,d_door_wall_min):
        # 放置电视柜
        # 先获取门的位置 1.门与虚边界垂直 2.门与虚边界平行
        is_recliners = False
        for d in self.ele_list:  # 获取门的points and backline
            if isinstance(d, CommonElement.Door):
                door_points = d.point_list
                door_backline = d.backline
        op_borders = get_opposite_bounds(TV_wall,self.boundary)
        mid_point = Point2D(int(TV_wall.seg.midpoint.x), int(TV_wall.seg.midpoint.y))
        if door_backline.normal.is_perpendicular(op_borders[0].normal):
            tv_win_p = self.main_curtain.frontline.line.intersection(TV_wall.line)[0]
            mid = mid_point - self.main_win_wall.normal.p2 * int(DOUBLE_LEN / 2 + d_door_wall_min / 2)
            is_recliners = True
            p1 = mid + self.main_win_wall.normal.p2 * int(TVbench_width/2)
            p2 = mid - self.main_win_wall.normal.p2 * int(TVbench_width/2)
            p1, p2 = DY_segment.get_p1_p2_from_normal(TV_wall.normal,p1,p2)
            bl = DY_segment(p1, p2)
            TVben = TVbench(bl)
            self.ele_list.append(TVben)
            # 配置沙发茶几区
            TV_tea_dis = self.main_win_wall.seg.length - TVben.len - DIS_TVBEN_TEA_MIN
            if TV_tea_dis > SOFAANDTEA_MAX_LEN:
                sofa_tea_len = SOFAANDTEA_MAX_LEN
            else:
                sofa_tea_len = TV_tea_dis
            sofa_tea_width = TV_wall.seg.length - self.main_curtain.len - DOUBLE_LEN
            sofa_wall = get_adjacent_bounds(self.main_win_wall, self.boundary)
            sofa_wall = [wall for wall in sofa_wall if wall.seg != TV_wall.seg][0]
            p1 = self.main_curtain.frontline.line.intersection(sofa_wall.line)[0]
            p2 = p1 + self.main_win_wall.normal.p2 * sofa_tea_width
            p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_wall.normal, p1, p2)
            bl = DY_segment(p1, p2)
            sofa_tea_area = Sofa_Tea_area()
            sofa_tea_area.set_pos(bl, sofa_tea_len)
            self.ele_list.append(sofa_tea_area)
            sofa_tea_area.run()

            # 配置躺椅
            if is_recliners:
                dis = sofa_tea_area.frontline.line.distance(TVben.frontline.line.p1)
                if dis > RECLINERS_WIDTH_LEN[1]:
                    p1 = sofa_tea_area.frontline.line.intersection(self.main_curtain.frontline.line)[0]
                    p2 = p1 + self.main_win_wall.normal.p2 * RECLINERS_WIDTH_LEN[0]
                    p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_tea_area.backline.normal, p1, p2)
                    bl = DY_segment(p1, p2)
                    re = CommonElement.Recliner(bl)
                    self.ele_list.append(re)
            else:
                pass

            return True
        else:
            for d in self.ele_list:  # 获取门的points and backline
                if isinstance(d, CommonElement.Door):
                    door_points = d.point_list
                    door_backline = d.backline
            win_op = get_opposite_bounds(self.main_win_wall, self.boundary)

            is_recliners = False
            sofa_tea_width = TV_wall.seg.length - self.main_curtain.len - DOUBLE_LEN - d_door_wall_min
            sofa_wall = get_adjacent_bounds(self.main_win_wall, self.boundary)
            sofa_wall = [wall for wall in sofa_wall if wall.seg != TV_wall.seg][0]
            sofa_mid = Point2D(int(sofa_wall.seg.midpoint.x),int(sofa_wall.seg.midpoint.y))
            if self.main_win_wall.line.distance(door_points[0]) < win_op[0].line.distance(door_points[0]):
                # mid = TV_wall.seg.midpoint + TV_wall.dir.p2 * int(DOUBLE_LEN / 2 )
                mid = mid_point + self.main_win_wall.normal.p2 * int(DOUBLE_LEN / 2 + CURTAIN_LEN / 2 + d_door_wall_min / 2 )
                mid1 =  sofa_mid + self.main_win_wall.normal.p2 * int(DOUBLE_LEN / 2 + CURTAIN_LEN / 2 + d_door_wall_min / 2 )
                # mid = TV_wall.seg.midpoint + self.main_win_wall.normal.p2 * int(DOUBLE_LEN / 2 )
                # mid1 = sofa_wall.seg.midpoint + self.main_win_wall.normal.p2 * int(DOUBLE_LEN / 2 )
            else:
                # mid = TV_wall.seg.midpoint - TV_wall.dir.p2 * int(DOUBLE_LEN / 2)
                mid = mid_point - self.main_win_wall.normal.p2 * int(DOUBLE_LEN / 2 - CURTAIN_LEN / 2 + d_door_wall_min / 2 )
                mid1 = sofa_mid - self.main_win_wall.normal.p2 * int(DOUBLE_LEN / 2 - CURTAIN_LEN / 2 + d_door_wall_min / 2 )
                # mid = TV_wall.seg.midpoint - self.main_win_wall.normal.p2 * int(DOUBLE_LEN / 2 )
                # mid1 = sofa_wall.seg.midpoint - self.main_win_wall.normal.p2 * int(DOUBLE_LEN / 2 )
            p1 = mid + TV_wall.dir.p2 * int(TVbench_width / 2)
            p2 = mid - TV_wall.dir.p2 * int(TVbench_width / 2)
            p1, p2 = DY_segment.get_p1_p2_from_normal(TV_wall.normal, p1, p2)
            bl = DY_segment(p1, p2)
            TVben = TVbench(bl)
            self.ele_list.append(TVben)
            # 配置沙发茶几区
            TV_tea_dis = self.main_win_wall.seg.length - TVben.len - DIS_TVBEN_TEA_MIN
            if TV_tea_dis > SOFAANDTEA_MAX_LEN:
                sofa_tea_len = SOFAANDTEA_MAX_LEN
            else:
                sofa_tea_len = TV_tea_dis
            if self.main_win_wall.line.distance(bl.seg.midpoint) < \
                    win_op[0].line.distance(bl.seg.midpoint):
                # p11 = mid1 + sofa_wall.dir.p2 * int((sofa_wall.seg.length - DOUBLE_LEN ) / 2 - CURTAIN_LEN / 2)
                # p22 = mid1 - sofa_wall.dir.p2 * int((sofa_wall.seg.length - DOUBLE_LEN ) / 2 - CURTAIN_LEN / 2)
                p11 = mid1 + sofa_wall.dir.p2 * int(sofa_tea_width / 2)
                p22 = mid1 - sofa_wall.dir.p2 * int(sofa_tea_width / 2)
            else:
                # p11 = mid1 + sofa_wall.dir.p2 * int((sofa_wall.seg.length - DOUBLE_LEN) / 2)
                # p22 = mid1 - sofa_wall.dir.p2 * int((sofa_wall.seg.length - DOUBLE_LEN) / 2)
                p11 = mid1 + sofa_wall.dir.p2 * int(sofa_tea_width / 2)
                p22 = mid1 - sofa_wall.dir.p2 * int(sofa_tea_width / 2)
            p11, p22 = DY_segment.get_p1_p2_from_normal(sofa_wall.normal, p11, p22)
            bl = DY_segment(p11, p22)
            sofa_tea_area = Sofa_Tea_area()
            sofa_tea_area.set_pos(bl, sofa_tea_len)
            self.ele_list.append(sofa_tea_area)
            sofa_tea_area.run()
            # 配置躺椅
            if is_recliners:
                dis = sofa_tea_area.frontline.line.distance(TVben.frontline.line.p1)
                if dis > RECLINERS_WIDTH_LEN[1]:
                    p1 = sofa_tea_area.frontline.line.intersection(self.main_curtain.frontline.line)[0]
                    p2 = p1 + self.main_win_wall.normal.p2 * RECLINERS_WIDTH_LEN[0]
                    p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_tea_area.backline.normal, p1, p2)
                    bl = DY_segment(p1, p2)
                    re = CommonElement.Recliner(bl)
                    self.ele_list.append(re)
            else:
                pass
            return  True


        # **************************************(4,1,1,1)#end#*********************************************************
    # **************************************(4,1,1,1)#end#*********************************************************
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
    # **************************************(4,1,0,2)#begin#*******************************************************
    def run4102(self):
        for d in self.ele_list:
            if isinstance(d, CommonElement.Door):
                door = d
                break
        #电视柜所在墙包含门
        tv_wall = [tv for tv in self.boundary.seg_list if door.boundary.polygon.intersection(tv.seg)][0]
        d_door_wall_min = []
        sofa_wall = get_opposite_bounds(tv_wall,self.boundary)[0]
        border_list = [b for b in self.line_list if isinstance(b, Border)]
        for b in border_list:
        #     d_door_wall_min.append(door.boundary.polygon.\
        #                            intersection(tv_wall.seg).distance(b.line))
             d_door_wall_min.append(get_min_dis_seg_boundary(b,door.boundary))
        d_min = min(d_door_wall_min)
        #获得电视柜的合理宽度
        rand = random.random()
        TV_wall_len = tv_wall.seg.length - DOUBLE_LEN - d_min
        TVbench_w_lst = [w for w in LIVINGROOM_TV_BENCH_WIDTH if w < TV_wall_len]
        TVbench_width = LIVINGROOM_TV_BENCH_WIDTH[get_idx_probability(TVbench_w_lst, rand)]  # rand
        d1 = border_list[0].line.distance(door.boundary.polygon.centroid)
        d2 = border_list[1].line.distance(door.boundary.polygon.centroid)
        #放置电视柜
        mid_point = Point2D(int(tv_wall.seg.midpoint.x),int(tv_wall.seg.midpoint.y))
        if d1 < d2:
            mid = mid_point- border_list[1].normal.p2 * int((DOUBLE_LEN + d_min) / 2)
        else:
            mid = mid_point - border_list[0].normal.p2 * int((DOUBLE_LEN + d_min) / 2)
        tv_p1 = mid + tv_wall.dir.p2 * int(TVbench_width / 2)
        tv_p2 = mid - tv_wall.dir.p2 * int(TVbench_width / 2)
        tv_p1,tv_p2 = DY_segment.\
            get_p1_p2_from_normal(tv_wall.normal,tv_p1,tv_p2)
        tv_bl = DY_segment(tv_p1,tv_p2)
        tvben = TVbench(tv_bl)
        self.ele_list.append(tvben)
        # 配置沙发茶几区
        # if border_list[0].seg.length < border_list[1].seg.length:#此处不妥，因为虚边界有可能不是完整的
        bd_wall_len = get_two_wall_dis(tv_wall,sofa_wall)
        TV_tea_dis = bd_wall_len - tvben.len - DIS_TVBEN_TEA_MIN
        if TV_tea_dis > SOFAANDTEA_MAX_LEN:
            sofa_tea_len = SOFAANDTEA_MAX_LEN
        else:
            sofa_tea_len = TV_tea_dis
        sofa_tea_width = tv_wall.seg.length - d_min - DOUBLE_LEN
        if d1 < d2:
            p1 = sofa_wall.line.intersection(border_list[1].line)[0]
            p2 = p1 + border_list[1].normal.p2 * sofa_tea_width
            p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_wall.normal, p1, p2)
            sofa_bl = DY_segment(p1, p2)
        else:
            p1 = sofa_wall.line.intersection(border_list[0].line)[0]
            p2 = p1 + border_list[0].normal.p2 * sofa_tea_width
            p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_wall.normal, p1, p2)
            sofa_bl = DY_segment(p1, p2)
        sofa_tea_area = Sofa_Tea_area()
        sofa_tea_area.set_pos(sofa_bl, sofa_tea_len)
        self.ele_list.append(sofa_tea_area)
        sofa_tea_area.run()


