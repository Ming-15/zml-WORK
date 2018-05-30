# -*- coding:utf-8 -*-

import random

import AutoLayout.BaseModual as BaseModual
import AutoLayout.CommonElement as CommonElement
from AutoLayout.bathroom.Element import *
from  AutoLayout.bathroom.settings import *
from AutoLayout.helpers import *
import AutoLayout.DY_Line as DY_Line
from AutoLayout.bathroom.utility import *

class Bathroom(BaseModual.Region):
    def __init__(self):
        super(Bathroom, self).__init__()
        self.main_win_wall = None
        #use for virtual case below
        self.door_list = []
        self.vir_door_list = []
        self.win = []
        self.vir_win = []#no use here now,maybe in future

    def run(self):
        res = self.check_room_size_type()

    def check_room_size_type(self):
        xmin, ymin, xmax, ymax = self.boundary.polygon.bounds
        xlen = xmax - xmin
        ylen = ymax - ymin
        if xlen < MIN_SIZE or xlen > MAX_SIZE or ylen < MIN_SIZE or \
                        ylen > MAX_SIZE:
            # raise Exception("warning:卫生间功能区长度或者宽度不满足")
            self.run_abnormal()

            return True
        if abs(self.boundary.polygon.area) < MIN_SIZE * MIN_SIZE:
            # raise Exception("warning:卫生间功能区面积不满足")
            self.run_abnormal()

            return True
        arrangement_dic = {
            (4, 1, 0): self.run410,  # 顶点4，门1，窗户0，下同
            (4, 1, 1): self.run411
            # undo
        }
        key = (len(self.boundary.polygon.vertices), self.doors, self.windows)
        if not arrangement_dic.get(key, False):
            # raise Exception("warning:卫生间暂时不支持此户型")
            self.run_sub_regions()
            return True
        result = arrangement_dic.get(key)()

    def run410(self):
        js = 0
        mk = 0
        t_bl = None
        for e in self.ele_list:
            if isinstance(e, CommonElement.Door):
                door = e
                # if self.vir_door_list:
                #     door = self.vir_door_list[0]
        for s in self.boundary.seg_list:
            if s.seg.is_parallel(door.backline.seg) and \
                    door.boundary.polygon.intersection(s.seg):
                door_wall = s
                # if s.seg.contains(door.backline.seg):
                #     door_wall = s
        # 初始化确定各个墙并得到进深和面宽尺寸
        mk = door_wall.seg.length
        op_door_wall = get_opposite_bounds(door_wall, self.boundary)[0]
        js_walls = get_adjacent_bounds(door_wall, self.boundary)
        js = js_walls[0].seg.length
        wash_flag1 = False
        wash_flag2 = False
        wash_flag3 = False
        wh_layout_flag = False
        # wall_doorbody_dis1 = js_walls[0].line.distance(door.door_body.seg.midpoint)
        # wall_doorbody_dis2 = js_walls[1].line.distance(door.door_body.seg.midpoint)
        # if wall_doorbody_dis1 < wall_doorbody_dis2:
        #     far_wall = js_walls[1]
        #     near_wall = js_walls[0]
        # else:
        #     far_wall = js_walls[0]
        #     near_wall = js_walls[1]
        # 初始化确定各个墙并得到进深和面宽尺寸end
        # #确定洗衣机摆放方式
        # if mk < MID_W11:
        #     wash_flag1 = False
        # else:
        #     wash_flag1 = True
        # wash_flag2 = False

        # if js > max(WASHBASIN_W) + TOILET_DEV_W:
        #     wb_ind = random.randint(0,len(WASHBASIN_W)-1)
        #     wb_should = WASHBASIN_W[wb_ind]
        # else:
        #     wb_should = WASHBASIN_W[0]
        # 判断门两边的墙的长度 X1 和 X2并修改门的body位置
        half_door_bl = door.backline.seg.length / 2
        X1 = js_walls[0].line.distance(door.backline.seg.midpoint)
        X2 = js_walls[1].line.distance(door.backline.seg.midpoint)
        X1 = X1 - half_door_bl
        X2 = X2 - half_door_bl
        door_body = [seg for seg in door.boundary.seg_list \
                     if seg.seg.is_perpendicular(door.backline.seg)]
        ###这儿有问题?
        # 判断们中心点距离哪边墙近，并放置门，区分近墙和远点
        if js_walls[0].line.distance(door_body[0].seg.midpoint) == X1:
            door_body_near0 = door_body[0]
        if js_walls[0].line.distance(door_body[1].seg.midpoint) == X1:
            door_body_near0 = door_body[1]
        if js_walls[1].line.distance(door_body[0].seg.midpoint) == X2:
            door_body_near1 = door_body[0]
        if js_walls[1].line.distance(door_body[1].seg.midpoint) == X2:
            door_body_near1 = door_body[1]
        if X1 >= X2:  # 区分近点远点
            door.set_body(door_body_near1)
            near_door_wall = js_walls[1]
            far_door_wall = js_walls[0]

        else:
            door.set_body(door_body_near0)
            near_door_wall = js_walls[0]
            far_door_wall = js_walls[1]
        T2X = min(near_door_wall.line.distance(door.backline.p1),
                  near_door_wall.line.distance(door.backline.p2))
        T1X = min(far_door_wall.line.distance(door.backline.p1),
                  far_door_wall.line.distance(door.backline.p2))

        # 开门处有空间就放置WB
        if T2X >= DOOR_BODY_TO_WALL:
            wb_should = WASHBASIN_W[1]
            if T2X > WAHING_MAC_L:
                wash_flag1 = True  # 设置洗衣机摆放标志位
                wash_flag2 = False
        else:
            wb_should = WASHBASIN_W[0]
            wash_flag1 = False
        # 理想状态：在开门正面开始放置组件:面盆->坐便->淋浴房->洗衣机（需要根据尺寸判断）
        if js >= JS_T1 and js <= JS_T2:  # 面盆需要首选放在门的正对面（进深在[1.3-2.0m]）
            # 放置面盆
            if js <= 1500:  # 超小户型
                wb_should = WASHBASIN_W[0]
                p_t1 = op_door_wall.seg.intersection(far_door_wall.seg)[0] + op_door_wall.normal.p2 * 100
                p_t2 = p_t1 + op_door_wall.normal.p2 * TOILET_DEV_W
                p_t1, p_t2 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal, p_t1, p_t2)
                t_bl = DY_segment(p_t1, p_t2)
                tt = ToiletDevice(t_bl)
                self.ele_list.append(tt)
                p_s1 = op_door_wall.seg.intersection(near_door_wall.seg)[0] + op_door_wall.normal.p2 * 150
                p_s2 = p_s1 + op_door_wall.normal.p2 * int(SPRAY_W)
                dir = near_door_wall.normal
                self.sr_put(p_s1, p_s2, dir)
                if T1X > wb_should:
                    p_m1 = door_wall.seg.intersection(far_door_wall.seg)[0]
                    p_m2 = p_m1 + far_door_wall.normal.p2 * wb_should
                    dir = door_wall.normal
                    self.wb_put(p_m1, p_m2, dir)
                elif T1X > WASHBASIN_L and js > (TOILET_DEV_W + 100 + wb_should):
                    p_m1 = door_wall.seg.intersection(far_door_wall.seg)[0]
                    p_m2 = p_m1 + door_wall.normal.p2 * wb_should
                    dir = far_door_wall.normal
                    self.wb_put(p_m1, p_m2, dir)

            else:
                door_wall_inter = door.boundary.polygon.intersection(door_wall.seg)
                if isinstance(door_wall_inter[0], Segment2D):
                    dw_inter = door_wall_inter#jxh:tongting code here modified by jxh
                else:
                    dw_inter = DY_segment(door_wall_inter[0], door_wall_inter[1])
                if T2X > SHOWER_W:
                    p_m_mid = Point2D(int(dw_inter.seg.midpoint.x), int(dw_inter.seg.midpoint.y)) + \
                              door_wall.normal.p2 * js
                else:
                    p_m_mid = Point2D(int(op_door_wall.seg.midpoint.x), int(op_door_wall.seg.midpoint.y)) \
                              - near_door_wall.normal.p2 * (mk - wb_should) / 2
                p_m1 = p_m_mid + op_door_wall.dir.p2 * (wb_should / 2)
                p_m2 = p_m_mid - op_door_wall.dir.p2 * (wb_should / 2)
                p_m1, p_m2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_m1, p_m2)
                m_bl = DY_segment(p_m1, p_m2)
                wb = WashBasin(m_bl)
                self.ele_list.append(wb)
                # #放置坐便
                # 这儿有大问题，在1.5*1.5尺寸左右
                mid = Point2D(int(far_door_wall.seg.midpoint.x), int(far_door_wall.seg.midpoint.y)) \
                      - door_wall.normal.p2 * (SHOWER_L / 2)
                p_t1 = mid + far_door_wall.dir.p2 * (TOILET_DEV_W / 2)
                p_t2 = mid - far_door_wall.dir.p2 * (TOILET_DEV_W / 2)
                p_t1, p_t2 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal, p_t1, p_t2)
                t_bl = DY_segment(p_t1, p_t2)
                tt = ToiletDevice(t_bl)
                self.ele_list.append(tt)
                # # 放置淋浴房 可以是花洒或者淋浴房
                if mk <= wb_should + SHOWER_W:  # 判断面宽来决定淋浴房要什么样的
                    spray_flag = True
                    shower_flag = False
                    wash_flag1 = False
                    sr = Spray()
                    temp = 1
                else:
                    spray_flag = False
                    shower_flag = True
                    sr = ShowerRoom()
                    temp = 0
                if spray_flag:
                    shower_len = SPRAY_L
                    shower_wid = SPRAY_W
                if shower_flag:
                    shower_len = SHOWER_L
                    shower_wid = SHOWER_W
                # mid_s = op_door_wall.seg.midpoint + near_door_wall.normal.p2 * (wb_should / 2)
                if temp == 1:
                    p_s1 = op_door_wall.line.intersection(far_door_wall.seg)[0] + far_door_wall.normal.p2 * SPRAY_E
                    p_s2 = p_s1 + far_door_wall.normal.p2 * shower_wid
                    p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_s1, p_s2)
                    s_bl = DY_segment(p_s1, p_s2)
                    sr.set_pos(s_bl, shower_len)
                    self.ele_list.append(sr)
                else:
                    p_s1 = op_door_wall.line.intersection(far_door_wall.seg)[0]
                    p_s2_vec = get_vector_seg(p_s1, self.boundary)
                    p_s2 = p_s1 + p_s2_vec.dir.p2 * shower_wid
                    s_bl = DY_segment(p_s1, p_s2)
                    sr.set_pos(s_bl, shower_len)
                    self.ele_list.append(sr)
                # #放置洗衣机
                if wash_flag1:
                    p_wh1 = door_wall.line.intersection(near_door_wall.seg)[0]
                    p_wh2 = p_wh1 + door_wall.normal.p2 * WAHING_MAC_W
                    p_wh1, p_wh2 = DY_segment.get_p1_p2_from_normal(near_door_wall.normal, p_wh1, p_wh2)
                    wh_bl = DY_segment(p_wh1, p_wh2)
                    whmc = WashingMachine(wh_bl)
                    self.ele_list.append(whmc)

        else:  # 进深大于两米

            if T1X >= min(WASHBASIN_W):  # 面盆可以放在门墙上根据尺寸判断面盆两个宽度
                # 沿面宽方向放面盆
                wb_should = min(WASHBASIN_W)
                if T1X >= max(WASHBASIN_W):
                    wb_should = max(WASHBASIN_W)
                wb_mid = Point2D(int(door_wall.seg.midpoint.x), int(door_wall.seg.midpoint.y)) + \
                         near_door_wall.normal.p2 * int((door.backline.seg.length + T2X) / 2)
                p_m1 = wb_mid + door_wall.dir.p2 * int(wb_should / 2)
                p_m2 = wb_mid - door_wall.dir.p2 * int(wb_should / 2)
                p_m1, p_m2 = DY_segment.get_p1_p2_from_normal(door_wall.normal, p_m1, p_m2)
                m_bl = DY_segment(p_m1, p_m2)
                wb = WashBasin(m_bl)
                self.ele_list.append(wb)
                # 放坐便
                p_inter = door_wall.line.intersection(far_door_wall.seg)[0]
                p_t1 = p_inter + door_wall.normal.p2 * (DEVICE_FRONT + WASHBASIN_L)
                p_t2 = p_t1 + door_wall.normal.p2 * TOILET_DEV_W
                p_t1, p_t2 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal, p_t1, p_t2)
                t_bl = DY_segment(p_t1, p_t2)
                tt = ToiletDevice(t_bl)
                self.ele_list.append(tt)
                # 淋浴房亦可以选择花洒
                if js - WASHBASIN_L - DEVICE_FRONT - TOILET_DEV_W - TOILET_DIS_AROUND > SHOWER_L:
                    p_s1 = far_door_wall.line.intersection(op_door_wall.seg)[0]
                    p_s2_vec = get_vector_seg(p_s1, self.boundary)
                    p_s2 = p_s1 + p_s2_vec.dir.p2 * SHOWER_W
                    # p_s2 = p_s1 + far_door_wall.normal.p2 * SHOWER_W
                    # p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_s1, p_s2)
                    s_bl = DY_segment(p_s1, p_s2)
                    sr = ShowerRoom()
                    sr.set_pos(s_bl, SHOWER_L)
                    self.ele_list.append(sr)
                    wash_flag2 = True
                else:
                    rand = random.randint(0, 1)
                    sr, case = self.shower_case(rand)
                    if isinstance(sr, Spray):  # 成立意味着选择花洒？？？
                        p_s1 = far_door_wall.line.intersection(op_door_wall.seg)[0] + far_door_wall.normal.p2 * SPRAY_E
                        p_s2 = p_s1 + far_door_wall.normal.p2 * case[0]
                        p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_s1, p_s2)
                        s_bl = DY_segment(p_s1, p_s2)
                        sr.set_pos(s_bl, case[1])
                        self.ele_list.append(sr)
                        wash_flag2 = True
                    else:
                        p_s1 = near_door_wall.line.intersection(op_door_wall.seg)[0]
                        p_s2_vec = get_vector_seg(p_s1, self.boundary)
                        p_s2 = p_s1 + p_s2_vec.dir.p2 * case[0]
                        # p_s2 = p_s1 + near_door_wall.normal.p2 * case[0]
                        # p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_s1, p_s2)
                        s_bl = DY_segment(p_s1, p_s2)
                        sr.set_pos(s_bl, case[1])
                        self.ele_list.append(sr)
                        wash_flag3 = True
                # 放洗衣机
                if wash_flag2:
                    mid_wh = Point2D(int(op_door_wall.seg.midpoint.x), int(op_door_wall.seg.midpoint.y)) + \
                             far_door_wall.normal.p2 * int(SHOWER_L / 2)
                    p_wh1 = mid_wh + op_door_wall.dir.p2 * int(WAHING_MAC_W / 2)
                    p_wh2 = mid_wh - op_door_wall.dir.p2 * int(WAHING_MAC_W / 2)
                    p_wh1, p_wh2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_wh1, p_wh2)
                    wh_layout_flag = True
                if wash_flag3:
                    if js > half_door_bl * 2 + SHOWER_L + WAHING_MAC_W:
                        mid_wh = Point2D(int(near_door_wall.seg.midpoint.x), int(near_door_wall.seg.midpoint.y)) \
                                 - door_wall.normal.p2 * int(SHOWER_L / 2) + door_wall.normal.p2 * int(half_door_bl)
                        p_wh1 = mid_wh + near_door_wall.dir.p2 * int(WAHING_MAC_W / 2)
                        p_wh2 = mid_wh - near_door_wall.dir.p2 * int(WAHING_MAC_W / 2)
                        p_wh1, p_wh2 = DY_segment.get_p1_p2_from_normal(near_door_wall.normal, p_wh1, p_wh2)
                        wh_layout_flag = True
                    elif mk > WAHING_MAC_L + DEVICE_FRONT + SHOWER_W:
                        p_wh1 = far_door_wall.line.intersection(op_door_wall.seg)[0]
                        p_wh2 = p_wh1 + op_door_wall.normal.p2 * WAHING_MAC_L
                        p_wh1, p_wh2 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal, p_wh1, p_wh2)
                        wh_layout_flag = True
                if wh_layout_flag:
                    wh_bl = DY_segment(p_wh1, p_wh2)
                    whmc = WashingMachine(wh_bl)
                    self.ele_list.append(whmc)

            else:
                # 沿进深方向放面盆,坐便,淋浴房
                if T1X >= WASHBASIN_L:  # 面盆转放到邻墙上，但可以贴在拐角处放置
                    p_m1 = door_wall.line.intersection(far_door_wall.seg)[0]
                    p_m2 = p_m1 + door_wall.normal.p2 * max(WASHBASIN_W)
                    # 放坐便 放在和面盆同墙上,再判断是否能放下淋浴房
                    p_t1 = door_wall.line.intersection(far_door_wall.seg)[0] + door_wall.normal.p2 * \
                                                                               (max(WASHBASIN_W) + TOILET_DIS_AROUND)
                    p_t2 = p_t1 + door_wall.normal.p2 * TOILET_DEV_W
                    p_t1, p_t2 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal, p_t1, p_t2)
                    t_bl = DY_segment(p_t1, p_t2)
                    tt = ToiletDevice(t_bl)
                    self.ele_list.append(tt)
                    if js > max(WASHBASIN_W) + TOILET_DIS_AROUND + TOILET_DEV_W + SHOWER_L:  # 直接放淋浴房在面盆的直线延长区域
                        sr, case = self.shower_case(0)
                        p_s1 = far_door_wall.line.intersection(op_door_wall.seg)[0]
                        p_s2_vec = get_vector_seg(p_s1, self.boundary)
                        p_s2 = p_s1 + p_s2_vec.dir.p2 * case[0]
                        # p_s2 = p_s1 + far_door_wall.normal.p2 * case[0]
                        # p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_s1, p_s2)
                        s_bl = DY_segment(p_s1, p_s2)
                        sr.set_pos(s_bl, case[1])
                        self.ele_list.append(sr)
                        mk_flag = True
                        sp_flag = False
                        # if mk > SHOWER_W + WAHING_MAC_W:
                        #     wash_flag2 = True
                        #     wash_flag3 = True
                        # else:
                        #     wash_flag3 = False
                        #     wash_flag2 = False


                    else:  # 进深尺寸不够，随机决定放花洒还是淋浴房，花洒会放在面盆的直线区域，淋浴房则会移到另对面拐角处
                        rand = random.randint(0, 1)
                        sr, case = self.shower_case(rand)
                        mk_flag = False
                        if rand == 1:
                            sp_flag = True
                            mid_sp = Point2D(int(op_door_wall.seg.midpoint.x), int(op_door_wall.seg.midpoint.y))
                            p_s1 = mid_sp + op_door_wall.dir.p2 * int(case[0] / 2)
                            p_s2 = mid_sp - op_door_wall.dir.p2 * int(case[0] / 2)
                            p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_s1, p_s2)
                            s_bl = DY_segment(p_s1, p_s2)
                            sr.set_pos(s_bl, case[1])
                            self.ele_list.append(sr)
                        else:
                            sp_flag = False
                            p_s1 = near_door_wall.line.intersection(op_door_wall.seg)[0]
                            p_s2_vec = get_vector_seg(p_s1, self.boundary)
                            p_s2 = p_s1 + p_s2_vec.dir.p2 * case[0]
                            # p_s2 = p_s1 + near_door_wall.normal.p2 * case[0]
                            # p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_s1, p_s2)
                            s_bl = DY_segment(p_s1, p_s2)
                            sr.set_pos(s_bl, case[1])
                            self.ele_list.append(sr)


                            # if rand == 1 and mk > TOILET_DEV_L + DEVICE_FRONT + WAHING_MAC_L:
                            #     wash_flag3 = True
                            #     wash_flag2 = False
                            # else:
                            #     wash_flag2 = False
                            #     wash_flag3 = False

                    # 根据面宽尺寸放置洗衣机，如果尺寸够，可以放在面盆对面也可以放在门对面，否则不放洗衣机
                    if mk > SHOWER_W + WAHING_MAC_W and mk_flag:
                        wash_flag2 = True
                    if mk > TOILET_DEV_L + DEVICE_FRONT + WAHING_MAC_L and sp_flag:
                        wash_flag3 = True
                    else:
                        wash_flag2 = False
                        wash_flag3 = False

                else:  # 不能在拐角处放置，面盆需要躲开门的延长线放置
                    p_m1 = door_wall.line.intersection(far_door_wall.seg)[0] + door_wall.normal.p2 * (half_door_bl * 2)
                    p_m2 = p_m1 + door_wall.normal.p2 * max(WASHBASIN_W)
                    # 放坐便，计算是否能放在同一墙上
                    if js - half_door_bl * 2 - max(WASHBASIN_W) - TOILET_DIS_AROUND > TOILET_DEV_W:  # 可以放在和面盆同墙上
                        # 进深还可以再大，是否考虑继续往进深方向放呢？应该放在对面？暂时先按后者考虑
                        mid_t = Point2D(int(far_door_wall.seg.midpoint.x), int(far_door_wall.seg.midpoint.y)) + \
                                door_wall.normal.p2 * int((half_door_bl * 2 + max(WASHBASIN_W) + TOILET_DIS_AROUND) / 2)
                        p_t1 = mid_t + far_door_wall.dir.p2 * int(TOILET_DEV_W / 2)
                        p_t2 = mid_t - far_door_wall.dir.p2 * int(TOILET_DEV_W / 2)
                        p_t1, p_t2 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal, p_t1, p_t2)
                        t_bl = DY_segment(p_t1, p_t2)
                        tt = ToiletDevice(t_bl)
                        self.ele_list.append(tt)
                        if mk < TOILET_DEV_L + SHOWER_W + DEVICE_FRONT:
                            flag = 1
                            wash_flag2 = False
                            wash_flag3 = False
                            sr, case = self.shower_case(flag)
                            p_s1 = near_door_wall.line.intersection(op_door_wall.seg)[0] + \
                                   op_door_wall.normal.p2 * SPRAY_E
                            p_s2 = p_s1 + near_door_wall.normal.p2 * case[0]
                            p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_s1, p_s2)
                            s_bl = DY_segment(p_s1, p_s2)
                            sr.set_pos(s_bl, case[1])
                            self.ele_list.append(sr)
                        else:
                            flag = 0
                            wash_flag2 = False
                            wash_flag3 = True
                            sr, case = self.shower_case(flag)
                            p_s1 = near_door_wall.line.intersection(op_door_wall.seg)[0]
                            p_s2_vec = get_vector_seg(p_s1, self.boundary)
                            p_s2 = p_s1 + p_s2_vec.dir.p2 * case[0]
                            # p_s2 = p_s1 + near_door_wall.normal.p2 * case[0]
                            # p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_s1, p_s2)
                            s_bl = DY_segment(p_s1, p_s2)
                            sr.set_pos(s_bl, case[1])
                            self.ele_list.append(sr)
                    else:  # 放在对面墙上（near_door_wall）或门对面，此时应该只能放花洒
                        if mk > WASHBASIN_L + DEVICE_FRONT + TOILET_DEV_L:
                            rand = random.randint(0, 1)
                            flag = 1
                            if rand == 1:
                                mid_t = Point2D(int(near_door_wall.seg.midpoint.x),
                                                int(near_door_wall.seg.midpoint.y)) \
                                        + door_wall.normal.p2 * half_door_bl * DIS_DOOR_R
                                p_t1 = mid_t + near_door_wall.dir.p2 * int(TOILET_DEV_W / 2)
                                p_t2 = mid_t - near_door_wall.dir.p2 * int(TOILET_DEV_W / 2)
                                p_t1, p_t2 = DY_segment.get_p1_p2_from_normal(near_door_wall.normal, p_t1, p_t2)
                                t_bl = DY_segment(p_t1, p_t2)
                                tt = ToiletDevice(t_bl)
                                self.ele_list.append(tt)
                                sr, case = self.shower_case(flag)
                                p_s1 = op_door_wall.line.intersection(near_door_wall.seg)[
                                           0] + near_door_wall.normal.p2 * SPRAY_E
                                p_s2 = p_s1 + op_door_wall.normal.p2 * case[0]
                                p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(near_door_wall.normal, p_s1, p_s2)
                                s_bl = DY_segment(p_s1, p_s2)
                                sr.set_pos(s_bl, case[1])
                                self.ele_list.append(sr)
                            else:
                                mid_t = Point2D(int(op_door_wall.seg.midpoint.x),
                                                int(op_door_wall.seg.midpoint.y)) \
                                        + far_door_wall.normal.p2 * int(WASHBASIN_L / 2)
                                p_t1 = mid_t + op_door_wall.dir.p2 * int(TOILET_DEV_W / 2)
                                p_t2 = mid_t - op_door_wall.dir.p2 * int(TOILET_DEV_W / 2)
                                p_t1, p_t2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_t1, p_t2)
                                t_bl = DY_segment(p_t1, p_t2)
                                tt = ToiletDevice(t_bl)
                                self.ele_list.append(tt)
                                sr, case = self.shower_case(flag)
                                # mid_s = near_door_wall.seg.midpoint + door_wall.normal.p2 * half_door_bl * DIS_DOOR_R
                                mid_s = Point2D(int(near_door_wall.seg.midpoint.x), int(near_door_wall.seg.midpoint.y))
                                p_s1 = mid_s + near_door_wall.dir.p2 * int(SPRAY_W / 2)
                                p_s2 = mid_s - near_door_wall.dir.p2 * int(SPRAY_W / 2)
                                p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(near_door_wall.normal, p_s1, p_s2)
                                s_bl = DY_segment(p_s1, p_s2)
                                sr.set_pos(s_bl, case[1])
                                self.ele_list.append(sr)
                            wash_flag2 = False
                            wash_flag3 = False
                        else:
                            pass

                p_m1, p_m2 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal, p_m1, p_m2)
                m_bl = DY_segment(p_m1, p_m2)
                wb = WashBasin(m_bl)
                self.ele_list.append(wb)
                # 放置洗衣机
                case_wh = self.wash_machine_flag_select(wash_flag2, wash_flag3)
                if case_wh == 2 or case_wh == 1:
                    mid_wh = Point2D(int(op_door_wall.seg.midpoint.x), int(op_door_wall.seg.midpoint.y)) \
                             + far_door_wall.normal.p2 * int(SHOWER_L / 2)
                    p_wh1 = mid_wh + op_door_wall.dir.p2 * int(WAHING_MAC_W / 2)
                    p_wh2 = mid_wh - op_door_wall.dir.p2 * int(WAHING_MAC_W / 2)
                    p_wh1, p_wh2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_wh1, p_wh2)
                    wh_layout_flag = True
                elif case_wh == 0:
                    mid_wh = Point2D(int(t_bl.seg.midpoint.x), int(t_bl.seg.midpoint.y)) \
                             + far_door_wall.normal.p2 * mk
                    p_wh1 = mid_wh + near_door_wall.dir.p2 * int(WAHING_MAC_W / 2)
                    p_wh2 = mid_wh - near_door_wall.dir.p2 * int(WAHING_MAC_W / 2)
                    p_wh1, p_wh2 = DY_segment.get_p1_p2_from_normal(near_door_wall.normal, p_wh1, p_wh2)
                    wh_layout_flag = True
                if wh_layout_flag:
                    wh_bl = DY_segment(p_wh1, p_wh2)
                    whmc = WashingMachine(wh_bl)
                    self.ele_list.append(whmc)
        # if self.boundary and self.virtual_boundary:
        #     self.vir_door_list[0], self.door_list[0] = \
        #         self.exchange_vir_door(self.vir_door_list[0], self.door_list[0])
        #     self.virtual_boundary, self.boundary = \
        #         self.exchange_vir_boundary(self.virtual_boundary, self.boundary)

    def run411(self):
        js = 0
        mk = 0
        t_bl = None
        for e in self.ele_list:
            if isinstance(e, CommonElement.Door):
                door = e
                # if self.vir_door_list:
                #     door = self.vir_door_list[0]
        for s in self.boundary.seg_list:
            if s.seg.is_parallel(door.backline.seg) and \
                    door.boundary.polygon.intersection(s.seg):
                door_wall = s
                # if s.seg.contains(door.backline.seg):
                #     door_wall = s
        # 初始化确定各个墙并得到进深和面宽尺寸
        mk = door_wall.seg.length
        op_door_wall = get_opposite_bounds(door_wall, self.boundary)[0]
        js_walls = get_adjacent_bounds(door_wall, self.boundary)
        js = js_walls[0].seg.length
        wash_flag1 = False
        wash_flag2 = False
        wash_flag3 = False
        wh_layout_flag = False
        # wall_doorbody_dis1 = js_walls[0].line.distance(door.door_body.seg.midpoint)
        # wall_doorbody_dis2 = js_walls[1].line.distance(door.door_body.seg.midpoint)
        # if wall_doorbody_dis1 < wall_doorbody_dis2:
        #     far_wall = js_walls[1]
        #     near_wall = js_walls[0]
        # else:
        #     far_wall = js_walls[0]
        #     near_wall = js_walls[1]
        # 初始化确定各个墙并得到进深和面宽尺寸end
        # #确定洗衣机摆放方式
        # if mk < MID_W11:
        #     wash_flag1 = False
        # else:
        #     wash_flag1 = True
        # wash_flag2 = False

        # if js > max(WASHBASIN_W) + TOILET_DEV_W:
        #     wb_ind = random.randint(0,len(WASHBASIN_W)-1)
        #     wb_should = WASHBASIN_W[wb_ind]
        # else:
        #     wb_should = WASHBASIN_W[0]
        # 判断门两边的墙的长度 X1 和 X2并修改门的body位置
        half_door_bl = door.backline.seg.length / 2
        X1 = js_walls[0].line.distance(door.backline.seg.midpoint)
        X2 = js_walls[1].line.distance(door.backline.seg.midpoint)
        X1 = X1 - half_door_bl
        X2 = X2 - half_door_bl
        door_body = [seg for seg in door.boundary.seg_list \
                     if seg.seg.is_perpendicular(door.backline.seg)]
        if js_walls[0].line.distance(door_body[0].seg.midpoint) == X1:
            door_body_near0 = door_body[0]
        if js_walls[0].line.distance(door_body[1].seg.midpoint) == X1:
            door_body_near0 = door_body[1]
        if js_walls[1].line.distance(door_body[0].seg.midpoint) == X2:
            door_body_near1 = door_body[0]
        if js_walls[1].line.distance(door_body[1].seg.midpoint) == X2:
            door_body_near1 = door_body[1]
        if X1 >= X2:  # 这部分完成了门的放置，并且明确的给出两个与门墙相邻的墙的名字近墙和远墙
            door.set_body(door_body_near1)
            near_door_wall = js_walls[1]
            far_door_wall = js_walls[0]

        else:
            door.set_body(door_body_near0)
            near_door_wall = js_walls[0]
            far_door_wall = js_walls[1]
        T2X = min(near_door_wall.line.distance(door.backline.p1),
                  near_door_wall.line.distance(door.backline.p2))
        T1X = min(far_door_wall.line.distance(door.backline.p1),
                  far_door_wall.line.distance(door.backline.p2))

        if T2X >= DOOR_BODY_TO_WALL:
            wb_should = WASHBASIN_W[1]
            if T2X > WAHING_MAC_L:
                wash_flag1 = True  # 设置洗衣机摆放标志位
                wash_flag2 = False
        else:
            wb_should = WASHBASIN_W[0]
            wash_flag1 = False
        # 理想状态：在开门正面开始放置组件:面盆->坐便->淋浴房->洗衣机（需要根据尺寸判断）
        win_list = []  # 寻找窗户和窗户所在的墙
        for line in self.line_list:
            if isinstance(line, DY_Line.Window):
                win_list.append(line)
            win_list = sorted(win_list, key=lambda w: w.seg.length, reverse=True)
        self.main_win_wall = win_list[0].wall
        dis = door_wall.line.distance(win_list[0].seg.midpoint)
        win_len = win_list[0].seg.length
        dis = dis - win_len / 2
        win_wall = win_list[0]
        # if self.main_win_wall.line.is_parallel(door_wall.line) or \
        #       near_door_wall.line.distance(win_list[0].seg.midpoint) == 0 or \
        #         dis >= 1000 :  # 要进行比较.is_parallel(self.main_win_wall, door_wall)

        if js >= JS_T1 and js <= JS_T2:  # 面盆需要首选放在门的正对面（进深在[1.3-2.0m]）
            if js <= 1500:  # 超小户型
                p_t1 = op_door_wall.seg.intersection(far_door_wall.seg)[0] + op_door_wall.normal.p2 * TOILET_AREA
                p_t2 = p_t1 + op_door_wall.normal.p2 * TOILET_DEV_W
                dir = far_door_wall.normal
                self.tt_put(p_t1, p_t2, dir)
                p_s1 = op_door_wall.seg.intersection(near_door_wall.seg)[0] + op_door_wall.normal.p2 * SPRAY_E
                p_s2 = p_s1 + op_door_wall.normal.p2 * int(SPRAY_W)
                dir = near_door_wall.normal
                self.sr_put(p_s1, p_s2, dir)
                if T1X > wb_should and door_wall.line.distance(win_wall.seg.midpoint) > 50:
                    p_m1 = door_wall.seg.intersection(far_door_wall.seg)[0]
                    p_m2 = p_m1 + far_door_wall.normal.p2 * wb_should
                    dir = door_wall.normal
                    self.wb_put(p_m1, p_m2, dir)
                elif T1X > WASHBASIN_L and js > (TOILET_DEV_W + TOILET_AREA + wb_should):
                    if far_door_wall.line.distance(win_wall.seg.midpoint) > 50 or \
                                            door_wall.line.distance(win_wall.seg.midpoint) - win_len / 2 > wb_should:
                        p_m1 = door_wall.seg.intersection(far_door_wall.seg)[0]
                        p_m2 = p_m1 + door_wall.normal.p2 * wb_should
                        dir = far_door_wall.normal
                        self.wb_put(p_m1, p_m2, dir)
            else:
                wb_should = min(WASHBASIN_W)
                if op_door_wall.line.distance(win_wall.seg.midpoint) >= 50:  # 窗户不在对面墙上，面盆可以放对面墙
                    p_m1 = op_door_wall.line.intersection(near_door_wall.seg)[0]
                    p_m2 = p_m1 + near_door_wall.normal.p2 * wb_should
                    dir = op_door_wall.normal
                    self.wb_put(p_m1, p_m2, dir)
                    if mk > TOILET_DEV_L + wb_should + TOILET_AREA:  # mk够大，马桶放上面一点
                        p_t1 = op_door_wall.line.intersection(far_door_wall.seg)[
                                   0] + op_door_wall.normal.p2 * TOILET_AREA
                        p_t2 = p_t1 + op_door_wall.normal.p2 * TOILET_DEV_W
                        dir = far_door_wall.normal
                        self.tt_put(p_t1, p_t2, dir)
                        # 小户型直接放花洒
                        p_s1 = door_wall.line.intersection(far_door_wall.seg)[0] + door_wall.normal.p2 * SPRAY_E
                        p_s2 = p_s1 + door_wall.normal.p2 * SPRAY_W
                        dir = far_door_wall.normal
                        self.sr_put(p_s1, p_s2, dir)
                    else:  # 面宽不够，马桶得再中下,花洒只能下
                        # 考虑剩余空间
                        if mk - wb_should - TOILET_DEV_W > TOILET_AREA:
                            p_t1 = op_door_wall.line.intersection(far_door_wall.seg)[0] + far_door_wall.normal.p2 * (
                            TOILET_AREA / 2)
                            p_t2 = p_t1 + far_door_wall.normal.p2 * TOILET_DEV_W
                            dir = op_door_wall.normal
                            self.tt_put(p_t1, p_t2, dir)
                        else:
                            mid = far_door_wall.seg.midpoint
                            p_t1 = mid + door_wall.normal.p2 * (TOILET_DEV_W / 2)
                            p_t2 = mid - door_wall.normal.p2 * (TOILET_DEV_W / 2)
                            dir = far_door_wall.normal
                            self.tt_put(p_t1, p_t2, dir)
                        p_s1 = door_wall.line.intersection(far_door_wall.seg)[0] + door_wall.normal.p2 * SPRAY_E
                        p_s2 = p_s1 + door_wall.normal.p2 * int(SPRAY_W)
                        dir = far_door_wall.normal
                        self.sr_put(p_s1, p_s2, dir)
                else:  # 窗户在对墙，需要考虑新布局

                    if T1X > wb_should:  # 远墙距离够
                        p_m1 = door_wall.line.intersection(far_door_wall.seg)[0]
                        p_m2 = p_m1 + far_door_wall.normal.p2 * wb_should
                        dir = door_wall.normal
                        self.wb_put(p_m1, p_m2, dir)
                        p_t1 = op_door_wall.seg.intersection(near_door_wall.seg)[
                                   0] + near_door_wall.normal.p2 * TOILET_AREA
                        p_t2 = p_t1 + near_door_wall.normal.p2 * int(TOILET_DEV_W)
                        dir = op_door_wall.normal
                        self.tt_put(p_t1, p_t2, dir)
                        p_s1 = op_door_wall.seg.intersection(far_door_wall.seg)[0] + op_door_wall.normal.p2 * SPRAY_E
                        p_s2 = p_s1 + op_door_wall.normal.p2 * int(SPRAY_W)
                        dir = far_door_wall.normal
                        self.sr_put(p_s1, p_s2, dir)

                    elif T1X > WASHBASIN_L:
                        p_m1 = door_wall.line.intersection(far_door_wall.seg)[0]
                        p_m2 = p_m1 + door_wall.normal.p2 * wb_should
                        dir = far_door_wall.normal
                        self.wb_put(p_m1, p_m2, dir)
                        p_t1 = op_door_wall.seg.intersection(near_door_wall.seg)[
                                   0] + near_door_wall.normal.p2 * TOILET_AREA
                        p_t2 = p_t1 + near_door_wall.normal.p2 * int(TOILET_DEV_W)
                        dir = op_door_wall.normal
                        self.tt_put(p_t1, p_t2, dir)
                        p_s1 = op_door_wall.seg.intersection(far_door_wall.seg)[0] + far_door_wall.normal.p2 * SPRAY_E
                        p_s2 = p_s1 + far_door_wall.normal.p2 * int(SPRAY_W)
                        dir = op_door_wall.normal
                        self.sr_put(p_s1, p_s2, dir)
                    else:
                        p_m1 = op_door_wall.line.intersection(far_door_wall.seg)[0]
                        p_m2 = p_m1 + op_door_wall.normal.p2 * wb_should
                        dir = far_door_wall.normal
                        self.wb_put(p_m1, p_m2, dir)
                        p_t1 = near_door_wall.seg.midpoint + door_wall.normal.p2 * (TOILET_AREA / 2)
                        p_t2 = p_t1 + door_wall.normal.p2 * int(TOILET_DEV_W)
                        dir = near_door_wall.normal
                        self.tt_put(p_t1, p_t2, dir)
                        p_s1 = door_wall.seg.intersection(far_door_wall.seg)[0] + door_wall.normal.p2 * SPRAY_E
                        p_s2 = p_s1 + door_wall.normal.p2 * int(SPRAY_W)
                        dir = far_door_wall.normal
                        self.sr_put(p_s1, p_s2, dir)


        else:  # 进深大于两米
            wb_should = max(WASHBASIN_W)  # 大户型放大面盆
            if T1X >= wb_should and door_wall.line.distance(win_list[0].seg.midpoint) != 0:  # 面盆可以放在门墙上根据尺寸判断面盆两个宽度
                # 沿面宽方向放面盆,且窗户不在面宽的这条边上


                p_m1 = door_wall.line.intersection(far_door_wall.seg)[0]
                p_m2 = p_m1 + far_door_wall.normal.p2 * wb_should
                p_m1, p_m2 = DY_segment.get_p1_p2_from_normal(door_wall.normal, p_m1, p_m2)
                m_bl = DY_segment(p_m1, p_m2)
                wb = WashBasin(m_bl)
                self.ele_list.append(wb)
                # 放坐便
                p_inter = door_wall.line.intersection(far_door_wall.seg)[0]
                p_t1 = p_inter + door_wall.normal.p2 * (DEVICE_FRONT + WASHBASIN_L)
                p_t2 = p_t1 + door_wall.normal.p2 * TOILET_DEV_W
                p_t1, p_t2 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal, p_t1, p_t2)
                t_bl = DY_segment(p_t1, p_t2)
                tt = ToiletDevice(t_bl)
                self.ele_list.append(tt)
                # 淋浴房亦可以选择花洒
                if js - WASHBASIN_L - DEVICE_FRONT - TOILET_DEV_W - TOILET_DIS_AROUND > SHOWER_L:
                    p_s1 = far_door_wall.line.intersection(op_door_wall.seg)[0]
                    p_s2_vec = get_vector_seg(p_s1, self.boundary)
                    p_s2 = p_s1 + p_s2_vec.dir.p2 * SHOWER_W
                    # p_s2 = p_s1 + far_door_wall.normal.p2 * SHOWER_W
                    # p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_s1, p_s2)
                    s_bl = DY_segment(p_s1, p_s2)
                    sr = ShowerRoom()
                    sr.set_pos(s_bl, SHOWER_L)
                    self.ele_list.append(sr)
                    wash_flag2 = True
                else:
                    rand = random.randint(0, 1)
                    sr, case = self.shower_case(rand)
                    if isinstance(sr, Spray):
                        p_s1 = far_door_wall.line.intersection(op_door_wall.seg)[0] + far_door_wall.normal.p2 * SPRAY_E
                        # p_s1 = far_door_wall.line.intersection(op_door_wall.seg)[0]
                        p_s2 = p_s1 + far_door_wall.normal.p2 * case[0]
                        p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_s1, p_s2)
                        s_bl = DY_segment(p_s1, p_s2)
                        sr.set_pos(s_bl, case[1])
                        self.ele_list.append(sr)
                        wash_flag2 = True
                    else:
                        p_s1 = near_door_wall.line.intersection(op_door_wall.seg)[0]
                        p_s2_vec = get_vector_seg(p_s1, self.boundary)
                        p_s2 = p_s1 + p_s2_vec.dir.p2 * case[0]
                        # p_s2 = p_s1 + near_door_wall.normal.p2 * case[0]
                        # p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_s1, p_s2)
                        s_bl = DY_segment(p_s1, p_s2)
                        sr.set_pos(s_bl, case[1])
                        self.ele_list.append(sr)
                        wash_flag3 = True
                # 放洗衣机
                if wash_flag2:
                    mid_wh = Point2D(int(op_door_wall.seg.midpoint.x), int(op_door_wall.seg.midpoint.y)) + \
                             far_door_wall.normal.p2 * int(SHOWER_L / 2)
                    p_wh1 = mid_wh + op_door_wall.dir.p2 * int(WAHING_MAC_W / 2)
                    p_wh2 = mid_wh - op_door_wall.dir.p2 * int(WAHING_MAC_W / 2)
                    p_wh1, p_wh2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_wh1, p_wh2)
                    wh_layout_flag = True
                if wash_flag3:
                    if js > half_door_bl * 2 + SHOWER_L + WAHING_MAC_W:
                        mid_wh = Point2D(int(near_door_wall.seg.midpoint.x), int(near_door_wall.seg.midpoint.y)) \
                                 - door_wall.normal.p2 * int(SHOWER_L / 2) + door_wall.normal.p2 * int(half_door_bl)
                        p_wh1 = mid_wh + near_door_wall.dir.p2 * int(WAHING_MAC_W / 2)
                        p_wh2 = mid_wh - near_door_wall.dir.p2 * int(WAHING_MAC_W / 2)
                        p_wh1, p_wh2 = DY_segment.get_p1_p2_from_normal(near_door_wall.normal, p_wh1, p_wh2)
                        wh_layout_flag = True
                    elif mk > WAHING_MAC_L + DEVICE_FRONT + SHOWER_W:
                        p_wh1 = far_door_wall.line.intersection(op_door_wall.seg)[0]
                        p_wh2 = p_wh1 + op_door_wall.normal.p2 * WAHING_MAC_L
                        p_wh1, p_wh2 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal, p_wh1, p_wh2)
                        wh_layout_flag = True
                if wh_layout_flag:
                    wh_bl = DY_segment(p_wh1, p_wh2)
                    whmc = WashingMachine(wh_bl)
                    self.ele_list.append(whmc)

            elif T1X >= min(WASHBASIN_W) and door_wall.line.distance(win_list[0].seg.midpoint) == 0:
                # 门墙边有窗，竖着放东西

                p_m1 = far_door_wall.seg.intersection(door_wall.seg)[0]
                p_m2 = p_m1 + door_wall.normal.p2 * wb_should
                p_m1, p_m2 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal, p_m1, p_m2)
                m_bl = DY_segment(p_m1, p_m2)
                wb = WashBasin(m_bl)
                self.ele_list.append(wb)

                p_t1 = far_door_wall.seg.intersection(op_door_wall.seg)[0] - door_wall.normal.p2 * TOILET_AREA
                p_t2 = p_t1 - door_wall.normal.p2 * TOILET_DEV_W
                p_t1, p_t2 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal, p_t1, p_t2)
                t_bl = DY_segment(p_t1, p_t2)
                tt = ToiletDevice(t_bl)
                self.ele_list.append(tt)
                sr = Spray()
                p_s1 = near_door_wall.seg.intersection(op_door_wall.seg)[0] + op_door_wall.normal.p2 * SPRAY_E
                p_s2 = p_s1 + op_door_wall.normal.p2 * int(SPRAY_W)
                p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(near_door_wall.normal, p_s1, p_s2)
                s_bl = DY_segment(p_s1, p_s2)
                sr.set_pos(s_bl, SPRAY_L)
                self.ele_list.append(sr)
            else:
                # 沿进深方向放面盆,坐便,淋浴房
                if T1X >= WASHBASIN_L:
                    if ((door_wall.line.distance(win_list[0].seg.midpoint) - win_len / 2) >= wb_should or \
                                    near_door_wall.line.distance(win_list[0].seg.midpoint) == 0):
                        p_m1 = door_wall.line.intersection(far_door_wall.seg)[0]
                        p_m2 = p_m1 + door_wall.normal.p2 * wb_should
                        p_m1, p_m2 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal, p_m1, p_m2)
                        m_bl = DY_segment(p_m1, p_m2)
                        wb = WashBasin(m_bl)
                        self.ele_list.append(wb)
                        # 放坐便 放在和面盆同墙上,再判断是否能放下淋浴房
                        p_t1 = door_wall.line.intersection(far_door_wall.seg)[0] + door_wall.normal.p2 * \
                                                                                   (
                                                                                   max(WASHBASIN_W) + TOILET_DIS_AROUND)
                        p_t2 = p_t1 + door_wall.normal.p2 * TOILET_DEV_W
                        p_t1, p_t2 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal, p_t1, p_t2)
                        t_bl = DY_segment(p_t1, p_t2)
                        tt = ToiletDevice(t_bl)
                        self.ele_list.append(tt)
                        if js > max(WASHBASIN_W) + TOILET_DIS_AROUND + TOILET_DEV_W + SHOWER_L:  # 直接放淋浴房在面盆的直线延长区域
                            sr, case = self.shower_case(0)
                            p_s1 = far_door_wall.line.intersection(op_door_wall.seg)[0]
                            p_s2_vec = get_vector_seg(p_s1, self.boundary)
                            p_s2 = p_s1 + p_s2_vec.dir.p2 * case[0]
                            # p_s2 = p_s1 + far_door_wall.normal.p2 * case[0]
                            # p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_s1, p_s2)
                            s_bl = DY_segment(p_s1, p_s2)
                            sr.set_pos(s_bl, case[1])
                            self.ele_list.append(sr)
                            mk_flag = True
                            sp_flag = False
                            # if mk > SHOWER_W + WAHING_MAC_W:
                            #     wash_flag2 = True
                            #     wash_flag3 = True
                            # else:
                            #     wash_flag3 = False
                            #     wash_flag2 = False


                        else:  # 进深尺寸不够，随机决定放花洒还是淋浴房，花洒会放在面盆的直线区域，淋浴房则会移到另对面拐角处
                            rand = random.randint(0, 1)
                            sr, case = self.shower_case(rand)
                            mk_flag = False
                            if rand == 1:
                                sp_flag = True
                                mid_sp = Point2D(int(op_door_wall.seg.midpoint.x), int(op_door_wall.seg.midpoint.y))
                                p_s1 = mid_sp + op_door_wall.dir.p2 * int(case[0] / 2)
                                p_s2 = mid_sp - op_door_wall.dir.p2 * int(case[0] / 2)
                                p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_s1, p_s2)
                                s_bl = DY_segment(p_s1, p_s2)
                                sr.set_pos(s_bl, case[1])
                                self.ele_list.append(sr)
                            else:
                                sp_flag = False
                                p_s1 = near_door_wall.line.intersection(op_door_wall.seg)[0]
                                p_s2_vec = get_vector_seg(p_s1, self.boundary)
                                p_s2 = p_s1 + p_s2_vec.dir.p2 * case[0]
                                # p_s2 = p_s1 + near_door_wall.normal.p2 * case[0]
                                # p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_s1, p_s2)
                                s_bl = DY_segment(p_s1, p_s2)
                                sr.set_pos(s_bl, case[1])
                                self.ele_list.append(sr)


                                # if rand == 1 and mk > TOILET_DEV_L + DEVICE_FRONT + WAHING_MAC_L:
                                #     wash_flag3 = True
                                #     wash_flag2 = False
                                # else:
                                #     wash_flag2 = False
                                #     wash_flag3 = False

                        # 根据面宽尺寸放置洗衣机，如果尺寸够，可以放在面盆对面也可以放在门对面，否则不放洗衣机
                        if mk > SHOWER_W + WAHING_MAC_W and mk_flag:
                            wash_flag2 = True
                        if mk > TOILET_DEV_L + DEVICE_FRONT + WAHING_MAC_L and sp_flag:
                            wash_flag3 = True
                        else:
                            wash_flag2 = False
                            wash_flag3 = False
                    else:  # 对中面盆远中马桶近中花洒
                        p_m1 = op_door_wall.seg.midpoint - far_door_wall.normal.p2 * (wb_should / 2)
                        p_m2 = op_door_wall.seg.midpoint + far_door_wall.normal.p2 * (wb_should / 2)
                        p_m1, p_m2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_m1, p_m2)
                        m_bl = DY_segment(p_m1, p_m2)
                        wb = WashBasin(m_bl)
                        self.ele_list.append(wb)
                        mid = far_door_wall.seg.midpoint
                        p_t1 = mid + far_door_wall.dir.p2 * (TOILET_DEV_W / 2)
                        p_t2 = mid - far_door_wall.dir.p2 * (TOILET_DEV_W / 2)
                        p_t1, p_t2 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal, p_t1, p_t2)
                        t_bl = DY_segment(p_t1, p_t2)
                        tt = ToiletDevice(t_bl)
                        self.ele_list.append(tt)
                        sr = Spray()
                        p_s1 = near_door_wall.seg.midpoint
                        p_s2 = p_s1 + near_door_wall.dir.p2 * int(SPRAY_W)
                        p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(near_door_wall.normal, p_s1, p_s2)
                        s_bl = DY_segment(p_s1, p_s2)
                        sr.set_pos(s_bl, SPRAY_L)
                        self.ele_list.append(sr)
                # 面宽不行
                # 窗位置再来说
                else:
                    if near_door_wall.line.distance(win_list[0].seg.midpoint) == 0:
                        # 面盆放对墙
                        p_m1 = near_door_wall.seg.intersection(op_door_wall.seg)[0]
                        p_m2 = p_m1 + near_door_wall.normal.p2 * wb_should
                        p_m1, p_m2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_m1, p_m2)
                        m_bl = DY_segment(p_m1, p_m2)
                        wb = WashBasin(m_bl)
                        self.ele_list.append(wb)
                    else:
                        # 同一放近墙，简单
                        p_m1 = near_door_wall.seg.intersection(op_door_wall.seg)[0]
                        p_m2 = p_m1 + op_door_wall.normal.p2 * wb_should
                        p_m1, p_m2 = DY_segment.get_p1_p2_from_normal(near_door_wall.normal, p_m1, p_m2)
                        m_bl = DY_segment(p_m1, p_m2)
                        wb = WashBasin(m_bl)
                        self.ele_list.append(wb)
                    # 马桶放op,远中放花洒
                    mid = op_door_wall.seg.midpoint
                    p_t1 = mid
                    p_t2 = mid + near_door_wall.normal.p2 * (TOILET_DEV_W / 2)
                    p_t1, p_t2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_t1, p_t2)
                    t_bl = DY_segment(p_t1, p_t2)
                    tt = ToiletDevice(t_bl)
                    self.ele_list.append(tt)
                    sr = Spray()
                    p_s1 = far_door_wall.seg.midpoint
                    p_s2 = p_s1 + far_door_wall.dir.p2 * int(SPRAY_W)
                    p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(op_door_wall.normal, p_s1, p_s2)
                    s_bl = DY_segment(p_s1, p_s2)
                    sr.set_pos(s_bl, SPRAY_L)
                    self.ele_list.append(sr)
        # if self.boundary and self.virtual_boundary:
        #     self.vir_door_list[0], self.door_list[0] = \
        #         self.exchange_vir_door(self.vir_door_list[0], self.door_list[0])
        #     self.virtual_boundary, self.boundary = \
        #         self.exchange_vir_boundary(self.virtual_boundary, self.boundary)

    def run_abnormal(self):
        try:
            for e in self.ele_list:
                if isinstance(e, CommonElement.Door):
                    door = e
            for l in self.line_list:  # get windows
                if isinstance(l, DY_Line.Window):
                        self.win.append(l)
            far_vertice = get_far_vertice(door, self.boundary)

            for s in self.boundary.seg_list:
                if s.seg.is_parallel(door.backline.seg) and \
                        door.boundary.polygon.intersection(s.seg):
                    door_wall = s
                    break
            op_door_wall = get_opposite_bounds(door_wall, self.boundary)[0]

            # js_walls = get_adjacent_bounds(door_wall, self.boundary)
            d1, js_w1, d2, js_w2 = get_doorbackline_wall_dis(self.boundary, door)


            tolit_p1 = far_vertice + op_door_wall.normal.p2 * TOLIT_AWAY_WALL
            tolit_p2 = tolit_p1 + op_door_wall.normal.p2 * TOILET_DEV_W

            wb_p1 = another_p(op_door_wall, far_vertice)
            wb_p2 = wb_p1 + op_door_wall.normal.p2 * min(WASHBASIN_W)

            if d1 < d2:
                sr_mid = Point2D(int(js_w2.seg.midpoint.x), int(js_w2.seg.midpoint.y))
                sr_p1 = sr_mid + js_w2.dir.p2 * int(SPRAY_W / 2)
                sr_p2 = sr_mid - js_w2.dir.p2 * int(SPRAY_W / 2)
                if self.win:
                    self.tt_put(tolit_p1, tolit_p2, js_w2.normal)
                    self.sr_put(sr_p1, sr_p2, js_w2.normal)
                    wb_line = DY_segment(wb_p1, wb_p2)
                    if js_w1.seg.length >= min(WASHBASIN_W) and wb_line.seg.contains(self.win[0].seg) is False:
                        self.wb_put(wb_p1, wb_p2, js_w1.normal)
                    else:
                        for e in self.ele_list:
                            if isinstance(e, ToiletDevice):
                                self.ele_list.remove(e)
                            if isinstance(e, Spray):
                                self.ele_list.remove(e)
                        wb_p1 = far_vertice
                        wb_p2 = wb_p1 + op_door_wall.normal.p2 * min(WASHBASIN_W)
                        sr_mid = Point2D(int(js_w1.seg.midpoint.x), int(js_w1.seg.midpoint.y))
                        sr_p1 = sr_mid + js_w1.dir.p2 * int(SPRAY_W / 2)
                        sr_p2 = sr_mid - js_w1.dir.p2 * int(SPRAY_W / 2)
                        tolit_p1 = another_p(op_door_wall, far_vertice) + op_door_wall.normal.p2 * TOLIT_AWAY_WALL
                        tolit_p2 = tolit_p1 + op_door_wall.normal.p2 * TOILET_DEV_W
                        if js_w1.seg.length >= min(WASHBASIN_W):
                            self.wb_put(wb_p1, wb_p2, js_w2.normal)
                        self.tt_put(tolit_p1, tolit_p2, js_w1.normal)
                        self.sr_put(sr_p1, sr_p2, js_w1.normal)
                else:
                    if js_w1.seg.length >= min(WASHBASIN_W):
                        self.wb_put(wb_p1, wb_p2, js_w1.normal)
                    self.tt_put(tolit_p1, tolit_p2, js_w2.normal)
                    self.sr_put(sr_p1, sr_p2, js_w2.normal)
            else:
                sr_mid = js_w1.seg.midpoint
                sr_p1 = sr_mid + js_w1.dir.p2 * int(SPRAY_W / 2)
                sr_p2 = sr_mid - js_w1.dir.p2 * int(SPRAY_W / 2)

                if self.win:
                    self.tt_put(tolit_p1, tolit_p2, js_w1.normal)
                    self.sr_put(sr_p1, sr_p2, js_w1.normal)
                    wb_line = DY_segment(wb_p1, wb_p2)
                    if js_w1.seg.length >= min(WASHBASIN_W) and wb_line.seg.contains(self.win[0].seg) is False:
                        self.wb_put(wb_p1, wb_p2, js_w2.normal)
                    else:
                        for e in self.ele_list:
                            if isinstance(e, ToiletDevice):
                                self.ele_list.remove(e)
                            if isinstance(e, Spray):
                                self.ele_list.remove(e)
                        wb_p1 = far_vertice
                        wb_p2 = wb_p1 + op_door_wall.normal.p2 * min(WASHBASIN_W)
                        sr_mid = Point2D(int(js_w2.seg.midpoint.x), int(js_w2.seg.midpoint.y))
                        sr_p1 = sr_mid + js_w2.dir.p2 * int(SPRAY_W / 2)
                        sr_p2 = sr_mid - js_w2.dir.p2 * int(SPRAY_W / 2)
                        tolit_p1 = another_p(op_door_wall, far_vertice) + op_door_wall.normal.p2 * TOLIT_AWAY_WALL
                        tolit_p2 = tolit_p1 + op_door_wall.normal.p2 * TOILET_DEV_W
                        if js_w1.seg.length >= min(WASHBASIN_W):
                            self.wb_put(wb_p1, wb_p2, js_w1.normal)
                        self.tt_put(tolit_p1, tolit_p2, js_w2.normal)
                        self.sr_put(sr_p1, sr_p2, js_w2.normal)
                    # sr_line = DY_segment(sr_p1, sr_p2)
                    # if sr_line.seg.contains(self.win[0].p1) or sr_line.seg.contains(self.win[0].p2):
                    #     sr_mid = js_w1.seg.midpoint
                    #     sr_p1 = sr_mid + js_w1.dir.p2 * int(SPRAY_W / 2)
                    #     sr_p2 = sr_mid - js_w1.dir.p2 * int(SPRAY_W / 2)
                    #     self.sr_put(sr_p1, sr_p2, js_w1.normal)
                    # else:
                    #     self.sr_put(sr_p1, sr_p2, op_door_wall.normal)
                else:
                    if js_w1.seg.length >= min(WASHBASIN_W):
                        self.wb_put(wb_p1, wb_p2, js_w2.normal)
                    self.tt_put(tolit_p1, tolit_p2, js_w1.normal)
                    self.sr_put(sr_p1, sr_p2, js_w1.normal)

            return True
        except Exception as e:
            print(e)
            pass

    def run_sub_regions_old_method(self):
        # print('here running sub_region')
        '''
        主要处理干湿分离情况(简单处理)：
        1.当前布局思想为提取最大矩形来完成粗略布局
        2.剩余情况用run_abnormal()来处理
        '''
        win_tag = False
        door_tag = False
        vir_dr_tag = False
        vir_win_tag = False
        self.virtual_boundary = get_virtual_boundary(self.boundary)#get max virtual_boundary

        for i in self.ele_list:#get doors
            if isinstance(i, CommonElement.Door):
                self.door_list.append(i)
                door_tag = True
        for l in self.line_list:#get windows
            if isinstance(l, DY_Line.Window):
                self.win.append(l)
                win_tag = True

        dr_line = get_vir_door(self.door_list[0], self.boundary)#line_door = f(door)
        # self.door_list[0].backline = dr_line#refresh door's backline
        dr_mid_p = dr_line.seg.midpoint

        inner_pt = get_inner_point(self.boundary)


        vir_inner = []
        inner_pt_seg = []
        if win_tag:
            win_mid_p = self.win[0].seg.midpoint
            for s in self.virtual_boundary.seg_list:
                if s.seg.contains(dr_mid_p):
                    vir_dr_tag = True
                    if s.seg.contains(win_mid_p):
                        vir_win_tag = True
                        self.virtual_boundary, self.boundary = \
                            exchange_vir_boundary(self.virtual_boundary, self.boundary) # change the layout bounds
                        self.run411()
                    else:
                        self.virtual_boundary, self.boundary = \
                            exchange_vir_boundary(self.virtual_boundary, self.boundary)
                        self.run410()
                    break
                else:
                    # we need only represent the door on the opening
                    for in_pt in inner_pt:
                        if s.seg.contains(in_pt):
                            vir_inner.append(in_pt)
                            inner_pt_seg.append(s)
                    if len(inner_pt_seg) == 2:
                        dr_line = DY_segment(vir_inner[0], vir_inner[1])
                    elif len(inner_pt_seg) == 1:
                        for s in self.boundary.seg_list:
                            if s.seg.contains(vir_inner[0]):
                                inter_pt = another_p(s, vir_inner[0])
                                for s_vir in self.virtual_boundary.seg_list:
                                    if s_vir.contains(vir_inner[0]):
                                        dr_pt = another_p(s_vir, inter_pt)
                                        dr_line = DY_segment(vir_inner[0], dr_pt)
                                        self.vir_door_list.append(get_new_door(dr_line))
                                        break
                    else:
                        raise Exception('此户型没有标注门的信息！')
                    if s.seg.contains(win_mid_p):
                        vir_dr_tag = False
                        self.vir_door_list[0], self.door_list[0] = \
                            exchange_vir_door(self.vir_door_list[0], self.door_list[0])
                        self.virtual_boundary, self.boundary = \
                            exchange_vir_boundary(self.virtual_boundary, self.boundary)
                        self.run411()
                        break
                    else:
                        self.vir_door_list[0], self.door_list[0] = \
                            exchange_vir_door(self.vir_door_list[0], self.door_list[0])
                        self.virtual_boundary, self.boundary = \
                            exchange_vir_boundary(self.virtual_boundary, self.boundary)
                        self.run410()
                        break
        else:
            #we need represent the door on the opening
            for s in self.virtual_boundary.seg_list:
                if s.seg.contains(dr_mid_p):
                    vir_dr_tag = True
                    self.virtual_boundary, self.boundary = \
                        exchange_vir_boundary(self.virtual_boundary, self.boundary)
                    self.run410()
                    break
                else:
                    for in_pt in inner_pt:
                        if s.seg.contains(in_pt):
                            vir_inner.append(in_pt)
                            inner_pt_seg.append(s)
                    if len(inner_pt_seg) == 2:
                        dr_line = DY_segment(vir_inner[0], vir_inner[1])
                        self.vir_door_list.append(get_new_door(dr_line))
                        self.vir_door_list[0], self.door_list[0] = \
                            exchange_vir_door(self.vir_door_list[0], self.door_list[0])
                        self.virtual_boundary, self.boundary = \
                            exchange_vir_boundary(self.virtual_boundary, self.boundary)
                        self.run410()
                    elif len(inner_pt_seg) == 1:
                        for s in self.boundary.seg_list:
                            if s.seg.contains(vir_inner[0]):
                                inter_pt = another_p(s, vir_inner[0])
                                for s_vir in self.virtual_boundary.seg_list:
                                    if s_vir.seg.contains(vir_inner[0]):
                                        dr_pt = another_p(s_vir, inter_pt)
                                        dr_line = DY_segment(vir_inner[0], dr_pt)
                                        self.vir_door_list.append(get_new_door(dr_line))
                                        break
                        self.vir_door_list[0], self.door_list[0] = \
                            exchange_vir_door(self.vir_door_list[0], self.door_list[0])
                        self.virtual_boundary, self.boundary = \
                            exchange_vir_boundary(self.virtual_boundary, self.boundary)
                        self.run410()
                    # else:
                    #     self.boundary = self.virtual_boundary
                    #     self.run410()

    def run_sub_regions(self):
        # print('here running sub_region but now it can not ')
        # self.run_abnormal()
        '''
        主要处理干湿分离情况(简单处理)：
        1.当前布局思想为提取最大矩形来完成粗略布局
        用类似run_abnormal()情况来处理，但后期需要映射门和窗户到virtual_boundary上
        # '''

    def shower_case(self, flag):
        if flag == 0:
            sr = ShowerRoom()
            case = [SHOWER_W, SHOWER_L]
        else:
            sr = Spray()
            case = [SPRAY_W, SPRAY_L]
        return sr, case

    def wash_machine_flag_select(self, flag2, flag3):
        if flag2 and flag3 is False:
            case_wh = 2
        if flag3 and flag2 is False:
            case_wh = 0
        if flag3 and flag2:
            case_wh = random.randint(0, 1)
        if not flag2 and flag3 is False:
            case_wh = 3
        return case_wh

    def wb_put(self, p_m1, p_m2, dir):  # 放置wb直接self.wb_put(p_m1,p_m2,dir)dir表示方向下面组件一样
        p_m1, p_m2 = DY_segment.get_p1_p2_from_normal(dir, p_m1, p_m2)
        m_bl = DY_segment(p_m1, p_m2)
        wb = WashBasin(m_bl)
        self.ele_list.append(wb)

    def tt_put(self, p_t1, p_t2, dir):
        p_t1, p_t2 = DY_segment.get_p1_p2_from_normal(dir, p_t1, p_t2)
        t_bl = DY_segment(p_t1, p_t2)
        tt = ToiletDevice(t_bl)
        self.ele_list.append(tt)

    def sr_put(self, p_s1, p_s2, dir):
        sr = Spray()
        p_s1, p_s2 = DY_segment.get_p1_p2_from_normal(dir, p_s1, p_s2)
        s_bl = DY_segment(p_s1, p_s2)
        sr.set_pos(s_bl, SPRAY_L)
        self.ele_list.append(sr)
    # def sroom_put(self,p_s1, p_s2,dir):暂时不写






