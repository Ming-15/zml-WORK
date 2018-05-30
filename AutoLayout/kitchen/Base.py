# -*- coding:utf-8 -*-
import pandas as pd
from sympy.geometry import Point2D, Line, Point
import AutoLayout.kitchen.utility as utl
from AutoLayout.CommonElement import Door
from AutoLayout.DY_Line import Border, Window
import AutoLayout.helpers as helpers
from AutoLayout.kitchen.Element import *
from AutoLayout.BaseModual import Region, DY_segment
from AutoLayout.kitchen.settings import *
import AutoLayout.settings as settings


class Kitchen(Region):
    def __init__(self):
        super(Kitchen, self).__init__()
        self.w = 0  # 户型的短边长度，宽
        self.l = 0  # 长边长度，长
        self.triangle_long_table()
        self.residual_len_table()

        self.triangle_vertice = None #for L or U type
        #L_type 2-sides
        self.long_seg = None
        self.short_seg = None
        #U_type 3-sides
        self.u0 = None
        self.u1_tri = None  # 三角结构的u1边
        self.u1_reg = None  # 冰箱的u1边

        self.O0 = None
        self.O1 = None
        self.p1_reg_seg = None
        self.p2_rank_seg = None

    def run(self):
        arrangement_dict = {
            (4, 1, 1, 0): self.run4110,
            (4, 0, 1, 1): self.run4011,
            (4, 1, 0, 1): self.run4101_4200_4210,
            (4, 2, 0, 0): self.run4101_4200_4210,
            (4, 2, 1, 0): self.run4101_4200_4210,#here just one situation that window connects the balcony
            (4, 1, 1, 1): self.run4111,
            (4, 1, 0, 0): self.run4100,
        }

        key = (len(self.boundary.polygon.vertices), self.doors,
               self.windows, self.borders)
        if not arrangement_dict.get(key, False):
            # raise Exception("warning:厨房暂时不支持这种户型")
            self.run_any()
        res = arrangement_dict.get(key)()
    # ==========厨房4111布局,包含虚边界不完整布局======================================================================================
    def run_any(self):
        xmin, ymin, xmax, ymax = self.boundary.polygon.bounds
        if len(self.boundary.polygon.vertices) != 4:
            for p in self.boundary.polygon.vertices:

                if p.x != xmin and p.x != xmax and p.y != ymin and p.y != ymax:
                    inner_point = p
                    # 找到过道区域, 先找内部点划分后比较短的线段
                    pp = inner_point
                    # intersection
                    intersec_list = self.boundary.polygon.intersection(Line(pp, Point(pp.x, pp.y + 1)))
                    for p in intersec_list:
                        if isinstance(p, Point2D):
                            p0 = p
                            break
                    intersec_list = self.boundary.polygon.intersection(Line(pp, Point(pp.x + 1, pp.y)))
                    for p in intersec_list:
                        if isinstance(p, Point2D):
                            p1 = p
                            break
                    if inner_point.distance(p0) < inner_point.distance(p1):
                        xlen = inner_point.distance(p1)
                        ylen = ymax - ymin
                    else:
                        xlen = xmax - xmin
                        ylen = inner_point.distance(p0)
                    self.w = min(xlen, ylen)
                    self.l = max(xlen, ylen)
                    break
                else:
                    self.l, self.w = utl.room_size_judgement(self.boundary)
        else:
            self.l, self.w = utl.room_size_judgement(self.boundary)
        self.run4110_small()
    def run4111(self):
        self.l, self.w = utl.room_size_judgement(self.boundary)
        fun_ul = self.run4111_o_or_l()
        fun_ul()
    def run4111_o_or_l(self):
        res = None
        door = helpers.get_eles(self.ele_list, Door)
        door = door[0]
        border_list = [b for b in self.line_list if isinstance(b, Border)]
        border_bound = [s for s in self.boundary.seg_list if s.seg.contains(border_list[0].seg)]
        if border_list[0].seg != border_bound[0].seg:
            dis0 = border_list[0].seg.p1.distance(door.boundary.polygon.centroid)
            dis1 = border_list[0].seg.p2.distance(door.boundary.polygon.centroid)
            if dis0 > dis1:
                p1 = border_bound[0].seg.p1 if border_bound[0].seg.p1.distance(door.boundary \
                    .polygon.centroid) > border_bound[0].seg.p2.distance(door.boundary \
                    .polygon.centroid) else border_bound[0].seg.p2
                dis = border_list[0].seg.p1.distance(p1)
                if dis > CABINET_L:
                    res = self.run4110_L
                else:
                    res = self.run4101_4200_4210_O
            elif dis0 < dis1:
                p2 = border_bound[0].seg.p2 if border_bound[0].seg.p2.distance(door.boundary \
                       .polygon.centroid) > border_bound[0].seg.p1.distance(door.boundary \
                       .polygon.centroid) else border_bound[0].seg.p1
                dis = border_list[0].seg.p2.distance(p2)
                if dis > CABINET_L:
                    res = self.run4110_L
                else:
                    res = self.run4101_4200_4210_O
        else:
            res = self.run4101_4200_4210_O
        return res
    # =================================================================================================
    def run4100(self):
        self.l, self.w = utl.room_size_judgement(self.boundary)
        if self.l < RANGEHOOD_SINK_W * 2 or (self.w > CABINET_L and self.w < CABINET_L + BASE_CORNER_W[0]):
            fun_ul = self.run4110_small()
            fun_ul()
    def run4110(self):
        self.l, self.w = utl.room_size_judgement(self.boundary)
        if self.l < RANGEHOOD_SINK_W * 2 or (self.w > CABINET_L and self.w < CABINET_L + BASE_CORNER_W[0]):
            fun_ul = self.run4110_small()
        else:
            fun_ul = self.get_4110_U_or_L()
        fun_ul()

    def run4011(self):  # mostly U_type, open——type not applied now
        self.l, self.w = utl.room_size_judgement(self.boundary)

        pass

    def run4101_4200_4210(self):
        self.l, self.w = utl.room_size_judgement(self.boundary)
        fun_opl = self.get_4101_4200_4210_O_or_P_or_L()
        fun_opl()

    def get_4110_U_or_L(self):
        """对4110型户型，判断U型或L型布局"""
        res = None
        door = helpers.get_eles(self.ele_list, Door)
        if door[0].type == settings.DOOR_TYPE[2]:
            # 推拉门时，门所在墙的长度必须满足两个地柜间距，才选择U型布局
            parallel_wall_dr = helpers.get_paralleled_line(door[0].backline, self.boundary, type=DY_segment)
            if parallel_wall_dr[0].seg.length < MIN_DIS_CABINET + 2 * CABINET_L:
                res = self.run4110_L
                return res
            res = self.run4110_U
        if door[0].type == settings.DOOR_TYPE[0] or settings.DOOR_TYPE[1]:
            tmp_seg = DY_segment(door[0].backline.normal.p1, door[0].backline.normal.p2)
            parallel_wall_dr = helpers.get_paralleled_line(tmp_seg, self.boundary, type=DY_segment)
            tmp_seg = parallel_wall_dr[0]
            dis0 = helpers.get_min_dis_seg_boundary(tmp_seg, door[0].boundary)
            tmp_seg = parallel_wall_dr[1]
            dis1 = helpers.get_min_dis_seg_boundary(tmp_seg, door[0].boundary)

            # 非推拉门时，门距离两侧墙距离大于地柜长度时，才选择U型布局
            if dis0 <= CABINET_L or dis1 <= CABINET_L:
                res = self.run4110_L
            elif dis0 > CABINET_L and dis1 > CABINET_L:
                res = self.run4110_U
        return res

    def get_4101_4200_4210_O_or_P_or_L(self):
        """对4200（4顶点，2门，无窗，无边界）型/4101（4顶点，1门，无窗，1边界）型/4210(4顶点，2门，1窗，无边界)户型，
        判断一字形或平行布局或L型布局"""
        res = None
        border_flag = False
        second_door_flag = False
        win_flag = False
        door = helpers.get_eles(self.ele_list, Door)

        for dr_connect in DOOR_CONNECT:
            for dr in door:
                if dr_connect in dr.connect_list:#balcony 阳台
                    door_out = dr
                else:
                    door_in = dr
        if len(door) >= 2:
            second_door_flag = True
        for l in self.line_list:
            if isinstance(l, Border):
                border = l
                border_flag = True
                second_door_flag = False
            if isinstance(l, Window):
                win1 = l
                win_flag = True
        if border_flag:
            if door[0].backline.line.is_parallel(border.line):
                # add by lxy
                # ================================================================================
                dis0, dis1, dis2, dis3 = utl.get_doorbackline_wall_dis(self.boundary, door_in)
                # ================================================================================
                if self.l >= D1_MIN and self.l <= D1_MAX:
                    if self.w >= D2_TH1 and self.w < D2_TH2:
                        res = self.run4101_4200_4210_O
                    # add by lxy
                    # ============================================================================
                    elif self.w >= D2_TH2 and dis0 > CABINET_L and dis1 > CABINET_L:
                    #=============================================================================
                        res = self.run4101_4200_4210_P
                    else:
                        res = self.run4110_small()
                else:
                    # raise Exception("warning:此户型当前不满足条件")
                    res = self.run4110_small()
            else:
                # 存在阳台的情况下l_flag小于1500,或者虚边界包含距离门中心最远距离的点的情况下运行一字型户型
                l_flag = utl.get_l_flag_has_border_or_anotherdoor(door_in, self.boundary, border, None)
                if  l_flag:
                    res = self.run4101_4200_4210_L
                else:
                    res = self.run4101_4200_4210_O
        elif second_door_flag:
            if door_in.backline.line.is_parallel(door_out.backline.line):
                dis0, dis1, dis2, dis3 = utl.get_doorbackline_wall_dis(self.boundary, door_in, door_out)
                if self.l >= D1_MIN and self.l <= D1_MAX:
                    if self.w >= D2_TH1 and self.w < D2_TH2:
                        res = self.run4101_4200_4210_O
                    #when all door_wall_dis satisfy the cabinet len then go P_type
                    elif self.w >= D2_TH2 and dis0 > CABINET_L and dis1 > CABINET_L and dis2 > CABINET_L \
                            and dis3 > CABINET_L:
                        res = self.run4101_4200_4210_P
                    else:
                        res = self.run4110_small()
                else:
                    res = self.run4110_small()
            elif door_in.backline.line.is_perpendicular(door_out.backline.line):
                # win_normal.is_perpendicular(bord_normal)
                res = self.run4110_small()
            else:
                l_flag = utl.get_l_flag_has_border_or_anotherdoor(door_in, self.boundary, None, door_out)#两个门需要甄别出来
                # L_type ,is there anything more to be considered?
                if l_flag:
                    res = self.run4101_4200_4210_L
                else:
                    res = self.run4101_4200_4210_O

        else:
            raise Exception("warning:此户型当前不满足条件")

        return res

    def run4110_L(self):
        door = helpers.get_eles(self.ele_list, Door)

        # 通过离门最远的顶点，找到三角结构的顶点
        self.triangle_vertice = utl.get_triangle_vertice(door[0], self.boundary)
        for seg in self.boundary.seg_list:
            if seg.seg.length == self.l and seg.seg.contains(self.triangle_vertice):
                self.long_seg = seg
            if seg.seg.length == self.w and seg.seg.contains(self.triangle_vertice):
                self.short_seg = seg

        # 判断长边是否撞门,
        p1 = self.triangle_vertice + self.long_seg.normal.p2 * CABINET_L
        p2 = p1 + self.short_seg.normal.p2 * 1
        cabinet_seg = DY_segment(p1, p2)
        inter_pt = helpers.get_points_seg_intersect_boundary(cabinet_seg, door[0].boundary)
        # 如果撞门，更新长边!
        if len(inter_pt) != 0:
            l1 = DY_segment(p1, inter_pt[0])
            l2 = DY_segment(p1, inter_pt[1])
            l_length = min(l1.seg.length, l2.seg.length)
            self.l = l_length
            longsegp1, longsegp2 = DY_segment.get_p1_p2_from_normal(
                self.long_seg.normal,
                self.triangle_vertice,
                self.triangle_vertice + self.short_seg.normal.p2 * self.l)
            self.long_seg = DY_segment(longsegp1, longsegp2)
            if l_length < self.w:
                self.l, self.w = self.w, self.l
                self.long_seg, self.short_seg = self.short_seg, self.long_seg

        if self.l < BASE_CORNER_W[0] + RANGEHOOD_SINK_W:
            # raise Exception("warning:厨房功能区长宽不足")
            # add by lxy
            # ==========================================================================
            self.l = max([i.seg.length for i in self.boundary.seg_list])
            self.w = min([i.seg.length for i in self.boundary.seg_list])
            self.run4110_small()
            return
            #=========================================================================
        # 判断是否布置冰箱,并布置
        if_refig, seg_l, seg_s = self.arrange_L_refrigerator()
        l_flag = False
        s_flag = False
        # 布置冰箱后需要获知冰箱在长边还是短边
        if if_refig:
            if seg_l.seg.length != self.long_seg.seg.length:  # 长边布置了冰箱
                l_flag = True
                s_flag = False
            elif seg_s.seg.length != self.short_seg.seg.length:  # 短边布置了冰箱
                s_flag = True
                l_flag = False
        ##################################布置地柜################################
        # 布置长边
        '''通过长/短边的尺寸与是否放置冰箱在表格中选择最佳组合'''
        l_res = self.l - REFRIGERATOR_W
        if l_flag:
            suit_long_df = self.triangle_long_df. \
                loc[self.triangle_long_df.sum_len <= l_res]
            suit_long_df = suit_long_df.ix[suit_long_df.sum_len.idxmax]

            cabinet_wid = suit_long_df['cabinet_wid']
            corner_wid = suit_long_df['corner_wid']
            sink_ran_wid = suit_long_df['sink_ran_wid']
        else:
            suit_long_df = self.triangle_long_df. \
                loc[self.triangle_long_df.sum_len <= self.l]
            suit_long_df = suit_long_df.ix[suit_long_df.sum_len.idxmax]

            cabinet_wid = suit_long_df['cabinet_wid']
            corner_wid = suit_long_df['corner_wid']
            sink_ran_wid = suit_long_df['sink_ran_wid']

        '''配置转角地柜'''
        p1, p2 = self.long_seg.p1, self.long_seg.p2  # 也可以用交点方法获取点。
        cor_p1 = p2 if p2 == self.triangle_vertice else p1
        cor_p2 = cor_p1 + self.short_seg.normal.p2 * corner_wid
        cab_p1 = cor_p2
        cab_p2 = cab_p1 + self.short_seg.normal.p2 * cabinet_wid  # 保持点的连贯，防止backline更新导致错误
        sink_p1 = cab_p2
        sink_p2 = sink_p1 + self.short_seg.normal.p2 * sink_ran_wid

        cor_p1, cor_p2 = DY_segment. \
            get_p1_p2_from_normal(self.long_seg.normal, cor_p1, cor_p2)
        cor_bl = DY_segment(cor_p1, cor_p2)
        cor = self.get_L_corner_cabinet_type(cor_bl, CABINET_L)
        self.ele_list.append(cor)
        '''配置cabinet如果有'''
        if cabinet_wid != 0:
            cab_p1, cab_p2 = DY_segment. \
                get_p1_p2_from_normal(self.long_seg.normal, cab_p1, cab_p2)
            cab_bl = DY_segment(cab_p1, cab_p2)
            cab = SingleCabinet(cab_bl, CABINET_L)
            self.ele_list.append(cab)
        '''配置烟机或水槽柜/优先布置水槽柜在角落结构的长边'''
        sink_ran_p1, sink_ran_p2 = DY_segment. \
            get_p1_p2_from_normal(self.long_seg.normal, sink_p1, sink_p2)
        sink_bl = DY_segment(sink_ran_p1, sink_ran_p2)
        sink = SinkCabinet(sink_bl, CABINET_L)
        self.ele_list.append(sink)
        '''补齐长边剩余'''
        start_pt = sink_p2
        if l_flag:
            end_pt = seg_l.seg.p1 if seg_l.seg.p2 == self.triangle_vertice \
                else  seg_l.seg.p2
            if start_pt != end_pt:
                start_ptt, end_pt = DY_segment. \
                    get_p1_p2_from_normal(self.long_seg.normal, start_pt, end_pt)
                res_seg = DY_segment(start_ptt, end_pt)
                utl.arrange_cabinet_along_seg(res_seg, start_pt,
                                              self.ele_list, self.residual_len_table)
        else:
            end_pt = self.long_seg.seg.p1 if self.long_seg.seg.p2 == \
                                             self.triangle_vertice else self.long_seg.seg.p2
            if start_pt != end_pt:
                start_ptt, end_pt = DY_segment. \
                    get_p1_p2_from_normal(self.long_seg.normal, start_pt, end_pt)
                res_seg = DY_segment(start_ptt, end_pt)
                utl.arrange_cabinet_along_seg(res_seg, start_pt,
                                              self.ele_list, self.residual_len_table)
                # 布置短边
        '''优先布置烟机柜'''
        ref_p = self.triangle_vertice
        ran_p1 = ref_p + self.long_seg.normal.p2 * CABINET_L
        ran_p2 = ran_p1 + self.long_seg.normal.p2 * RANGEHOOD_SINK_W
        ran_p1, ran_p2 = DY_segment. \
            get_p1_p2_from_normal(self.short_seg.normal, ran_p1, ran_p2)
        ran_bl = DY_segment(ran_p1, ran_p2)
        ran = RangehoodCabinet(ran_bl, CABINET_L)
        self.ele_list.append(ran)
        '''补齐短边剩余'''
        start_pt = self.triangle_vertice + self.long_seg.normal.p2 * \
                                           (CABINET_L + RANGEHOOD_SINK_W)
        if s_flag:
            end_pt = seg_s.seg.p1 if seg_s.seg.p2 == self.triangle_vertice \
                else  seg_s.seg.p2
            if start_pt != end_pt:
                start_ptt, end_pt = DY_segment. \
                    get_p1_p2_from_normal(self.short_seg.normal, start_pt, end_pt)
                res_seg = DY_segment(start_ptt, end_pt)

                utl.arrange_cabinet_along_seg(res_seg, start_pt,
                                              self.ele_list, self.residual_len_table)
        else:
            end_pt = self.short_seg.seg.p1 if self.short_seg.seg.p2 == \
                                              self.triangle_vertice else self.short_seg.seg.p2
            if start_pt != end_pt:
                start_ptt, end_pt = DY_segment. \
                    get_p1_p2_from_normal(self.short_seg.normal, start_pt, end_pt)
                res_seg = DY_segment(start_ptt, end_pt)
                utl.arrange_cabinet_along_seg(res_seg, start_pt,
                                              self.ele_list, self.residual_len_table)

        # 判断窗户，如果在短边，烟机和水槽互换
        for l in self.line_list:
            if isinstance(l, Window):
                win = l
        if self.short_seg.seg.contains(win.seg):
            self.ele_list.remove(ran)
            self.ele_list.remove(sink)
            sink_new = RangehoodCabinet(sink_bl, CABINET_L)
            ran_new = SinkCabinet(ran_bl, CABINET_L)
            self.ele_list.append(sink_new)
            self.ele_list.append(ran_new)
        # 寻找第一个SingleCabinet, 替换成DrawerCabinet
        singlelist = []
        exsist = False
        for e in self.ele_list:
            if isinstance(e, SingleCabinet):
                singlelist.append(e)
                exsist = True
        if exsist:
            self.ele_list.remove(singlelist[0])
            drawcab_new = DrawerCabinet(singlelist[0].backline, CABINET_L)
            self.ele_list.append(drawcab_new)
        #################################布置吊柜######################################################################
        # 判断是否可以摆放转角吊柜并摆放
        is_hang_corner = utl.is_arrange_hanging_corner(
            self.long_seg, self.short_seg,
            self.triangle_vertice, self.boundary,
            self.line_list[0], HANGING_BASE_CORNER_LW[0])
        # 首先放置烟机吊柜
        for e in self.ele_list:
            if isinstance(e, RangehoodCabinet):
                ran_bl = e.backline
            if isinstance(e, SinkCabinet):
                sink_bl = e.backline
        ranhang = RanHangingCabinet(ran_bl, HANGING_CABINET_L)
        self.ele_list.append(ranhang)
        '''
             当前方法--需要分出多个seg逐一处理：
             烟机默认放在短边
             有窗户（只考虑是否在long_seg或short_seg上）：
                 是否有转角吊柜？
                 在长边：需要以窗户分割出seg,有转角吊柜时起点为其backline的p1,
                        短边则需要以烟机吊柜的一个端点为起点
                 在短边：此时的分段需要以窗户分割，有转角吊柜时起点为其backline的p1
                        则长边需要以烟机吊柜分割,长边其中一个起点为转角吊柜的另一长边的的端点
                        （非self.triangle_vertice）
             无窗户
                 只考虑烟机分割出seg即可,起点主要为转角吊柜上的长边与短边的交点
             '''
        win = self.line_list[0]
        res_flag = False
        # 窗户在三角结构内
        if self.long_seg.seg.contains(win.seg) or self.short_seg.seg.contains(win.seg):
            # 有转角吊柜
            if is_hang_corner:
                corner, cor_bl_wall = utl.get_hanging_corner_cabinet(self.long_seg, self.short_seg,
                                                                     self.triangle_vertice, HANGING_BASE_CORNER_LW[0],
                                                                     self.ele_list)
                # add by lxy
                # ===============================================================================================
                if if_refig:
                    p1 = seg_l.p2 if seg_l.seg.p1 == self.triangle_vertice else seg_l.seg.p1
                    p2 = p1 + seg_l.dir.p2 * REFRIGERATOR_W
                    refri_seg = DY_segment(p1, p2)
                # ===============================================================================================
                # 长边有窗户
                if self.long_seg.seg.contains(win.seg):
                    # 转角吊柜的backline在长边
                    if cor_bl_wall == self.long_seg:
                        start_pt = corner.backline.p1
                        end_pt = win.seg.p1 if win.seg.p1.distance(self.triangle_vertice) \
                                               < win.seg.p2.distance(self.triangle_vertice) else win.seg.p2
                        # add by lxy
                        # ========================================================================================
                        end_pt = end_pt - self.short_seg.normal.p2 * WIN_SIDES_D
                        # ============================================================================================
                        if start_pt != end_pt:
                            start_ptt, end_pt = DY_segment. \
                                get_p1_p2_from_normal(self.long_seg.normal, start_pt, end_pt)
                            seg1 = DY_segment(start_ptt, end_pt)

                            utl.arrange_hanging_along_seg(seg1, HANGING_CABINET_W[0], start_pt,
                                                          self.ele_list, self.boundary, res_flag)

                        start_pt = win.seg.p2 if win.seg.p1.distance(self.triangle_vertice) \
                                                 < win.seg.p2.distance(self.triangle_vertice) else win.seg.p1
                        # add by lxy
                        # ==================================================================================
                        start_pt = start_pt + self.short_seg.normal.p2 * WIN_SIDES_D
                        # ===================================================================================
                        end_pt = seg_l.seg.p1 if seg_l.seg.p2 == self.triangle_vertice else seg_l.seg.p2
                        # add by lxy
                        # ======================================================================================
                        if if_refig:
                            # ===============================================================================
                            if refri_seg.seg.contains(win.seg.p1) or refri_seg.seg.contains(win.seg.p2):
                                pass
                            else:
                                # =================================================================================
                                if start_pt != end_pt:
                                    start_ptt, end_pt = DY_segment. \
                                        get_p1_p2_from_normal(self.long_seg.normal, start_pt, end_pt)
                                    seg2 = DY_segment(start_ptt, end_pt)

                                    utl.arrange_hanging_along_seg(seg2, HANGING_CABINET_W[0], start_pt,
                                                                  self.ele_list, self.boundary, res_flag)

                        start_pt = corner.backline.p2 + corner.backline.normal.p2 * \
                                                        (HANGING_BASE_CORNER_LW[0] + RANGEHOOD_SINK_W)
                        end_pt = seg_s.seg.p2 if seg_s.seg.p1 == self.triangle_vertice else seg_s.seg.p1

                        if start_pt != end_pt:
                            start_ptt, end_pt = DY_segment. \
                                get_p1_p2_from_normal(self.short_seg.normal, start_pt, end_pt)
                            seg3 = DY_segment(start_ptt, end_pt)

                            utl.arrange_hanging_along_seg(seg3, HANGING_CABINET_W[0], start_pt,
                                                          self.ele_list, self.boundary, res_flag)

                    # 转角吊柜的backline在短边
                    else:
                        start_pt = self.triangle_vertice + corner.backline.normal.p2 * HANGING_BASE_CORNER_LW[0]
                        end_pt = win.seg.p1 if win.seg.p1.distance(self.triangle_vertice) \
                                               < win.seg.p2.distance(self.triangle_vertice) else win.seg.p2
                        # add by lxy
                        # ====================================================================================
                        end_pt = end_pt - self.short_seg.normal.p2 * WIN_SIDES_D
                        # ======================================================================================
                        if start_pt != end_pt:
                            start_ptt, end_pt = DY_segment. \
                                get_p1_p2_from_normal(self.long_seg.normal, start_pt, end_pt)
                            seg1 = DY_segment(start_ptt, end_pt)

                            utl.arrange_hanging_along_seg(seg1, HANGING_CABINET_W[0], start_pt,
                                                          self.ele_list, self.boundary, res_flag)

                        start_pt = win.seg.p2 if win.seg.p1.distance(self.triangle_vertice) \
                                                 < win.seg.p2.distance(self.triangle_vertice) else win.seg.p1
                        # add by lxy
                        # ====================================================================================
                        start_pt = start_pt + self.short_seg.normal.p2 * WIN_SIDES_D
                        # =====================================================================================
                        end_pt = seg_l.seg.p1 if seg_l.seg.p2 == self.triangle_vertice else seg_l.seg.p2
                        # add by lxy
                        # =====================================================================================
                        if refri_seg.seg.contains(win.seg.p1) or refri_seg.seg.contains(win.seg.p2):
                            pass
                        else:
                            # =================================================================================
                            if start_pt != end_pt:
                                start_ptt, end_pt = DY_segment. \
                                    get_p1_p2_from_normal(self.long_seg.normal, start_pt, end_pt)
                                seg2 = DY_segment(start_ptt, end_pt)

                                utl.arrange_hanging_along_seg(seg2, HANGING_CABINET_W[0], start_pt,
                                                              self.ele_list, self.boundary, res_flag)

                        start_pt = ran_bl.p2 if ran_bl.p1.distance(self.triangle_vertice) < \
                                                ran_bl.p2.distance(self.triangle_vertice) else ran_bl.p1
                        end_pt = seg_s.seg.p1 if seg_s.seg.p2 == self.triangle_vertice else seg_s.seg.p2
                        if start_pt != end_pt:
                            start_ptt, end_pt = DY_segment. \
                                get_p1_p2_from_normal(self.short_seg.normal, start_pt, end_pt)
                            seg3 = DY_segment(start_ptt, end_pt)

                            utl.arrange_hanging_along_seg(seg3, HANGING_CABINET_W[0], start_pt,
                                                          self.ele_list, self.boundary, res_flag)

                # 短边有窗户
                else:
                    # 转角吊柜的backline在长边
                    if cor_bl_wall == self.long_seg:
                        start_pt = corner.backline.p1
                        end_pt = ran_bl.seg.p1 if ran_bl.seg.p1.distance(self.triangle_vertice) \
                                                  < ran_bl.seg.p2.distance(self.triangle_vertice) else ran_bl.seg.p2
                        if start_pt != end_pt:
                            start_ptt, end_pt = DY_segment. \
                                get_p1_p2_from_normal(self.long_seg.normal, start_pt, end_pt)
                            seg1 = DY_segment(start_ptt, end_pt)

                            utl.arrange_hanging_along_seg(seg1, HANGING_CABINET_W[0], start_pt,
                                                          self.ele_list, self.boundary, res_flag)

                        start_pt = ran_bl.seg.p2 if ran_bl.seg.p1.distance(self.triangle_vertice) \
                                                    < ran_bl.seg.p2.distance(self.triangle_vertice) else ran_bl.seg.p1
                        end_pt = seg_l.seg.p1 if seg_l.seg.p2 == self.triangle_vertice else seg_l.seg.p2
                        if start_pt != end_pt:
                            start_ptt, end_pt = DY_segment. \
                                get_p1_p2_from_normal(self.long_seg.normal, start_pt, end_pt)
                            seg2 = DY_segment(start_ptt, end_pt)

                            utl.arrange_hanging_along_seg(seg2, HANGING_CABINET_W[0], start_pt,
                                                          self.ele_list, self.boundary, res_flag)
                        start_pt = corner.backline.p2 + corner.backline.normal.p2 * \
                                                        (HANGING_BASE_CORNER_LW[0])
                        end_pt = win.seg.p1 if win.seg.p1.distance(self.triangle_vertice) \
                                               < win.seg.p2.distance(self.triangle_vertice) else win.seg.p2
                        # add by lxy
                        # ==================================================================================
                        end_pt = end_pt - self.long_seg.normal.p2 * WIN_SIDES_D
                        # ====================================================================================
                        if start_pt != end_pt:
                            start_ptt, end_pt = DY_segment. \
                                get_p1_p2_from_normal(self.short_seg.normal, start_pt, end_pt)
                            seg3 = DY_segment(start_ptt, end_pt)

                            utl.arrange_hanging_along_seg(seg3, HANGING_CABINET_W[0], start_pt,
                                                          self.ele_list, self.boundary, res_flag)

                        start_pt = win.seg.p2 if win.seg.p1.distance(self.triangle_vertice) \
                                                 < win.seg.p2.distance(self.triangle_vertice) else win.seg.p1
                        # add by lxy
                        # ====================================================================================
                        start_pt = start_pt - seg_l.normal.p2 * WIN_SIDES_D
                        # ====================================================================================
                        end_pt = seg_s.seg.p1 if seg_s.seg.p2 == self.triangle_vertice else seg_s.seg.p2
                        if start_pt != end_pt:
                            start_ptt, end_pt = DY_segment. \
                                get_p1_p2_from_normal(self.short_seg.normal, start_pt, end_pt)
                            seg4 = DY_segment(start_ptt, end_pt)

                            utl.arrange_hanging_along_seg(seg4, HANGING_CABINET_W[0], start_pt,
                                                          self.ele_list, self.boundary, res_flag)

                    # 转角吊柜的backline在短边
                    else:
                        start_pt = self.triangle_vertice + corner.backline.normal.p2 * HANGING_BASE_CORNER_LW[0]
                        end_pt = ran_bl.seg.p1 if ran_bl.seg.p1.distance(self.triangle_vertice) \
                                                  < ran_bl.seg.p2.distance(self.triangle_vertice) else ran_bl.seg.p2

                        if start_pt != end_pt:
                            start_ptt, end_pt = DY_segment. \
                                get_p1_p2_from_normal(self.long_seg.normal, start_pt, end_pt)
                            seg1 = DY_segment(start_ptt, end_pt)

                            utl.arrange_hanging_along_seg(seg1, HANGING_CABINET_W[0], start_pt,
                                                          self.ele_list, self.boundary, res_flag)

                        start_pt = ran_bl.seg.p2 if ran_bl.seg.p1.distance(self.triangle_vertice) \
                                                    < ran_bl.seg.p2.distance(self.triangle_vertice) else ran_bl.seg.p1
                        end_pt = seg_l.seg.p1 if seg_l.seg.p2 == self.triangle_vertice else seg_l.seg.p2
                        if start_pt != end_pt:
                            start_ptt, end_pt = DY_segment. \
                                get_p1_p2_from_normal(self.long_seg.normal, start_pt, end_pt)
                            seg2 = DY_segment(start_ptt, end_pt)

                            utl.arrange_hanging_along_seg(seg2, HANGING_CABINET_W[0], start_pt,
                                                          self.ele_list, self.boundary, res_flag)

                        start_pt = corner.backline.p1
                        end_pt = win.seg.p1 if win.seg.p1.distance(self.triangle_vertice) \
                                               < win.seg.p2.distance(self.triangle_vertice) else win.seg.p2
                        # add by lxy
                        # ========================================================================================
                        end_pt = end_pt - self.long_seg.normal.p2 * WIN_SIDES_D
                        # ==========================================================================================
                        if start_pt != end_pt:
                            start_ptt, end_pt = DY_segment. \
                                get_p1_p2_from_normal(self.short_seg.normal, start_pt, end_pt)
                            seg3 = DY_segment(start_ptt, end_pt)

                            utl.arrange_hanging_along_seg(seg3, HANGING_CABINET_W[0], start_pt,
                                                          self.ele_list, self.boundary, res_flag)

                        start_pt = win.seg.p2 if win.seg.p1.distance(self.triangle_vertice) \
                                                 < win.seg.p2.distance(self.triangle_vertice) else win.seg.p1
                        # add by lxy
                        # =========================================================================================
                        start_pt = start_pt + self.long_seg.normal.p2 * WIN_SIDES_D
                        # ==========================================================================================
                        end_pt = seg_s.seg.p1 if seg_s.seg.p2 == self.triangle_vertice else seg_s.seg.p2
                        if start_pt != end_pt:
                            start_ptt, end_pt = DY_segment. \
                                get_p1_p2_from_normal(self.short_seg.normal, start_pt, end_pt)
                            seg4 = DY_segment(start_ptt, end_pt)

                            utl.arrange_hanging_along_seg(seg4, HANGING_CABINET_W[0], start_pt,
                                                          self.ele_list, self.boundary, res_flag)

            # 无转角吊柜
            else:
                # 长边有窗户
                if self.long_seg.seg.contains(win.seg):
                    start_pt = self.triangle_vertice
                    end_pt = win.seg.p1 if win.seg.p1.distance(self.triangle_vertice) \
                                           < win.seg.p2.distance(self.triangle_vertice) else win.seg.p2
                    if start_pt != end_pt:
                        start_ptt, end_pt = DY_segment. \
                            get_p1_p2_from_normal(self.long_seg.normal, start_pt, end_pt)
                        seg1 = DY_segment(start_ptt, end_pt)

                        utl.arrange_hanging_along_seg(seg1, HANGING_CABINET_W[0], start_pt,
                                                      self.ele_list, self.boundary, res_flag)

                    start_pt = win.seg.p2 if win.seg.p1.distance(self.triangle_vertice) \
                                             < win.seg.p2.distance(self.triangle_vertice) else win.seg.p1
                    # add by lxy
                    # ===========================================================================================
                    start_pt = start_pt + self.short_seg.normal.p2 * WIN_SIDES_D
                    # ================================================================================
                    end_pt = seg_l.seg.p1 if seg_l.seg.p2 == self.triangle_vertice else seg_l.seg.p2
                    if start_pt != end_pt:
                        start_ptt, end_pt = DY_segment. \
                            get_p1_p2_from_normal(self.long_seg.normal, start_pt, end_pt)
                        seg2 = DY_segment(start_ptt, end_pt)

                        utl.arrange_hanging_along_seg(seg2, HANGING_CABINET_W[0], start_pt,
                                                      self.ele_list, self.boundary, res_flag)

                    start_pt = self.triangle_vertice + self.long_seg.normal.p2 * HANGING_CABINET_L  # 需要考虑拐角处已经布置吊柜，不能重叠！
                    end_pt = ran_bl.seg.p1 if ran_bl.seg.p1.distance(self.triangle_vertice) < \
                                              ran_bl.seg.p2.distance(self.triangle_vertice) else ran_bl.seg.p2
                    if start_pt != end_pt:
                        start_ptt, end_pt = DY_segment. \
                            get_p1_p2_from_normal(self.short_seg.normal, start_pt, end_pt)
                        seg3 = DY_segment(start_ptt, end_pt)

                        utl.arrange_hanging_along_seg(seg3, HANGING_CABINET_W[0], start_pt,
                                                      self.ele_list, self.boundary, res_flag)

                    start_pt = ran_bl.seg.p2 if ran_bl.seg.p1.distance(self.triangle_vertice) < \
                                                ran_bl.seg.p2.distance(self.triangle_vertice) else ran_bl.seg.p1
                    end_pt = seg_s.seg.p1 if seg_s.seg.p2 == self.triangle_vertice else seg_s.seg.p2
                    if start_pt != end_pt:
                        start_ptt, end_pt = DY_segment. \
                            get_p1_p2_from_normal(self.short_seg.normal, start_pt, end_pt)
                        seg4 = DY_segment(start_ptt, end_pt)

                        utl.arrange_hanging_along_seg(seg4, HANGING_CABINET_W[0], start_pt,
                                                      self.ele_list, self.boundary, res_flag)

                # 短边有窗户
                else:
                    start_pt = self.triangle_vertice
                    end_pt = ran_bl.seg.p1 if ran_bl.seg.p1.distance(self.triangle_vertice) \
                                              < ran_bl.seg.p2.distance(self.triangle_vertice) else ran_bl.seg.p2
                    if start_pt != end_pt:
                        start_ptt, end_pt = DY_segment. \
                            get_p1_p2_from_normal(self.long_seg.normal, start_pt, end_pt)
                        seg1 = DY_segment(start_ptt, end_pt)

                        utl.arrange_hanging_along_seg(seg1, HANGING_CABINET_W[0], start_pt,
                                                      self.ele_list, self.boundary, res_flag)

                    start_pt = ran_bl.seg.p2 if ran_bl.seg.p1.distance(self.triangle_vertice) \
                                                < ran_bl.seg.p2.distance(self.triangle_vertice) else ran_bl.seg.p1
                    end_pt = seg_l.seg.p1 if seg_l.seg.p2 == self.triangle_vertice else seg_l.seg.p2
                    if start_pt != end_pt:
                        start_ptt, end_pt = DY_segment. \
                            get_p1_p2_from_normal(self.long_seg.normal, start_pt, end_pt)
                        seg2 = DY_segment(start_ptt, end_pt)

                        utl.arrange_hanging_along_seg(seg2, HANGING_CABINET_W[0], start_pt,
                                                      self.ele_list, self.boundary, res_flag)

                    start_pt = self.triangle_vertice + self.long_seg.normal.p2 * HANGING_CABINET_L  # 同理需要考虑转角处的重叠情况！
                    end_pt = win.seg.p1 if win.seg.p1.distance(self.triangle_vertice) \
                                           < win.seg.p2.distance(self.triangle_vertice) else win.seg.p2
                    # add by lxy
                    # ================================================================================================
                    line_s = start_pt.distance(self.triangle_vertice)
                    line_e = end_pt.distance(self.triangle_vertice)
                    if line_s > line_e:
                        end_pt = start_pt
                    #     ================================================================================================
                    if start_pt != end_pt:
                        start_ptt, end_pt = DY_segment. \
                            get_p1_p2_from_normal(self.short_seg.normal, start_pt, end_pt)
                        seg3 = DY_segment(start_ptt, end_pt)

                        utl.arrange_hanging_along_seg(seg3, HANGING_CABINET_W[0], start_pt,
                                                      self.ele_list, self.boundary, res_flag)

                    start_pt = win.seg.p2 if win.seg.p1.distance(self.triangle_vertice) \
                                             < win.seg.p2.distance(self.triangle_vertice) else win.seg.p1
                    # add by lxy
                    # ===========================================================================================
                    start_pt = start_pt + self.long_seg.normal.p2 * WIN_SIDES_D
                    # ==============================================================================================
                    end_pt = seg_s.seg.p1 if seg_s.seg.p2 == self.triangle_vertice else seg_s.seg.p2
                    if start_pt != end_pt:
                        start_ptt, end_pt = DY_segment. \
                            get_p1_p2_from_normal(self.short_seg.normal, start_pt, end_pt)
                        seg4 = DY_segment(start_ptt, end_pt)

                        utl.arrange_hanging_along_seg(seg4, HANGING_CABINET_W[0], start_pt,
                                                      self.ele_list, self.boundary, res_flag)

        # 窗户不在三角结构内,肯定就需要有转角吊柜
        else:
            if is_hang_corner:
                corner, cor_bl_wall = utl.get_hanging_corner_cabinet(self.long_seg, self.short_seg,
                                                                     self.triangle_vertice, HANGING_BASE_CORNER_LW[0],
                                                                     self.ele_list)
                # 转角吊柜的backline在长边
                if cor_bl_wall == self.long_seg:

                    start_pt = corner.backline.p1
                    end_pt = seg_l.seg.p1 if seg_l.seg.p2 == self.triangle_vertice else seg_l.seg.p2
                    if start_pt != end_pt:
                        start_ptt, end_pt = DY_segment. \
                            get_p1_p2_from_normal(self.long_seg.normal, start_pt, end_pt)
                        seg1 = DY_segment(start_ptt, end_pt)

                        utl.arrange_hanging_along_seg(seg1, HANGING_CABINET_W[0], start_pt,
                                                      self.ele_list, self.boundary, res_flag)

                    start_pt = corner.backline.p2 + corner.backline.normal.p2 * \
                                                    (HANGING_BASE_CORNER_LW[0] + RANGEHOOD_SINK_W)
                    end_pt = seg_s.seg.p2 if seg_s.seg.p1 == self.triangle_vertice else seg_s.seg.p1
                    if start_pt != end_pt:
                        start_ptt, end_pt = DY_segment. \
                            get_p1_p2_from_normal(self.short_seg.normal, start_pt, end_pt)
                        seg2 = DY_segment(start_ptt, end_pt)

                        utl.arrange_hanging_along_seg(seg2, HANGING_CABINET_W[0], start_pt,
                                                      self.ele_list, self.boundary, res_flag)

                # 转角吊柜的backline在短边
                else:
                    start_pt = self.triangle_vertice + corner.backline.normal.p2 * HANGING_BASE_CORNER_LW[0]
                    end_pt = seg_l.seg.p1 if seg_l.seg.p2 == self.triangle_vertice else seg_l.seg.p2
                    if start_pt != end_pt:
                        start_ptt, end_pt = DY_segment. \
                            get_p1_p2_from_normal(self.long_seg.normal, start_pt, end_pt)
                        seg1 = DY_segment(start_ptt, end_pt)

                        utl.arrange_hanging_along_seg(seg1, HANGING_CABINET_W[0], start_pt,
                                                      self.ele_list, self.boundary, res_flag)

                    start_pt = ran_bl.p2 if ran_bl.p1.distance(self.triangle_vertice) < \
                                            ran_bl.p2.distance(self.triangle_vertice) else ran_bl.p1
                    end_pt = seg_s.seg.p1 if seg_s.seg.p2 == self.triangle_vertice else seg_s.seg.p2
                    if start_pt != end_pt:
                        start_ptt, end_pt = DY_segment. \
                            get_p1_p2_from_normal(self.short_seg.normal, start_pt, end_pt)
                        seg2 = DY_segment(start_ptt, end_pt)

                        utl.arrange_hanging_along_seg(seg2, HANGING_CABINET_W[0], start_pt,
                                                      self.ele_list, self.boundary, res_flag)

                    ##############################################4011_L吊柜end##############################################################

    def run4110_U(self):
        door = helpers.get_eles(self.ele_list, Door)
        main_win = helpers.get_eles(self.line_list, Window)
        # self.triangle_vertice = utl.get_triangle_vertice_U(door[0], main_win[0], self.boundary)

        # 得到u0, u1
        u1 = [seg for seg in self.boundary.seg_list
              if seg.line.is_parallel(door[0].backline.normal)]
        for seg in self.boundary.seg_list:
            # if seg.line.is_parallel(door[0].backline.normal):
            #     continue
            if len(door[0].boundary.polygon.intersection(seg.line)) == 0:
                if seg.line.is_parallel(door[0].backline.dir):
                    self.u0 = seg
                    break
        self.triangle_vertice = utl.get__U_triangle_vertice(main_win[0], self.u0)
        for seg in u1:
            if seg.seg.contains(self.triangle_vertice):
                self.u1_tri = seg
            else:
                self.u1_reg = seg

        # utl.arrange_cabinet_along_seg(self.u0, self.triangle_vertice,
        #                               self.ele_list, self.residual_len_table)
        # utl.arrange_hanging_along_seg(self.u1_tri, HANGING_CABINET_W[0],
        #                               self.triangle_vertice,  self.ele_list)

        # 布置三角结构
        # '''U型木作有两个转角地柜，首先布置三角结构的转角地柜，两个转角共用U0'''
        thr = self.u0.seg.length - CABINET_L
        suit_u0_df = self.triangle_long_df. \
            loc[self.triangle_long_df.sum_len <= thr]
        suit_u0_df = suit_u0_df.ix[suit_u0_df.sum_len.idxmax]

        cabinet_wid = suit_u0_df['cabinet_wid']
        corner_wid = suit_u0_df['corner_wid']
        sink_ran_wid = suit_u0_df['sink_ran_wid']
        cor_p1 = self.triangle_vertice
        cor_p2 = cor_p1 + self.u1_tri.normal.p2 * corner_wid

        cab_p1 = cor_p2
        cab_p2 = cab_p1 + self.u1_tri.normal.p2 * cabinet_wid

        sink_p1 = cab_p2
        sink_p2 = sink_p1 + self.u1_tri.normal.p2 * sink_ran_wid
        # '''开始布置厨房组件首先是三角结构的转角地柜'''
        cor_p1, cor_p2 = DY_segment. \
            get_p1_p2_from_normal(self.u0.normal, cor_p1, cor_p2)
        cor_bl1 = DY_segment(cor_p1, cor_p2)
        cor = self.get_U_corner_cabinet_type(cor_bl1, None, CABINET_L)
        self.ele_list.append(cor)
        # '''如果有cabinet就放置'''
        if cabinet_wid != 0:
            cab_p1, cab_p2 = DY_segment. \
                get_p1_p2_from_normal(self.u0.normal, cab_p1, cab_p2)
            cab_bl = DY_segment(cab_p1, cab_p2)
            cab = SingleCabinet(cab_bl, CABINET_L)
            self.ele_list.append(cab)
        # '''布置水槽柜'''
        sink_p11, sink_p22 = DY_segment. \
            get_p1_p2_from_normal(self.u0.normal, sink_p1, sink_p2)
        sink_bl = DY_segment(sink_p11, sink_p22)
        sink = SinkCabinet(sink_bl, CABINET_L)
        self.ele_list.append(sink)
        # '''布置烟机柜'''
        ran_p1 = self.triangle_vertice + self.u0.normal.p2 * CABINET_L
        ran_p2 = ran_p1 + self.u0.normal.p2 * sink_ran_wid
        ran_p11, ran_p22 = DY_segment. \
            get_p1_p2_from_normal(self.u1_tri.normal, ran_p1, ran_p2)
        ran_bl = DY_segment(ran_p11, ran_p22)
        ran = RangehoodCabinet(ran_bl, CABINET_L)
        self.ele_list.append(ran)
        # 补齐三角结构u1边
        start_pt = ran_p2
        u1_tri_res_end_pt = self.u1_tri.seg.p1 if self.u1_tri.seg.p2 == self.triangle_vertice else \
            self.u1_tri.seg.p2
        if start_pt != u1_tri_res_end_pt:
            u1_tri_res_start_pt, u1_tri_res_end_pt = DY_segment. \
                get_p1_p2_from_normal(self.u1_tri.normal, start_pt, u1_tri_res_end_pt)
            u1_tri_res = DY_segment(u1_tri_res_start_pt, u1_tri_res_end_pt)
            utl.arrange_cabinet_along_seg(u1_tri_res, start_pt, self.ele_list,
                                          self.residual_len_table)
        # 布置另一个转角柜---通过u1的长度-冰箱宽度判断，优先更长的转角柜#####优化了此处逻辑
        u1_reg_select = self.u1_reg.seg.length - REFRIGERATOR_W
        if u1_reg_select >= BASE_CORNER_W[-1]:
            corner_wid = BASE_CORNER_W[-1]
        elif u1_reg_select >= BASE_CORNER_W[0] and \
                        u1_reg_select < BASE_CORNER_W[-1]:
            corner_wid = [w for w in BASE_CORNER_W[:-2] if u1_reg_select >= w]
            corner_wid.append(0)
            corner_wid = max(corner_wid)
        cor_p11_ref = self.u0.seg.p1 if self.u0.seg.p2 \
                                        == self.triangle_vertice else self.u0.seg.p2
        cor_p12_ref = cor_p11_ref + self.u0.normal.p2 * corner_wid
        cor_p11, cor_p12 = DY_segment. \
            get_p1_p2_from_normal(self.u1_reg.normal, cor_p11_ref, cor_p12_ref)
        cor_bl2 = DY_segment(cor_p11, cor_p12)
        cor = self.get_U_corner_cabinet_type(cor_bl1, cor_bl2, CABINET_L)
        self.ele_list.append(cor)
        # 补齐u0边
        start_pt = sink_p2
        u0_res_end_pt = cor_p11_ref + self.u1_reg.normal.p2 * CABINET_L
        if start_pt != u0_res_end_pt:
            u0_res_start_pt, u0_res_end_pt = DY_segment. \
                get_p1_p2_from_normal(self.u0.normal, start_pt, u0_res_end_pt)
            u0_res_seg = DY_segment(u0_res_start_pt, u0_res_end_pt)
            utl.arrange_cabinet_along_seg(u0_res_seg, start_pt, self.ele_list,
                                          self.residual_len_table)
        # 布置冰箱
        is_refri, res_end_pt = self.arrange_U_refrigerator()
        # 补齐冰箱u1边
        start_pt = cor_p12_ref
        u1_reg_res_end_pt = res_end_pt
        if start_pt != u1_tri_res_end_pt:
            u1_reg_res_start_pt, u1_reg_res_end_pt = DY_segment. \
                get_p1_p2_from_normal(self.u1_reg.normal, start_pt, u1_reg_res_end_pt)
            u1_reg_res = DY_segment(u1_reg_res_start_pt, u1_reg_res_end_pt)
            utl.arrange_cabinet_along_seg(u1_reg_res, start_pt, self.ele_list,
                                          self.residual_len_table)
        # '''window appears in tri_seg exchange sink and ran'''
        for l in self.line_list:
            if isinstance(l, Window):
                win = l
        if self.u1_tri.seg.contains(win.seg):
            self.ele_list.remove(ran)
            self.ele_list.remove(sink)
            sink_new = RangehoodCabinet(sink_bl, CABINET_L)
            ran_new = SinkCabinet(ran_bl, CABINET_L)
            self.ele_list.append(sink_new)
            self.ele_list.append(ran_new)
        # '''Change the first SingleCabinet to a DrawerCabinet'''
        singlelist = []
        exsist = False
        for e in self.ele_list:
            if isinstance(e, SingleCabinet):
                singlelist.append(e)
                exsist = True
        if exsist:
            self.ele_list.remove(singlelist[0])
            drawcab_new = DrawerCabinet(singlelist[0].backline, CABINET_L)
            self.ele_list.append(drawcab_new)

        ##########################################布置U型吊柜begin###############################################
        # '''first to arrange ranCabinet'''
        for e in self.ele_list:
            if isinstance(e, RangehoodCabinet):
                ran_bl = e.backline
            if isinstance(e, SinkCabinet):
                sink_bl = e.backline
        ranhang = RanHangingCabinet(ran_bl, HANGING_CABINET_L)
        self.ele_list.append(ranhang)
        # '''judge the corner whether it can arrange a cornercabinet or not '''
        is_hanging_tri = utl.is_arrange_hanging_corner(self.u0, self.u1_tri, self.triangle_vertice,
                                                       self.boundary, self.line_list[0], HANGING_BASE_CORNER_LW[0])
        is_hanging_reg = utl.is_arrange_hanging_corner(self.u0, self.u1_reg, cor_p11_ref,
                                                       self.boundary, self.line_list[0], HANGING_BASE_CORNER_LW[0])
        if is_hanging_tri:
            corner_tri, cor_wall_tri = utl.get_hanging_corner_cabinet(self.u0, self.u1_tri, self.triangle_vertice,
                                                                      HANGING_BASE_CORNER_LW[0], self.ele_list)

        if is_hanging_reg:
            corner_reg, cor_wall_reg = utl.get_hanging_corner_cabinet(self.u0, self.u1_reg, cor_p11_ref,
                                                                      HANGING_BASE_CORNER_LW[0], self.ele_list)
        # '''consider them(self.u0,self.u1_tri,self.u1_reg) based on the position of window '''
        win = self.line_list[0]
        res_flag = False
        # 1.for self.u1_tri
        # window here means sink here no consideration about ran segment
        if self.u1_tri.seg.contains(win.seg):
            '''hanging base corner here '''
            if is_hanging_tri:
                start_pt = self.triangle_vertice + self.u0.normal.p2 * HANGING_BASE_CORNER_LW[0]
            else:
                start_pt = self.triangle_vertice + self.u0.normal.p2 * HANGING_CABINET_L
            # start_pt = self.triangle_vertice + self.u0.normal.p2 * HANGING_BASE_CORNER_LW[0]
            end_pt = win.p1 if win.p1.distance(self.triangle_vertice) < \
                               win.p2.distance(self.triangle_vertice) else win.p2
            # add by lxy
            # ==================================================================================================
            line_s = start_pt.distance(self.triangle_vertice)
            line_e = end_pt.distance(self.triangle_vertice)
            if line_s > line_e:
                end_pt = start_pt
            else:
                end_pt = end_pt - self.u0.normal.p2 * WIN_SIDES_D  # win_sides to consider the delta distance
            # 修改函数,函数功能为点到点的距离
            # result = utl.tri_arrange_startp(start_pt, end_pt, self.triangle_long_df)

            # ====================================================================================================
            if start_pt != end_pt:
                start_ptt, end_pt = DY_segment. \
                    get_p1_p2_from_normal(self.u1_tri.normal, start_pt, end_pt)
                seg1 = DY_segment(start_ptt, end_pt)

                utl.arrange_hanging_along_seg(seg1, HANGING_CABINET_W[0], start_pt,
                                              self.ele_list, self.boundary, res_flag)

            start_pt = win.p1 if win.p1.distance(self.triangle_vertice) > \
                                 win.p2.distance(self.triangle_vertice) else win.p2
            start_pt = start_pt + self.u0.normal.p2 * WIN_SIDES_D
            end_pt = self.u1_tri.p1 if self.u1_tri.p2 == self.triangle_vertice \
                else self.u1_tri.p2
            # add by lxy
            #=================================================================================================
            start_result = utl.tri_arrange_startp(start_pt,end_pt,self.triangle_vertice)
            if start_result != True:
                start_pt = win.p1 if win.p1.distance(self.triangle_vertice) > \
                                     win.p2.distance(self.triangle_vertice) else win.p2
            # =================================================================================================
            if start_pt != end_pt:
                start_ptt, end_pt = DY_segment. \
                    get_p1_p2_from_normal(self.u1_tri.normal, start_pt, end_pt)
                seg2 = DY_segment(start_ptt, end_pt)

                utl.arrange_hanging_along_seg(seg2, HANGING_CABINET_W[0], start_pt,
                                              self.ele_list, self.boundary, res_flag)

        # no window means ran here consider it !
        else:
            # '''hanging base corner here '''
            if is_hanging_tri:
                start_pt = self.triangle_vertice + self.u0.normal.p2 * \
                                                   (HANGING_BASE_CORNER_LW[0] + RANGEHOOD_SINK_W)
                end_pt = self.u1_tri.p1 if self.u1_tri.p2 == self.triangle_vertice \
                    else self.u1_tri.p2
                if start_pt != end_pt:
                    start_ptt, end_pt = DY_segment. \
                        get_p1_p2_from_normal(self.u1_tri.normal, start_pt, end_pt)
                    seg1 = DY_segment(start_ptt, end_pt)

                    utl.arrange_hanging_along_seg(seg1, HANGING_CABINET_W[0], start_pt,
                                                  self.ele_list, self.boundary, res_flag)

            else:
                start_pt = self.triangle_vertice
                end_pt = self.triangle_vertice + self.u0.normal.p2 * HANGING_BASE_CORNER_LW[0]
                if start_pt != end_pt:
                    start_ptt, end_pt = DY_segment. \
                        get_p1_p2_from_normal(self.u1_tri.normal, start_pt, end_pt)
                    seg1 = DY_segment(start_ptt, end_pt)

                    utl.arrange_hanging_along_seg(seg1, HANGING_CABINET_W[0], start_pt,
                                                  self.ele_list, self.boundary, res_flag)

                start_pt = self.triangle_vertice + self.u0.normal.p2 * \
                                                   (HANGING_BASE_CORNER_LW[0] + RANGEHOOD_SINK_W)
                end_pt = self.u1_tri.p1 if self.u1_tri.p2 == self.triangle_vertice \
                    else self.u1_tri.p2
                if start_pt != end_pt:
                    start_ptt, end_pt = DY_segment. \
                        get_p1_p2_from_normal(self.u1_tri.normal, start_pt, end_pt)
                    seg2 = DY_segment(start_ptt, end_pt)

                    utl.arrange_hanging_along_seg(seg2, HANGING_CABINET_W[0], start_pt,
                                                  self.ele_list, self.boundary, res_flag)

        # 2.for self.u0
        if self.u0.seg.contains(win.seg):  # sink here absolutely
            if is_hanging_tri:
                start_pt = self.triangle_vertice + self.u1_tri.normal.p2 * HANGING_BASE_CORNER_LW[0]
            else:
                if self.u1_tri.seg.contains(win.seg):#here may not be used
                    start_pt = self.triangle_vertice
                else:
                    start_pt = self.triangle_vertice + self.u1_tri.normal.p2 * HANGING_CABINET_L
            end_pt = win.p1 if win.p1.distance(self.triangle_vertice) < \
                               win.p2.distance(self.triangle_vertice) else win.p2
            line_s = start_pt.distance(self.triangle_vertice)
            line_e = end_pt.distance(self.triangle_vertice)
            if line_s > line_e:
                end_pt = start_pt
            else:
                end_pt = end_pt - self.u1_tri.normal.p2 * WIN_SIDES_D##offset op win
            if start_pt != end_pt:
                start_ptt, end_pt = DY_segment. \
                    get_p1_p2_from_normal(self.u0.normal, start_pt, end_pt)
                seg1 = DY_segment(start_ptt, end_pt)

                utl.arrange_hanging_along_seg(seg1, HANGING_CABINET_W[0], start_pt,
                                              self.ele_list, self.boundary, res_flag)

            start_pt = win.p1 if win.p1.distance(self.triangle_vertice) > \
                                 win.p2.distance(self.triangle_vertice) else win.p2
            # add by lxy
            # =====================================================================================================
            start_pt = start_pt - self.u1_reg.normal.p2 * WIN_SIDES_D
            # ======================================================================================================
            if is_hanging_reg:
                end_pt = cor_p11_ref + self.u1_reg.normal.p2 * HANGING_BASE_CORNER_LW[0]
                # end_pt = end_pt + self.u1_tri.normal.p2 * WIN_SIDES_D
            else:
                end_pt = cor_p11_ref + self.u1_reg.normal.p2 * HANGING_CABINET_L
            if start_pt != end_pt:
                start_ptt, end_pt = DY_segment. \
                    get_p1_p2_from_normal(self.u0.normal, start_pt, end_pt)
                seg2 = DY_segment(start_ptt, end_pt)

                utl.arrange_hanging_along_seg(seg2, HANGING_CABINET_W[0], start_pt,
                                              self.ele_list, self.boundary, res_flag)

        else:
            # '''hanging base corner here '''
            if is_hanging_tri:
                start_pt = self.triangle_vertice + self.u1_tri.normal.p2 * \
                                                   HANGING_BASE_CORNER_LW[0]
            else:
                if self.u1_tri.seg.contains(win.seg):
                    start_pt = self.triangle_vertice
                else:
                    start_pt = self.triangle_vertice + self.u1_tri.normal.p2 * HANGING_CABINET_L
            # just when window is like this that you should consider the ran on self.u0
            if win.wall == self.u1_tri:
                end_pt = ran_bl.p1 if ran_bl.p1.distance(self.triangle_vertice) \
                                      < ran_bl.p2.distance(self.triangle_vertice) else ran_bl.p2
                if start_pt != end_pt:
                    start_ptt, end_pt = DY_segment. \
                        get_p1_p2_from_normal(self.u0.normal, start_pt, end_pt)
                    seg1 = DY_segment(start_ptt, end_pt)

                    utl.arrange_hanging_along_seg(seg1, HANGING_CABINET_W[0], start_pt,
                                                  self.ele_list, self.boundary, res_flag)

                start_pt = ran_bl.p1 if ran_bl.p1.distance(self.triangle_vertice) \
                                        > ran_bl.p2.distance(self.triangle_vertice) else ran_bl.p2
                if is_hanging_reg:
                    end_pt = cor_p11_ref + self.u1_reg.normal.p2 * HANGING_BASE_CORNER_LW[0]
                else:
                    if self.u1_reg.seg.contains(win.seg):
                        end_pt = cor_p11_ref + self.u1_reg.normal.p2 * HANGING_BASE_CORNER_LW[0]
                    else:
                        end_pt = cor_p11_ref
                if start_pt != end_pt:
                    start_ptt, end_pt = DY_segment. \
                        get_p1_p2_from_normal(self.u0.normal, start_pt, end_pt)
                    seg2 = DY_segment(start_ptt, end_pt)

                    utl.arrange_hanging_along_seg(seg2, HANGING_CABINET_W[0], start_pt,
                                                  self.ele_list, self.boundary, res_flag)

            else:  # it means no-consideration about the ran
                if is_hanging_reg:
                    end_pt = cor_p11_ref + self.u1_reg.normal.p2 * HANGING_BASE_CORNER_LW[0]
                else:
                    if self.u1_reg.seg.contains(win.seg):
                        end_pt = cor_p11_ref
                    else:
                        end_pt = cor_p11_ref + self.u1_reg.normal.p2 * HANGING_CABINET_L
                if start_pt != end_pt:
                    start_ptt, end_pt = DY_segment. \
                        get_p1_p2_from_normal(self.u0.normal, start_pt, end_pt)
                    seg1 = DY_segment(start_ptt, end_pt)

                    utl.arrange_hanging_along_seg(seg1, HANGING_CABINET_W[0], start_pt,
                                                  self.ele_list, self.boundary, res_flag)
        # 3.for self.u1_reg, simple for 2 situations
        if self.u1_reg.seg.contains(win.seg):
            if is_hanging_reg:
                start_pt = cor_p11_ref + self.u0.normal.p2 * HANGING_BASE_CORNER_LW[0]
            else:
                start_pt = cor_p11_ref + self.u0.normal.p2 * HANGING_CABINET_L
            end_pt = win.p1 if win.p1.distance(cor_p11_ref) < \
                               win.p2.distance(cor_p11_ref) else win.p2
            if start_pt != end_pt:
                start_ptt, end_pt = DY_segment. \
                    get_p1_p2_from_normal(self.u1_reg.normal, start_pt, end_pt)
                seg1 = DY_segment(start_ptt, end_pt)

                utl.arrange_hanging_along_seg(seg1, HANGING_CABINET_W[0], start_pt,
                                              self.ele_list, self.boundary, res_flag)
            start_pt = win.p1 if win.p1.distance(cor_p11_ref) > \
                                 win.p2.distance(cor_p11_ref) else win.p2
            # add by lxy
            # ===============================================================================
            start_pt = start_pt + self.u0.normal.p2 * WIN_SIDES_D
            # ===============================================================================
            end_pt = res_end_pt
            if start_pt != end_pt:
                start_ptt, end_pt = DY_segment. \
                    get_p1_p2_from_normal(self.u1_reg.normal, start_pt, end_pt)
                seg2 = DY_segment(start_ptt, end_pt)
                utl.arrange_hanging_along_seg(seg2, HANGING_CABINET_W[0], start_pt,
                                              self.ele_list, self.boundary, res_flag)

        else:
            if is_hanging_reg:
                start_pt = cor_p11_ref + self.u0.normal.p2 * HANGING_BASE_CORNER_LW[0]
            else:
                start_pt = cor_p11_ref
            # start_pt = cor_p11_ref + self.u0.normal.p2 * HANGING_BASE_CORNER_LW[0]
            end_pt = res_end_pt
            if start_pt != end_pt:
                start_ptt, end_pt = DY_segment. \
                    get_p1_p2_from_normal(self.u1_reg.normal, start_pt, end_pt)
                seg1 = DY_segment(start_ptt, end_pt)
                utl.arrange_hanging_along_seg(seg1, HANGING_CABINET_W[0], start_pt,
                                              self.ele_list, self.boundary, res_flag)
            pass
        ##########################################布置U型吊柜end###############################################


        ##########################################布置"一"字型吊柜start###############################################
    def run4101_4200_4210_O(self):
        #find the wall that can be use as one_type position
        if self.l < RANGEHOOD_SINK_W * 2 + SINGLE_CABINET_W[0]:
            raise Exception("warning:厨房功能区最基本长度不足")
        door = helpers.get_eles(self.ele_list, Door)
        for dr_connect in DOOR_CONNECT:
            for dr in door:
                if dr_connect in dr.connect_list:#balcony 阳台
                    door_out = dr
                else:
                    door_in = dr
        self.triangle_vertice = utl.get_triangle_vertice(door_in, self.boundary)#需要甄别两个门
        border_flag = False
        if self.doors > 1:
            tmp_seg = DY_segment(door_out.backline.normal.p1, door_out.backline.normal.p2)
            parallel_dr = helpers.get_paralleled_line(tmp_seg, door_out.boundary, type=DY_segment)
            d0 = parallel_dr[0].line.distance(self.triangle_vertice)
            d1 = parallel_dr[1].line.distance(self.triangle_vertice)
            if min(d0, d1) < CABINET_L:
                raise Exception("warning:当前特殊户型需要单独处理")
            else:
                self.O0 = [s for s in self.boundary.seg_list if s.seg.contains(self.triangle_vertice) \
                           and not door_out.boundary.polygon.intersection(s.seg)][0]
        else:
            for b in self.line_list:
                if isinstance(b, Border):
                    border = b
                    border_flag = True
                    break
            if border_flag:
                self.O0 = [s for s in self.boundary.seg_list if s.seg.contains(self.triangle_vertice) \
                           and s.seg.length == self.l][0]
            else:
                return False
        # if border_flag:
        for seg in self.boundary.seg_list:
            # if seg.seg.length == self.l and seg.seg.contains(self.triangle_vertice):
            #     self.O0 = seg
            if seg.seg.length == self.w and seg.seg.contains(self.triangle_vertice):
                self.short_seg = seg
                break
        # 判断边是否撞门
        p1 = self.triangle_vertice + self.O0.normal.p2 * CABINET_L
        p2 = p1 + self.short_seg.normal.p2 * 1
        cabinet_seg = DY_segment(p1, p2)
        inter_pt = helpers.get_points_seg_intersect_boundary(cabinet_seg, door_in.boundary)
        # 如果撞门，更新长边!并判断长边是否满足厨房基本三样（洗/切/炒）
        if len(inter_pt) != 0:
            l1 = DY_segment(p1, inter_pt[0])
            l2 = DY_segment(p1, inter_pt[1])
            l_length = min(l1.seg.length, l2.seg.length)
            self.l = l_length
            longsegp1, longsegp2 = DY_segment.get_p1_p2_from_normal(
                self.O0.normal,
                self.triangle_vertice,
                self.triangle_vertice + self.short_seg.normal.p2 * self.l)
            self.O0 = DY_segment(longsegp1, longsegp2)
            # if l_length < self.w:
            #     self.l, self.w = self.w, self.l
            #     self.long_seg, self.short_seg = self.short_seg, self.long_seg
            if self.l < RANGEHOOD_SINK_W * 2 + SINGLE_CABINET_W[0]:
                raise Exception("warning:厨房功能区最基本长度不足")

        thr = self.O0.seg.length
        # suit_O0_df = self.triangle_long_df. \
        #     loc[self.triangle_long_df.sum_len <= thr]
        # suit_O0_df = suit_O0_df.ix[suit_O0_df.sum_len.idxmax]
        #
        # corner_wid = suit_O0_df['corner_wid']
        # cabinet_wid = suit_O0_df['cabinet_wid']
        # sink_ran_wid = suit_O0_df['sink_ran_wid']
        # To begin the layout
        ran_p1 = self.triangle_vertice
        ran_p2 = ran_p1 + self.short_seg.normal.p2 * RANGEHOOD_SINK_W

        cab_p1 = ran_p2
        cab_p2 = cab_p1 + self.short_seg.normal.p2 * SINGLE_CABINET_W[0]
        cabinet_flag = False

        sink_p1 = cab_p2
        sink_p2 = sink_p1 + self.short_seg.normal.p2 * RANGEHOOD_SINK_W

        #put the ran, cabinet, sink and if res exists then consider put a refrigerator
        ran_p11, ran_p22 = DY_segment. \
            get_p1_p2_from_normal(self.O0.normal, ran_p1, ran_p2)
        ran_bl = DY_segment(ran_p11, ran_p22)
        ran = RangehoodCabinet(ran_bl, CABINET_L)
        self.ele_list.append(ran)

        if cab_p1 != cab_p2:
            cab_p1, cab_p2 = DY_segment. \
                get_p1_p2_from_normal(self.O0.normal, cab_p1, cab_p2)
            cab_bl = DY_segment(cab_p1, cab_p2)
            cab = DrawerCabinet(cab_bl, CABINET_L)
            self.ele_list.append(cab)
            cabinet_flag = True

        else:
            drawer_p1 = ran_p2
            drawer_p2 = drawer_p1 + self.short_seg.normal.p2 * SINGLE_CABINET_W[0]
            drawer_p11, drawer_p22 = DY_segment.\
                get_p1_p2_from_normal(self.O0.normal, drawer_p1, drawer_p2)
            drawer_bl = DY_segment(drawer_p11, drawer_p22)
            drawer_cab = DrawerCabinet(drawer_bl, CABINET_L)
            self.ele_list.append(drawer_cab)

        if cabinet_flag:
            if sink_p1 != sink_p2:

                sink_p11, sink_p22 = DY_segment. \
                    get_p1_p2_from_normal(self.O0.normal, sink_p1, sink_p2)
                sink_bl = DY_segment(sink_p11, sink_p22)
                sink = SinkCabinet(sink_bl, CABINET_L)
                self.ele_list.append(sink)
        else:
            sink_p1 = self.triangle_vertice + self.short_seg.normal.p2 * \
                                              (RANGEHOOD_SINK_W + SINGLE_CABINET_W[0])
            sink_p2 = sink_p1 + self.short_seg.normal.p2 * RANGEHOOD_SINK_W
            sink_p11, sink_p22 = DY_segment. \
                get_p1_p2_from_normal(self.O0.normal, sink_p1, sink_p2)
            sink_bl = DY_segment(sink_p11, sink_p22)
            sink = SinkCabinet(sink_bl, CABINET_L)
            self.ele_list.append(sink)
        res = thr - RANGEHOOD_SINK_W * 2 - SINGLE_CABINET_W[0]
        refrige_flag = False
        if res >= REFRIGERATOR_W:
            refrige_flag = True
            refri_p1 = self.O0.seg.p1 if self.O0.seg.p2 == self.triangle_vertice else self.O0.seg.p2
            refri_p2 = refri_p1 + self.short_seg.normal.p2 * (-1) * REFRIGERATOR_W

            refri_p11, refri_p22 = DY_segment. \
                get_p1_p2_from_normal(self.O0.normal, refri_p1, refri_p2)
            refri_bl = DY_segment(refri_p11, refri_p22)
            refrige = Refrigerator(refri_bl, CABINET_L)
            self.ele_list.append(refrige)
            #fill in
            start_pt = sink_p2
            end_pt = refri_p2
            if start_pt != end_pt:
                res_start_pt, res_end_pt = DY_segment. \
                    get_p1_p2_from_normal(self.O0.normal, start_pt, end_pt)
                res_seg = DY_segment(res_start_pt, res_end_pt)
                utl.arrange_cabinet_along_seg(res_seg, start_pt, self.ele_list,
                                              self.residual_len_table)
        else:
            # fill in
            start_pt = sink_p2
            end_pt = start_pt + self.short_seg.normal.p2 * res
            if start_pt != end_pt:
                res_start_pt, res_end_pt = DY_segment. \
                    get_p1_p2_from_normal(self.O0.normal, start_pt, end_pt)
                res_seg = DY_segment(res_start_pt, res_end_pt)
                utl.arrange_cabinet_along_seg(res_seg, start_pt, self.ele_list,
                                              self.residual_len_table)
            # consider put the refrigerator on door_wall if door_wall is_parallel border else not
            # if res >= CABINET_L and res < REFRIGERATOR_W:
            #     dis0, dis1, dis2, dis3 = utl.get_doorbackline_wall_dis(self.boundary, door[0], None)
            #     if max(dis0, dis1) > CABINET_L + REFRIGERATOR_W:
            #         refri_p1 = sink_p2 + self.short_seg.normal.p2 * res + \
            #                    self.O0.normal.p2 * (CABINET_L + REFRIGERATOR_W)
            #         refri_p2 = refri_p1 + self.O0.normal.p2 * REFRIGERATOR_W
            #
            #         refri_p11, refri_p22 = DY_segment. \
            #             get_p1_p2_from_normal(self.short_seg.normal * (-1), refri_p1, refri_p2)
            #         refri_bl = DY_segment(refri_p11, refri_p22)
            #         refrige = Refrigerator(refri_bl, CABINET_L)
            #         self.ele_list.append(refrige)
###################################################hanging zone########################################################
        #put ran hanging first
        for e in self.ele_list:
            if isinstance(e, RangehoodCabinet):
                ran_bl = e.backline
                break
            # if isinstance(e, SinkCabinet):
            #     sink_bl = e.backline
        ranhanging = RanHangingCabinet(ran_bl, HANGING_CABINET_L)
        self.ele_list.append(ranhanging)
        res_flag = False
        #fill in the hanging res
        start_pt = self.triangle_vertice + self.short_seg.normal.p2 * RANGEHOOD_SINK_W
        end_pt = self.triangle_vertice + self.short_seg.normal.p2 * (self.l - REFRIGERATOR_W) \
            if refrige_flag else  self.triangle_vertice + self.short_seg.normal.p2 * self.l
        if start_pt != end_pt:
            start_ptt, end_pt = DY_segment. \
                get_p1_p2_from_normal(self.O0.normal, start_pt, end_pt)
            seg_hang = DY_segment(start_ptt, end_pt)

            utl.arrange_hanging_along_seg(seg_hang, HANGING_CABINET_W[1], start_pt,
                                          self.ele_list, self.boundary, res_flag)
    def run4101_4200_4210_P(self):
        if not D1_MIN <= self.l <= D1_MAX:
            raise Exception ("warning:厨房功能区最基本长度不足")
        door = helpers.get_eles(self.ele_list,Door)
        border_flag = False
        for dr in door:
            if 'balcony' in dr.connect_list:
                door_out = dr
            else:
                door_in = dr
        if self.doors > 1:
            pass
        else:
            for b in self.line_list:
                if isinstance(b, Border):
                    border = b
                    border_flag = True
                    break
            if border_flag:

                for seg in self.boundary.seg_list:
                    if (seg.seg.contains(door_in.backline.p1) and seg.seg.contains(door_in.backline.p2)) and door_in.backline.line.is_parallel(border.line) and \
                        seg.seg.length == self.w:
                        self.door_seg = seg
                        break
                for seg in self.boundary.seg_list:
                    if door_in.door_body.normal.p2 == seg.normal.p2 * (-1) and seg.seg.length == self.l:
                        self.p1_reg_seg = seg
                        break
        #与门的door_body法线平行且反向的边布置冰箱与水槽柜
        dr_center = door_in.boundary.polygon.centroid
        d = CROSS_D
        res_len = self.l - REFRIGERATOR_W - RANGEHOOD_SINK_W - SINGLE_CABINET_W[0]
        if res_len < SINK_RANK_MIN:
            raise Exception("warning:厨房功能区最基本长度不足")
        elif res_len > REF_SINK_MAX:
            res = REF_SINK_MAX
        elif  SINK_RANK_MIN < res_len < REF_SINK_MAX:
            res = res_len
        refri_p1 = self.p1_reg_seg.p1 if self.p1_reg_seg.p1.distance(dr_center) < self.p1_reg_seg.p2.distance(dr_center) \
            else self.p1_reg_seg.p2
        refri_p2 = refri_p1 + self.door_seg.normal.p2 * REFRIGERATOR_W
        refri_p11, refri_p22 = DY_segment. \
            get_p1_p2_from_normal(self.p1_reg_seg.normal, refri_p1, refri_p2)
        refri_bl = DY_segment(refri_p11, refri_p22)
        refrige = Refrigerator(refri_bl, CABINET_L)
        self.ele_list.append(refrige)
        # 布置水槽柜
        sink_p1 = refri_p2 + self.door_seg.normal.p2 * res
        sink_p2 = sink_p1 + self.door_seg.normal.p2 * RANGEHOOD_SINK_W
        sink_p11, sink_p22 = DY_segment. \
            get_p1_p2_from_normal(self.p1_reg_seg.normal, sink_p1, sink_p2)
        sink_bl = DY_segment(sink_p11, sink_p22)
        sink = SinkCabinet(sink_bl, CABINET_L)
        self.ele_list.append(sink)

        if res >= SINGLE_CABINET_W[0]:
            for i, l in enumerate(SINGLE_CABINET_W[::-1]):
                if float(res) / float(l) >= 1.:
                    idx = i
                    break
            idx = len(SINGLE_CABINET_W) - 1 - idx
            cab_p1 = sink_p1
            cab_p2 = cab_p1 + self.door_seg.normal.p2 * (-1) * SINGLE_CABINET_W[idx]
            cab_p1, cab_p2 = DY_segment. \
                get_p1_p2_from_normal(self.p1_reg_seg.normal, cab_p1, cab_p2)
            cab_bl = DY_segment(cab_p1, cab_p2)
            cab = SingleCabinet(cab_bl, CABINET_L)
            self.ele_list.append(cab)
        else:
            pass

        #补齐p1_reg_seg剩余边
        start_pt = sink_p2
        end_pt = self.p1_reg_seg.p2 if self.p1_reg_seg.p2.distance(dr_center) > \
            self.p1_reg_seg.p1.distance(dr_center) else self.p1_reg_seg.p1
        p1_reg_rest = start_pt.distance(end_pt)
        if start_pt != end_pt:
            res_start_pt, res_end_pt = DY_segment. \
                get_p1_p2_from_normal(self.p1_reg_seg.normal, start_pt, end_pt)
            res_seg = DY_segment(res_start_pt, res_end_pt)
            utl.arrange_cabinet_along_seg(res_seg, start_pt, self.ele_list,
                                          self.residual_len_table)
        #布置p2_rank_seg
        for seg in self.boundary.seg_list:
            if seg.line.is_parallel(self.door_seg.normal) and seg is not self.p1_reg_seg:
                self.p2_rank_seg = seg

        x_seg = DY_segment(Point(0, 0), Point(1, 0))
        y_seg = DY_segment(Point(0, 0), Point(0, 1))
        if SINK_RANK_MIN < p1_reg_rest < SINK_RANK_MAX:
            d = p1_reg_rest
        elif p1_reg_rest > SINK_RANK_MAX:
            d = SINK_RANK_MAX
        elif p1_reg_rest < SINK_RANK_MIN:
            d = -SINK_RANK_MIN
        if self.p2_rank_seg.line.is_parallel(y_seg.line):
            rank_y = (sink_p2 + self.door_seg.normal.p2 * d).y if sink_p2.distance(dr_center) \
                > sink_p1.distance(dr_center) else (sink_p1 + self.door_seg.normal.p2 * d).y
            rank_x = self.p2_rank_seg.p1.x
            rank_p1 = Point(rank_x, rank_y)
            rank_p2 = rank_p1 + self.door_seg.normal.p2 * (-1) * RANGEHOOD_SINK_W
        elif self.p2_rank_seg.line.is_parallel(x_seg.line):
            rank_y = self.p2_rank_seg.p1.y
            rank_x = (sink_p2 + self.door_seg.normal.p2 * d).x if sink_p2.distance(dr_center) \
                > sink_p1.distance(dr_center) else (sink_p1 + self.door_seg.normal.p2 * d).x
            rank_p1 = Point(rank_x, rank_y)
            rank_p2 = rank_p1 + self.door_seg.normal.p2 * (-1) * RANGEHOOD_SINK_W
        start_pt = self.p2_rank_seg.p2 if self.p2_rank_seg.p2.distance(dr_center) > \
                                          self.p2_rank_seg.p1.distance(dr_center) else self.p2_rank_seg.p1
        end_pt = rank_p1 if rank_p1.distance(dr_center) > rank_p2.distance(dr_center) \
            else rank_p2
        if start_pt != end_pt:
            # 根据布置地柜的尺寸确定烟机柜向下移动的距离,防止在阳台方向布置拉篮或者调节板
            if 0 < start_pt.distance(end_pt) <= SINGLE_CABINET_W[0]:
                rank_p1 = rank_p1 + self.door_seg.normal.p2 * (-1) * (SINGLE_CABINET_W[0] - start_pt.distance(end_pt))
                rank_p2 = rank_p1 + self.door_seg.normal.p2 * (-1) * RANGEHOOD_SINK_W
            elif  SINGLE_CABINET_W[0] <= start_pt.distance(end_pt) < SINGLE_CABINET_W[1]:
                rank_p1 = rank_p1 + self.door_seg.normal.p2 * (-1) * (SINGLE_CABINET_W[1] - start_pt.distance(end_pt))
                rank_p2 = rank_p1 + self.door_seg.normal.p2 * (-1) * RANGEHOOD_SINK_W
            elif SINGLE_CABINET_W[1] <= start_pt.distance(end_pt) < SINGLE_CABINET_W[2]:
                rank_p1 = rank_p1 + self.door_seg.normal.p2 * (-1) * (SINGLE_CABINET_W[2] - start_pt.distance(end_pt))
                rank_p2 = rank_p1 + self.door_seg.normal.p2 * (-1) * RANGEHOOD_SINK_W
            elif SINGLE_CABINET_W[2] <= start_pt.distance(end_pt) < SINGLE_CABINET_W[3]:
                rank_p1 = rank_p1 + self.door_seg.normal.p2 * (-1) * (SINGLE_CABINET_W[3] - start_pt.distance(end_pt))
                rank_p2 = rank_p1 + self.door_seg.normal.p2 * (-1) * RANGEHOOD_SINK_W
            else:
                raise Exception("warning:厨房功能区长度不满足要求")
            cab_p1 = start_pt
            cab_p2 = rank_p1
            cab_p1, cab_p2 = DY_segment. \
                get_p1_p2_from_normal(self.p2_rank_seg.normal, cab_p1, cab_p2)
            cab_bl = DY_segment(cab_p1, cab_p2)
            cab = SingleCabinet(cab_bl, CABINET_L)
            self.ele_list.append(cab)
        # 放置烟机柜
        ran_p11, ran_p22 = DY_segment. \
            get_p1_p2_from_normal(self.p2_rank_seg.normal, rank_p1, rank_p2)
        ran_bl = DY_segment(ran_p11, ran_p22)
        ran = RangehoodCabinet(ran_bl, CABINET_L)
        self.ele_list.append(ran)

        start_pt = rank_p2 if rank_p2.distance(dr_center) < rank_p1.distance(dr_center) \
            else rank_p1
        end_pt = self.p2_rank_seg.p1 if self.p2_rank_seg.p1.distance(dr_center) < self.p2_rank_seg.p2.distance(
            dr_center) \
            else self.p2_rank_seg.p2
        if start_pt != end_pt:
            if start_pt != end_pt:
                res_start_pt, res_end_pt = DY_segment. \
                    get_p1_p2_from_normal(self.p2_rank_seg.normal, start_pt, end_pt)
                res_seg = DY_segment(res_start_pt, res_end_pt)
                utl.arrange_cabinet_along_seg(res_seg, start_pt, self.ele_list,
                                              self.residual_len_table)
        # 将第一个地柜替换成抽屉地柜
        singlelist = []
        exsist = False
        for e in self.ele_list:
            if isinstance(e, SingleCabinet):
                singlelist.append(e)
                exsist = True
        if exsist:
            self.ele_list.remove(singlelist[0])
            drawcab_new = DrawerCabinet(singlelist[0].backline, CABINET_L)
            self.ele_list.append(drawcab_new)
        ########################################布置吊柜################################################################
        # 首先布置烟机吊柜
        for e in self.ele_list:
            if isinstance(e, RangehoodCabinet):
                ran_bl = e.backline
                break
        ranhanging = RanHangingCabinet(ran_bl, HANGING_CABINET_L)
        self.ele_list.append(ranhanging)
        res_flag = False
        start_pt = refri_p2
        end_pt = self.p1_reg_seg.p1 if self.p1_reg_seg.p1.distance(dr_center) > self.p1_reg_seg \
            .p2.distance(dr_center) else self.p1_reg_seg.p2

        if start_pt != end_pt:
            start_ptt, end_pt = DY_segment. \
                get_p1_p2_from_normal(self.p1_reg_seg.normal, start_pt, end_pt)
            seg_hang = DY_segment(start_ptt, end_pt)
            # HANGING_CABINET_W[1]在给arrange_hanging_along_seg函数传参时吊柜的长度尽量与地柜持平或保持倍数关系
            utl.arrange_hanging_along_seg(seg_hang, HANGING_CABINET_W[1], start_pt,
                                          self.ele_list, self.boundary, res_flag)

        start_pt = rank_p2
        end_pt = self.p2_rank_seg.p1 if self.p2_rank_seg.p1.distance(dr_center) < self.p2_rank_seg \
            .p2.distance(dr_center) else self.p2_rank_seg.p2
        if start_pt != end_pt:
            start_ptt, end_pt = DY_segment. \
                get_p1_p2_from_normal(self.p2_rank_seg.normal, start_pt, end_pt)
            ran_hang = DY_segment(start_ptt, end_pt)

            utl.arrange_hanging_along_seg(ran_hang, HANGING_CABINET_W[1], start_pt,
                                          self.ele_list, self.boundary, res_flag)

        start_pt = rank_p1
        end_pt = self.p2_rank_seg.p2 if self.p2_rank_seg.p2.distance(dr_center) > self.p2_rank_seg \
            .p1.distance(dr_center) else self.p2_rank_seg.p1
        if start_pt != end_pt:
            start_ptt, end_pt = DY_segment. \
                get_p1_p2_from_normal(self.p2_rank_seg.normal, start_pt, end_pt)
            ran_hang = DY_segment(start_ptt, end_pt)

            utl.arrange_hanging_along_seg(ran_hang, HANGING_CABINET_W[0], start_pt,
                                          self.ele_list, self.boundary, res_flag)

    def run4110_small(self):
        door = helpers.get_eles(self.ele_list, Door)
        door_out_res = False
        for dr_connect in DOOR_CONNECT:
            for dr in door:
                if dr_connect in dr.connect_list:  # balcony 阳台
                    door_out = dr
                    door_out_res = True
                else:
                    door_in = dr
        dr_center = door_in.boundary.polygon.centroid
        backline_list = utl.door_backline_boundary(door_in, self.boundary)
        if door_out_res:
            backline_list = utl.door_backline_boundary(door_out, self.boundary)
        O1 = [s for s in self.boundary.seg_list if s.seg.length == self.l]
        if len(O1) == 2:
            if O1[0].seg.distance(dr_center) >= O1[1].seg.distance(dr_center):
                self.O1 = O1[0]
            else:
                self.O1 = O1[1]
        else:
            self.O1 = O1[0]
        short_seg_list = helpers.get_adjacent_bounds(self.O1, self.boundary)
        dis0 = short_seg_list[0].seg.distance(dr_center)
        dis1 = short_seg_list[1].seg.distance(dr_center)
        if dis0 > dis1:
            self.short_seg = short_seg_list[0]
        else:
            self.short_seg = short_seg_list[1]
        border_line = [b for b in self.line_list if isinstance(b, Border)]
        border_flag = False
        if border_line != []:
            border_line = border_line[0]
            border_flag = True
        for e in backline_list:
            if border_flag:
                if (self.O1.seg.contains(border_line.seg.p1) and self.O1.seg.contains(border_line.seg.p2)) or \
                        (self.O1.seg.contains(e.p1) and self.O1.seg.contains(e.p2)):
                    for seg in self.boundary.seg_list:
                        if seg.line.is_parallel(self.O1.line) and seg is not self.O1.seg:
                            self.O1 = seg
                    for e in backline_list:
                        if (self.O1.seg.contains(border_line.seg.p1) and self.O1.seg.contains(border_line.seg.p2)) or \
                            (self.O1.seg.contains(e.p1) and self.O1.seg.contains(e.p2)):
                            temp0 = self.O1
                            temp1 = self.short_seg
                            self.short_seg = temp0
                            self.O1 = temp1
                            short_list = []
                            for seg in self.boundary.seg_list:
                               if seg.line.is_parallel(self.short_seg.line):
                                   short_list.append(seg)
                            dis0 = short_list[0].seg.distance(dr_center)
                            dis1 = short_list[1].seg.distance(dr_center)
                            if dis0 > dis1:
                                self.short_seg = short_list[0]
                            else:
                                self.short_seg = short_list[1]
            else:
                if self.O1.seg.contains(e.p1) and self.O1.seg.contains(e.p2):
                    for seg in self.boundary.seg_list:
                        if seg.line.is_parallel(self.O1.line) and seg is not self.O1.seg:
                            self.O1 = seg
                    for e in backline_list:
                        if self.O1.seg.contains(e.p1) and self.O1.seg.contains(e.p2):
                            temp0 = self.O1
                            temp1 = self.short_seg
                            self.short_seg = temp0
                            self.O1 = temp1
                            short_list = []
                            for seg in self.boundary.seg_list:
                                if seg.line.is_parallel(self.short_seg.line):
                                    short_list.append(seg)
                            dis0 = short_list[0].seg.distance(dr_center)
                            dis1 = short_list[1].seg.distance(dr_center)
                            if dis0 > dis1:
                                self.short_seg = short_list[0]
                            else:
                                self.short_seg = short_list[1]
                        else:
                            pass

        SINK_W = RANGEHOOD_SINK_W  # 自定义水槽长度,避免与烟机重合,小户型厨房放不下水槽时,水槽的长度为0
        single_cabinet_w = SINGLE_CABINET_W
        ref_flag = False
        if self.O1.seg.length < RANGEHOOD_SINK_W * 2:
            SINK_W = 0
            single_cabinet_w = (0, )
        elif self.O1.seg.length >= RANGEHOOD_SINK_W * 2 and self.O1.seg.length < RANGEHOOD_SINK_W * 2 + SINGLE_CABINET_W[0]:
            single_cabinet_w = (0, )
        elif self.O1.seg.length >= RANGEHOOD_SINK_W * 2 + SINGLE_CABINET_W[0] + REFRIGERATOR_W:
            ref_flag = True
        nor = self.O1.normal  # 修正法线
        if ref_flag:
            ref_p1 = self.O1.seg.p1 if self.O1.seg.p1.distance(dr_center) < self.O1.seg.p2.distance(dr_center) \
                else self.O1.seg.p2
            ref_p2 = ref_p1 + self.short_seg.normal.p2 * (-1) * REFRIGERATOR_W
            refri_p11, refri_p22 = DY_segment.get_p1_p2_from_normal(self.O1.normal, ref_p1, ref_p2)
            refri_bl = DY_segment(refri_p11, refri_p22)
            refrige = Refrigerator(refri_bl, CABINET_L)
            self.ele_list.append(refrige)
            tri = self.O1.seg.p1 if self.O1.seg.p1.distance(dr_center) > self.O1.seg.p2.distance(dr_center) \
                else self.O1.seg.p2
            self.O1 = DY_segment(
                tri,
                tri + self.short_seg.normal.p2 * (self.l - REFRIGERATOR_W)
            )
            self.O1.normal = nor  # 修正normal与原长边法线一致

        ran_p1 = self.O1.seg.p1 if self.O1.seg.p1.distance(dr_center) > self.O1.seg.p2.distance(dr_center) \
                else self.O1.seg.p2
        ran_p2 = ran_p1 + self.short_seg.normal.p2 * RANGEHOOD_SINK_W
        ran_p11, ran_p22 = DY_segment. \
            get_p1_p2_from_normal(self.O1.normal, ran_p1, ran_p2)
        ran_bl = DY_segment(ran_p11, ran_p22)
        ran = RangehoodCabinet(ran_bl, CABINET_L)
        self.ele_list.append(ran)

        cab_p1 = ran_p2
        cab_p2 = cab_p1 + self.short_seg.normal.p2 * single_cabinet_w[0]
        if cab_p1 != cab_p2:
            cab_p11, cab_p22 = DY_segment. \
                get_p1_p2_from_normal(self.O1.normal, cab_p1, cab_p2)
            cab_bl = DY_segment(cab_p11, cab_p22)
            cab = SingleCabinet(cab_bl, CABINET_L)
            self.ele_list.append(cab)
        sink_p1 = cab_p2
        sink_p2 = sink_p1 + self.short_seg.normal.p2 * SINK_W
        if sink_p1 != sink_p2:
            sink_p11, sink_p22 = DY_segment. \
                get_p1_p2_from_normal(self.O1.normal, sink_p1, sink_p2)
            sink_bl = DY_segment(sink_p11, sink_p22)
            sink = SinkCabinet(sink_bl, CABINET_L)
            self.ele_list.append(sink)
        start_pt = sink_p2
        end_pt = self.O1.seg.p1 if self.O1.seg.p1.distance(dr_center) < self.O1.seg.p2.distance(dr_center) \
                else self.O1.seg.p2
        if start_pt != end_pt:
            res_start_pt, res_end_pt = DY_segment. \
                get_p1_p2_from_normal(self.O1.normal, start_pt, end_pt)
            res_seg = DY_segment(res_start_pt, res_end_pt)
            utl.arrange_cabinet_along_seg(res_seg, start_pt, self.ele_list,
                                          self.residual_len_table)
        singlelist = []
        exsist = False
        for e in self.ele_list:
            if isinstance(e, SingleCabinet):
                singlelist.append(e)
                exsist = True
        if exsist:
            self.ele_list.remove(singlelist[0])
            drawcab_new = DrawerCabinet(singlelist[0].backline, CABINET_L)
            self.ele_list.append(drawcab_new)
            ##################################################布置吊柜################################################
        for e in self.ele_list:
            if isinstance(e, RangehoodCabinet):
                ran_bl = e.backline
                break
        ranhanging = RanHangingCabinet(ran_bl, HANGING_CABINET_L)
        self.ele_list.append(ranhanging)
        win_flag = False
        for l in self.line_list:
            if isinstance(l, Window):
                win = l
                win_flag = True
        if win_flag:
            if self.O1.seg.contains(win.seg):
                if ran_bl.seg.contains(win.seg.p1) or ran_bl.seg.contains(win.seg.p2):
                    start_pt = win.seg.p1 if win.seg.p1.distance(dr_center) < win.seg.p2.distance \
                        (dr_center) else win.seg.p2
                    start_pt = start_pt + self.short_seg.normal.p2 * WIN_SIDES_D
                    end_pt = self.O1.seg.p2 if self.O1.seg.p2.distance(dr_center) < self.O1.seg.p1.distance(dr_center) \
                         else self.O1.seg.p1
                    if start_pt != end_pt:
                        start_ptt, end_pt = DY_segment. \
                            get_p1_p2_from_normal(self.O1.normal, start_pt, end_pt)
                        seg_hang = DY_segment(start_ptt, end_pt)
                        utl.arrange_hanging_along_seg(seg_hang, HANGING_CABINET_W[0], start_pt,
                                                      self.ele_list, self.boundary)
                else:
                    start_pt = ran_p2
                    end_pt = win.seg.p2 if win.seg.p2.distance(dr_center) > win.seg.p1.distance \
                        (dr_center) else win.seg.p1
                    end_pt = end_pt + self.short_seg.normal.p2 * WIN_SIDES_D
                    if start_pt != end_pt:
                        start_ptt, end_pt = DY_segment. \
                            get_p1_p2_from_normal(self.O1.normal, start_pt, end_pt)
                        seg_hang = DY_segment(start_ptt, end_pt)
                        utl.arrange_hanging_along_seg(seg_hang, HANGING_CABINET_W[0], start_pt,
                                                      self.ele_list, self.boundary)
                    start_pt = win.seg.p1 if win.seg.p1.distance(dr_center) < win.seg.p2.distance \
                        (dr_center) else win.seg.p2
                    start_pt = start_pt + self.short_seg.normal.p2 * WIN_SIDES_D
                    end_pt = self.O1.seg.p2 if self.O1.seg.p2.distance(dr_center) < self.O1.seg.p1.distance(dr_center) \
                        else self.O1.seg.p1
                    if start_pt != end_pt:
                        start_ptt, end_pt = DY_segment. \
                            get_p1_p2_from_normal(self.O1.normal, start_pt, end_pt)
                        seg_hang = DY_segment(start_ptt, end_pt)
                        utl.arrange_hanging_along_seg(seg_hang, HANGING_CABINET_W[0], start_pt,
                                                      self.ele_list, self.boundary)
            else:
                start_pt = ran_p2
                end_pt = self.O1.seg.p2 if self.O1.seg.p2.distance(dr_center) < self.O1.seg.p1.distance(dr_center) \
                        else self.O1.seg.p1
                if start_pt != end_pt:
                    start_ptt, end_pt = DY_segment. \
                        get_p1_p2_from_normal(self.O1.normal, start_pt, end_pt)
                    seg_hang = DY_segment(start_ptt, end_pt)
                    utl.arrange_hanging_along_seg(seg_hang, HANGING_CABINET_W[0], start_pt,
                                                  self.ele_list, self.boundary)
        else:
            start_pt = ran_p2
            end_pt = end_pt
            if start_pt != end_pt:
                start_ptt, end_pt = DY_segment. \
                    get_p1_p2_from_normal(self.O1.normal, start_pt, end_pt)
                seg_hang = DY_segment(start_ptt, end_pt)

                utl.arrange_hanging_along_seg(seg_hang, HANGING_CABINET_W[0], start_pt,
                                              self.ele_list, self.boundary)


    def run4101_4200_4210_L(self):
        pass

    def arrange_L_refrigerator(self):
        # 冰箱在长边时最小距离，2500
        tmpL0 = REFRIGERATOR_W + MIN_DIS_REFR_SINK_RANG + RANGEHOOD_SINK_W + BASE_CORNER_W[0]
        # 冰箱在短边时最小距离，2200
        tmpL1 = REFRIGERATOR_W + MIN_DIS_REFR_SINK_RANG + RANGEHOOD_SINK_W + CABINET_L

        if self.l < tmpL0:
            # long < L0 & wid < L1 不布置冰箱
            if self.w < tmpL1:
                return False, self.long_seg, self.short_seg
            # long < L0 & wid > L1 冰箱布置在短边
            if self.w > tmpL1:
                p1, p2 = self.short_seg.p1, self.short_seg.p2
                ref_p1 = p2 if p1 == self.triangle_vertice else p1
                tmpseg = DY_segment(ref_p1, self.triangle_vertice)
                ref_p2 = ref_p1 + tmpseg.dir.p2 * REFRIGERATOR_W
                ref_p1, ref_p2 = DY_segment. \
                    get_p1_p2_from_normal(self.short_seg.normal, ref_p1, ref_p2)
                backline = DY_segment(ref_p1, ref_p2)
                refrigerator = Refrigerator(backline, CABINET_L)
                self.ele_list.append(refrigerator)
                s_seg = DY_segment(
                    self.triangle_vertice,
                    self.triangle_vertice + self.long_seg.normal.p2 * (self.w - REFRIGERATOR_W)
                )
                return True, self.long_seg, s_seg
        else:
            # long > L0 冰箱放置在长边
            p1, p2 = self.long_seg.p1, self.long_seg.p2
            ref_p1 = p2 if p1 == self.triangle_vertice else p1
            tmpseg = DY_segment(ref_p1, self.triangle_vertice)
            ref_p2 = ref_p1 + tmpseg.dir.p2 * REFRIGERATOR_W
            ref_p1, ref_p2 = DY_segment. \
                get_p1_p2_from_normal(self.long_seg.normal, ref_p1, ref_p2)
            backline = DY_segment(ref_p1, ref_p2)
            refrigerator = Refrigerator(backline, CABINET_L)
            self.ele_list.append(refrigerator)
            l_seg = DY_segment(
                self.triangle_vertice,
                self.triangle_vertice + self.short_seg.normal.p2 * (self.l - REFRIGERATOR_W)
            )
            return True, l_seg, self.short_seg#l_seg是去掉冰箱剩余的长边

    def arrange_U_refrigerator(self):
        '''放置冰箱的条件是u1.reg的长度大于最小转角地柜的长度900+650=1550'''
        limit_l = BASE_CORNER_W[0] + REFRIGERATOR_W
        u0_op = helpers.get_opposite_bounds(self.u0, self.boundary)[0]  # method 1
        ref_start = u0_op.line.intersection(self.u1_reg.seg)[0]
        if self.u1_reg.seg.length >= limit_l:
            # for v in self.boundary.polygon.vertices:
            #     if v.distance(self.triangle_vertice) > max(self.u1_reg.seg.length, self.u0.seg):#method 2
            #         ref_p1 = v
            ref_end = ref_start - self.u0.normal.p2 * REFRIGERATOR_W
            ref_p1, ref_p2 = DY_segment. \
                get_p1_p2_from_normal(self.u1_reg.normal, ref_start, ref_end)
            ref_bl = DY_segment(ref_p1, ref_p2)
            refrigerator = Refrigerator(ref_bl, CABINET_L)
            self.ele_list.append(refrigerator)
            ref_res_seg_p1 = self.u1_reg.p1 if self.u1_reg.p2 == ref_p1 else \
                self.u1_reg.p2
            update_ref_seg = DY_segment(ref_res_seg_p1, ref_end)
            return True, ref_end
        else:
            return False, ref_start
        pass

    def get_L_corner_cabinet_type(self, bl, len):

        door = helpers.get_eles(self.ele_list, Door)
        self.triangle_vertice = utl.get_triangle_vertice(door[0], self.boundary)
        '''
        实例左右转角柜：
        根据布局逻辑--long_seg上布置转角地柜，
        通过long_seg.p1 or p2 是否与三角动线模型的顶点相等
        能够有效实现转角地柜实例化 
        '''
        if self.long_seg.p1 == self.triangle_vertice:
            corinstance = RightCornerCabinet(bl, len)
        elif self.long_seg.p2 == self.triangle_vertice:
            corinstance = LeftCornerCabinet(bl, len)
        else:
            raise Exception("warning:此处违反布局的顺时针规则！")
        return corinstance

    def get_U_corner_cabinet_type(self, bl1, bl2, len):

        # door = helpers.get_eles(self.ele_list, Door)
        # main_win = helpers.get_eles(self.line_list, Window)
        # self.triangle_vertice = utl.get_triangle_vertice(main_win[0], self.u0)
        '''
        分析可知：两个转角地柜的方向呈现一致，此处可以统一获取其转角方向以供摆放
        '''
        if bl1.p1 == self.triangle_vertice:
            corinstance = RightCornerCabinet(bl1, len)
            if bl2 is not None:
                corinstance = RightCornerCabinet(bl2, len)
        elif bl1.p2 == self.triangle_vertice:
            corinstance = LeftCornerCabinet(bl1, len)
            if bl2 is not None:
                corinstance = LeftCornerCabinet(bl2, len)
        else:
            raise Exception("warning:当前转角地柜摆放有误！")
        return corinstance

    def triangle_long_table(self):
        sum_len_lst = []
        corner_wid = []
        cabinet_wid = []
        sink_ran_wid = []

        corner_wid.append(BASE_CORNER_W[0])
        cabinet_wid.append(0)
        sink_ran_wid.append(RANGEHOOD_SINK_W)

        corner_wid.append(BASE_CORNER_W[2])
        cabinet_wid.append(0)
        sink_ran_wid.append(RANGEHOOD_SINK_W)

        corner_wid.append(BASE_CORNER_W[1])
        cabinet_wid.append(SINGLE_CABINET_W[1])
        sink_ran_wid.append(RANGEHOOD_SINK_W)

        for i in range(len(corner_wid)):
            sum = corner_wid[i] + cabinet_wid[i] + sink_ran_wid[i]
            sum_len_lst.append(sum)

        pd_dict = {
            "sum_len": sum_len_lst,
            "corner_wid": corner_wid,
            "cabinet_wid": cabinet_wid,
            "sink_ran_wid": sink_ran_wid
        }
        self.triangle_long_df = pd.DataFrame(pd_dict)
        self.triangle_long_df = self.triangle_long_df.sort_values(by='sum_len')

    def residual_len_table(self):
        sum_len = []
        single_cabinet_wid = []
        double_cabinet_wid = []
        pull_bas_wid = []

        pull_bas_wid.append(0)
        single_cabinet_wid.append(0)
        double_cabinet_wid.append(0)
        sum_len.append(0)

        for pull_w in PULL_BASKET_W:
            pull_bas_wid.append(pull_w)
            single_cabinet_wid.append(0)
            double_cabinet_wid.append(0)
            sum_len.append(pull_w)
        for s_cab_w in SINGLE_CABINET_W:
            pull_bas_wid.append(0)
            single_cabinet_wid.append(s_cab_w)
            double_cabinet_wid.append(0)
            sum_len.append(s_cab_w)
        for d_cab_w in DOUBLE_CABINET_W:
            pull_bas_wid.append(0)
            single_cabinet_wid.append(0)
            double_cabinet_wid.append(d_cab_w)
            sum_len.append(d_cab_w)
        for s_cab_w in SINGLE_CABINET_W:
            for d_cab_w in DOUBLE_CABINET_W:
                pull_bas_wid.append(0)
                single_cabinet_wid.append(s_cab_w)
                double_cabinet_wid.append(d_cab_w)
                sum_len.append(d_cab_w + s_cab_w)
        pd_dict = {
            "sum_len": sum_len,
            "pull_wid": pull_bas_wid,
            "single_cab_wid": single_cabinet_wid,
            "double_cab_wid": double_cabinet_wid
        }
        self.residual_len_table = pd.DataFrame(pd_dict)
        self.residual_len_table = self.residual_len_table.sort_values(by='sum_len')

