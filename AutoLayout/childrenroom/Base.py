#—*— coding: utf-8 _*_
from AutoLayout import CommonElement, BaseClass
from AutoLayout.BaseModual import *
import AutoLayout.CommonElement
from AutoLayout.childrenroom.settings import *
from AutoLayout.settings import *
import cmath
import random
from AutoLayout.DY_Line import Window
from AutoLayout.childrenroom.Element import *
import AutoLayout.main_bedroom.utility as mb_uti
from AutoLayout.main_bedroom.utility import *
from AutoLayout import helpers
from AutoLayout.helpers import *

import numpy as np
import pandas as pd


class Childrenroom(Region):

    def __init__(self):
        super(Childrenroom, self).__init__()
        self.main_curtain = None
        self.main_win_wall = None
        self.bed_wall = None
        self.win_list = []
        ''' ---attr for virtual ---- ML --- '''
        self.door_list = []
        self.vir_door_list = []
        self.entrance = None
        self.vir_win_list = []
        self.vir_win = None
        self.__init()

    def run(self):
        self.run_anytype()
        arrangement_dict = {
            (4, 1, 1): self.run411,
            (6, 1, 1): self.run611
        }
        key = (len(self.boundary.polygon.vertices), self.doors, self.windows)
        if not arrangement_dict.get(key, False):
            # raise Exception("暂时不支持这种户型")
            self.run411()
        arrangement_dict.get(key)()
        (xmin, ymin, xmax, ymax) = self.boundary.polygon.bounds
        xlen = xmax - xmin
        ylen = ymax - ymin

        # # 区间判断2.1米-4米
        # if xlen > CHILDBED_MAX_LEN or xlen < CHILDED_MIN_LEN or \
        #                 ylen > CHILDBED_MAX_LEN or ylen < CHILDED_MIN_LEN:
        #     raise Exception("warning:此功能区作为儿童房长度不满足")
        # if abs(self.boundary.polygon.area) < CHILDED_MIN_LEN * CHILDED_MIN_LEN:
        #     raise Exception("warning:此功能区作为儿童房面积不足")
        return True

    def get_entrance_point(self, vir_dr_mid_p):
        vir_ver_list = []
        for p in self.virtual_boundary.polygon.vertices:
            long = point_distance(p, vir_dr_mid_p)
            vir_ver_list.append([p, long])
        vir_ver_list.sort(key=lambda x: x[1], reverse=False)
        a = vir_ver_list[0][0]
        return a

    def get_entrance(self):
        dr = None
        bal_tag = 0
        bal_dr_list = []
        bal_dr = None
        entrance_list = []
        for door in self.door_list:
            if 'Balcony' in door.connect_list:
                '''如果有阳台，返回阳台标志，并将门映射成线返回，列表用于未来扩展控制'''
                bal_tag = 1
                dr = get_vir_door(door, self.boundary)
                bal_dr = dr
                bal_dr_list.append(dr)
            elif 'Bathroom' in door.connect_list or 's' in door.connect_list:
                ''' ---这儿添加不是入口的门的种类，后期避开---'''
                dr = get_vir_door(door, self.boundary)
            else:
                '''待完全定型后决定是过道还是什么情况的门为入口'''
                entrance_list.append(door)
        if len(entrance_list) == 1:
            self.entrance = entrance_list[0]

        else:
            print('这个门数量奇葩')
            self.entrance = entrance_list[0]

        vir_door = get_vir_door(self.entrance, self.boundary)
        vir_door_line = get_mother_boundary(vir_door, self.boundary)
        '''返回虚映射门'''
        return vir_door, vir_door_line, bal_tag, bal_dr

    def run_anytype(self):
        '''虚拟边界'''
        self.virtual_boundary = helpers.get_virtual_boundary(self.boundary)
        '''初始化入口'''
        for i in self.ele_list:
            if isinstance(i, Door):
                self.door_list.append(i)
        bal_tag = 0
        dr, door_line, bal_tag, bal_door = self.get_entrance()
        dr_mid_p = dr.seg.midpoint
        '''---------对门标记，在点初始化之后根据标记进行虚拟化-----------------'''
        # 完成门映射到边上,vir_dr只虚拟门
        # vir_dr_tag 是虚拟门标识，为0 表示实体门就在虚拟墙上，不需要操作
        vir_dr_tag = 1
        for s in self.virtual_boundary.seg_list:
            if s.line.contains(dr_mid_p):
                if s.seg.contains(dr_mid_p):
                    door_line = s
                    vir_dr_tag = 0
                else:  # 2刚好是在把上的虚界线延长线上。
                    vir_dr_tag = 2
                break
        a = self.get_entrance_point(dr_mid_p)

        '''---------如果门在把上，更新门跟虚拟边界关系---'''
        if vir_dr_tag != 0:  # 说明门是在把上，标志为1和2只是说要设置虚门时偏移距离不一样
            # 同时在虚边界上的内点，为了完成去吧
            inner = get_inner_point(self.boundary)
            inner_list = []
            for i in inner:
                if is_inner_point(i, self.virtual_boundary) == 2:
                    inner_list.append(i)

            tp = None
            if vir_dr_tag == 1:  # 1 代表多种类型的吧
                for s in self.virtual_boundary.seg_list:
                    if s.seg.intersection(door_line.seg) != []:
                        tp = s.seg.intersection(door_line.seg)[0]
                        t_doorline = s
                        break
                if tp == None:
                    t_doorline = get_nearest_parallel_line(door_line, self.virtual_boundary)
                if True:
                    '''确定离把近的点'''
                    tp_list = []
                    for i in inner:
                        if t_doorline.seg.contains(i):
                            tp_list.append(i)
                    if tp_list == []:
                        print('不合理')  # 但还是要继续进行
                        if True:
                            tp_list = get_adj_seg(a, self.virtual_boundary)
                            if tp_list[0].seg == t_doorline.seg:
                                t_doorline = tp_list[1]
                            else:
                                t_doorline = tp_list[0]
                            tdr = []
                            for i in tp_list:
                                tdr.append([i, point_distance(i, a)])
                            tdr.sort(key=lambda x: x[1])
                            dr = DY_segment(a, tdr[0][0])
                            dr_mid_p = dr.seg.midpoint()
                    elif len(tp_list) == 1:
                        dr = DY_segment(a, tp_list[0])
                        vir_dr_mid_p = dr.seg.midpoint
                    else:
                        # 多个点
                        tdr = []
                        for i in tp_list:
                            tdr.append([i, point_distance(i, a)])
                        tdr.sort(key=lambda x: x[1])
                        dr = DY_segment(a, tdr[1][0])
                        dr_mid_p = dr.seg.midpoint()
            else:
                tp_list = get_adj_seg(a, self.virtual_boundary)
                if tp_list[0].line.contains(dr_mid_p):
                    t_doorline = tp_list[1]
                else:
                    t_doorline = tp_list[0]
                for i in inner_list:
                    if t_doorline.seg.contains(i):
                        tp = i
                if tp == None:
                    print('不合理')
                else:
                    dr = DY_segment(a, tp)
                    vir_dr_mid_p = dr.seg.midpoint
            # 虚拟数据赋给实际参数
            door_line = t_doorline
            dr = dr
            dr_mid_p = vir_dr_mid_p

        '''---------初始化窗户-----------------------------------------------'''
        if bal_tag:
            self.vir_win_list = get_vir_win(self.line_list)  # 依旧初始化这个，如果以后要扩展避让函数这需要这个列表。
            self.vir_win = get_mother_boundary(bal_door, self.boundary)  # self.vir_win 就是指所在墙
            win_mid_p = self.vir_win.seg.midpoint
            # 先确定主窗，主窗跟虚拟边界的关系再说，定义为主窗阳台虚拟边。
            win_tag = 1
        else:
            '''未直接标注阳台，可能有，使用虚边界和最长窗来界定
            ------1,阳台未标记，那阳台上的窗户应该最大
            ------2，阳台标记，虚边界应该最大
            ------3，房间内的窗户太大，那他是最大，忽略阳台
            '''
            if self.line_list != []:
                self.vir_win_list = get_vir_win(self.line_list)
                vir_win_list = []
                for x in self.vir_win_list:
                    seg = DY_segment(x.seg.p1, x.seg.p2)
                    vir_win_list.append(seg)

                # 窗户也虚映射到边上成为线段
                self.vir_win = vir_win_list[0]
                win_mid_p = self.vir_win.seg.midpoint
                win_tag = 1
            else:
                # 没有窗户和虚边界，无窗户型
                win_tag = 0

        '''-----先布局窗户----------------------------------------------------'''
        if bal_tag or win_tag:
            win_move_dis = CURTAIN_LEN  # 有无窗造成的移动距离
            '''----先放窗帘---------'''
            main_curtain = Curtain()
            backline = self.vir_win
            # 为了确保虚拟窗户在墙虚拟墙上。即窗帘无论什么情况都拉在虚拟墙这里
            # if bal_tag==0
            vir_win_tag = 0
            for i in self.virtual_boundary.seg_list:  # 阳台或窗在虚边界上
                if i.seg.contains(win_mid_p):
                    backline = i
                    vir_win_tag = 1
                    break
            if vir_win_tag == 0:  # 不在虚边界上
                backline = get_nearest_parallel_line(self.vir_win, self.virtual_boundary)

            if backline.line.contains(dr_mid_p):
                print('留个标记')

            main_curtain.set_pos(backline, main_curtain.len)
            self.ele_list.append(main_curtain)
            self.vir_win = backline  # 阳台位置信息，统一用vir——win
            win_mid_p = self.vir_win.seg.midpoint
        else:
            # 无窗户型
            win_move_dis = 0
            self.vir_win = get_opposite_bounds(door_line, self.virtual_boundary)[0]
            win_mid_p = self.vir_win.seg.midpoint

        '''现有标志，bal_tag 阳台标志，win_tag 虚拟窗标志，门的信息已经被虚拟门代替了。
                            door-line是门墙，
                        '''
        '''-----下面开始其他组件，由门边信息和阳台边vir_win信息来决定-------'''
        tp_list = get_adj_seg(a, self.virtual_boundary)
        if tp_list[0].line.contains(dr_mid_p):
            self.near_door_wall = tp_list[1]
        else:
            self.near_door_wall = tp_list[0]
        self.op_door_wall = get_opposite_bounds(door_line, self.virtual_boundary)[0]

    def run611(self):
        small_recs = []
        # 1.    """六个顶点，一门一窗, 首先判断门是否在过道内"""
        # 找到六边形内部的点     bounds界限的意思   找到平面图中的界限点
        xmin, ymin, xmax, ymax = self.boundary.polygon.bounds  # 获取的是边界中的四个极值,即X最大,最小,Y最大最小
        for p in self.boundary.polygon.vertices:  # vertices平面图形的顶点
            # 如果p点不等于极值
            if p.x != xmin and p.x != xmax and p.y != ymin and p.y != ymax:  # 即p点是刀把中的拐角的那个点
                inner_point = p
                # 找到过道区域, 先找内部点划分后比较短的线段
        pp = inner_point
        # intersection交叉       Line是生成一条直线，     找到line延伸的直线与上下相交的交点（2个）放在一个列表中
        intersec_list = self.boundary.polygon.intersection(Line(pp, Point(pp.x, pp.y + 1)))  # point是pp对象实例的一个点
        for p in intersec_list:
            #  Point2D表示二维空间上的点
            if isinstance(p, Point2D):
                p0 = p
                break
        # Line是生成一条直线，     找到line延伸的直线与左右相交的交点放在一个列表中
        intersec_list = self.boundary.polygon.intersection(Line(pp, Point(pp.x + 1, pp.y)))
        # 输出的结果
        # [Point2D(3000, 1000), Segment2D(Point2D(-1200, 1000), Point2D(0, 1000))]要单独的一个点
        for p in intersec_list:
            if isinstance(p, Point2D):
                p1 = p
                break
        if inner_point.distance(p0) < inner_point.distance(p1):
            passage_pt = p0  # 过道边界的交点
            xlen = inner_point.distance(p1)
            ylen = ymax - ymin
        else:
            # 刀把过道的距离，
            passage_pt = p1
            # 卧室X轴方向的长度
            xlen = xmax - xmin
            # 卧室Y轴方向的长度等于p0的长度
            ylen = inner_point.distance(p0)
        # 在找到划分面积比较小的区域
        # 即使刀把型区域的四个点
        if passage_pt.x == inner_point.x:
            p1, p2 = passage_pt, inner_point
            for p in self.boundary.polygon.vertices:
                if p == inner_point:
                    continue
                if p.y == inner_point.y:
                    p3 = p
            for p in self.boundary.polygon.vertices:
                if p.y == passage_pt.y and p.x == p3.x:
                    p4 = p
            small_rec = Polygon(p1, p2, p3, p4)  #
            small_recs.append(small_rec)
        else:
            p1, p2 = passage_pt, inner_point
            for p in self.boundary.polygon.vertices:
                if p == inner_point:
                    continue
                if p.x == inner_point.x:
                    p3 = p
            for p in self.boundary.polygon.vertices:
                if p.x == passage_pt.x and p.y == p3.y:
                    p4 = p
            small_rec = Polygon(p1, p2, p3, p4)
            small_recs.append(small_rec)
            # return small_rec
        # 判断过道区域内是否有门
        for d in self.ele_list:
            if isinstance(d, CommonElement.Door):
                door = d
                break
        found_door = False
        # small_rec刀把型小区域
        # 遍历刀把型区域的边界

        for seg in small_rec.sides:
            # 如果边界线中含有门的backline则门可以画出来
            if seg.contains(door.backline.seg):
                found_door = True
        # 门的边界与刀把型交叉的个数
        if len(small_rec.intersection(door.boundary.polygon)) != 0:
            found_door = True
        if found_door == False:
            raise Exception("warning:暂时不支持门不在过道内的六边形户型")

        #通过翻转、旋转归一化户型，使得过道在左下角
        # vir_line = Segment2D(inner_point, passage_pt)
        # for s in small_rec.sides:
        #     if s.is_parallel(vir_line) and s != vir_line:
        #         markline0 = s
        #         break
        # for s in self.boundary.seg_list:
        #     if s.seg == markline0:
        #         markline = s
        #         break
        # markline_mid = markline.seg.midpoint
        # center = self.boundary.polygon.centroid
        # relative_pos = markline_mid - center
        # normalize_zone(markline.normal, relative_pos, self)
        # 此时和411情况相同
        # 区间判断2.1米-4米
        # if xlen > CHILDBED_MAX_LEN or xlen < CHILDED_MIN_LEN or \
        #                 ylen > CHILDBED_MAX_LEN or ylen < CHILDED_MIN_LEN:
        #     raise Exception("warning:此功能区作为儿童房长度不满足")
        # if abs(self.boundary.polygon.area) < CHILDED_MIN_LEN * CHILDED_MIN_LEN:
        #     raise Exception("warning:此功能区作为儿童房面积不足")

        self.run411()
        return True

    def run411(self):
        # self.win_list, self.main_curtain, self.main_win_wall = \
        #     mb_uti.arrange_main_curtain(self.line_list, self.ele_list)

        self.main_win_wall = self.vir_win
        # 1.判断床所在的墙，放置床
        door = get_eles(self.ele_list, CommonElement.Door)[0]
        door_center = door.boundary.polygon.centroid
        self.door_wall = self.near_door_wall
        self.bed_wall = self.op_door_wall

        bed_door_dis = self.bed_wall.line.distance(door_center) - int(CHILD_DOOR/2)
        if bed_door_dis >= BED_LEN[0]:
            # 根据表格取床、衣柜、帐篷活动区最优值
            bed_dis = self.bed_wall.seg.length
            bed_nearst_df = self.bed_df.loc[self.bed_df.sum_len <= bed_dis]
            bed_nearst_df = bed_nearst_df.ix[bed_nearst_df.sum_len.idxmax]

            bed_width = bed_nearst_df['bed_len']
            clo_width = bed_nearst_df['closet_len']
            bed_tent_len = bed_nearst_df['tent_len']
            # 判断门所在的墙是否有窗户
            b_p0 = self.bed_wall.seg.intersection(self.door_wall.seg)[0]
            if self.door_wall == self.main_win_wall:
                b_p0 = b_p0 + self.main_win_wall.normal.p2 * DIS_CURTAIN
            else:
                b_p0 = b_p0

            if self.bed_wall == self.main_win_wall:
                b_p0 = b_p0 + self.main_win_wall.normal.p2 * DIS_CURTAIN
            else:
                b_p0 = b_p0

            b_p1 = b_p0 + self.door_wall.normal.p2 * bed_width
            bl_bed_p1, bl_bed_p2 = DY_segment. \
                get_p1_p2_from_normal(self.bed_wall.normal, b_p0, b_p1)

            backline = DY_segment(bl_bed_p1, bl_bed_p2)
            b = Bed()
            if bed_door_dis >= BED_LEN[-1]:
                b.len = BED_LEN[-1]
            if bed_door_dis < BED_LEN[-1]:
                b.len = BED_LEN[0]
            b.set_pos(backline, b.len)
            self.ele_list.append(b)

            # 2.放置儿童衣柜
            opposite_wall = get_opposite_bounds(self.near_door_wall, self.boundary)
            if opposite_wall[0].seg.length > opposite_wall[-1].seg.length:
                opposite_wall[0] = opposite_wall[0]
            else:
                opposite_wall[0] = opposite_wall[-1]

            closet_p0 = self.bed_wall.seg.intersection(opposite_wall[0].seg)[0]

            # 判断窗户位置
            if self.bed_wall == self.main_win_wall:
                closet_p0 = closet_p0 + self.main_win_wall.normal.p2 * DIS_CURTAIN
            else:
                closet_p0 = closet_p0

            if opposite_wall[0] == self.main_win_wall:
                closet_p1 = closet_p0 + self.main_win_wall.normal.p2 * DIS_CURTAIN
            else:
                closet_p1 = closet_p0
            closet_p2 = closet_p1 - self.door_wall.normal.p2 * clo_width
            clo_bed_p1, clo_bed_p2 = DY_segment. \
                get_p1_p2_from_normal(self.bed_wall.normal, closet_p2, closet_p1)
            backline = DY_segment(clo_bed_p1, clo_bed_p2)
            clo = ChildCloset(backline)
            self.ele_list.append(clo)

            # 当面宽足够时，寻找最优组合
            dis = opposite_wall[0].seg.length
            nearst_df = self.df.loc[self.df.sum_len <= dis]
            nearst_df = nearst_df.ix[nearst_df.sum_len.idxmax]

            play_len = nearst_df['play_len']
            table_len = nearst_df['table_len']
            stool_len = nearst_df['stool_len']
            tent_len = nearst_df['tent_len']

            # 3.儿童玩具柜：
            door_center = door.boundary.polygon.centroid
            childplay_dis = opposite_wall[0].line.distance(door_center) - int(CHILD_DOOR / 2)

            opposite1_wall = get_opposite_bounds(self.bed_wall, self.boundary)
            if opposite1_wall[0].seg.length > opposite1_wall[-1].seg.length:
                opposite1_wall[0] = opposite1_wall[0]
            else:
                opposite1_wall[0] = opposite1_wall[-1]

            childplay_p0 = opposite_wall[0].seg.intersection(opposite1_wall[0].seg)[0]
            if opposite_wall[0] == self.main_win_wall:
                childplay_p0 = childplay_p0 + self.main_win_wall.normal.p2 * DIS_CURTAIN
            else:
                childplay_p0 = childplay_p0

            len_list = []
            len_list.append(0)
            p_op_wall = get_opposite_bounds(self.bed_wall, self.boundary)
            for wall in p_op_wall:
                len_list.append(wall.seg.length)
            idx = len_list.index(max(len_list))
            p_op_wall = p_op_wall[idx - 1]

            if p_op_wall == self.main_win_wall:
                childplay_p1 = childplay_p0 - self.bed_wall.normal.p2 * DIS_CURTAIN
            else:
                childplay_p1 = childplay_p0

            if childplay_dis > CHILD_PLAY_WIDTH[4]:
                childplay_p2 = childplay_p1 - self.door_wall.normal.p2 * CHILD_PLAY_WIDTH[4]
                play_p1, play_p2 = DY_segment. \
                    get_p1_p2_from_normal(p_op_wall.normal, childplay_p1, childplay_p2)

                backline = DY_segment(play_p1, play_p2)
                p = ChildPlay()
                p.len = play_len
                p.set_pos(backline, p.len)
                self.ele_list.append(p)

            elif childplay_dis < CHILD_PLAY_WIDTH[4] and childplay_dis > CHILD_PLAY_WIDTH[0]:
                childplay_p2 = childplay_p1 - self.door_wall.normal.p2 * CHILD_PLAY_WIDTH[0]
                play_p1, play_p2 = DY_segment. \
                    get_p1_p2_from_normal(p_op_wall.normal, childplay_p1, childplay_p2)

                backline = DY_segment(play_p1, play_p2)
                p = ChildPlay()
                p.len = play_len
                p.set_pos(backline, p.len)
                self.ele_list.append(p)

            # 4.放置游戏桌和凳子
            if play_len != 0:
                table_len1 = table_len + stool_len + DIS_CHILD_TABLE*2
                table_len2 = table_len + int(stool_len/2) + DIS_CHILD_TABLE
                door_mainwall_dis = opposite_wall[0].line.distance(door_center) - int(CHILD_DOOR/2)

                # 方案一：四个凳子
                if door_mainwall_dis >= table_len1 and stool_len >= CHIDL_STOOL[-2]:
                    t_p1 = childplay_p1 - \
                           self.bed_wall.normal.p2 * (play_len + DIS_CHILD_TABLE + int(stool_len / 2)) - \
                           self.door_wall.normal.p2 * (DIS_CHILD_TABLE + int(stool_len / 2))

                    t_p2 = t_p1 - self.door_wall.normal.p2 * table_len

                    t_p3 = t_p2 - self.bed_wall.normal.p2 * table_len

                    table_p1, table_p2 = DY_segment. \
                        get_p1_p2_from_normal(p_op_wall.normal, t_p1, t_p2)

                    backline = DY_segment(table_p1, table_p2)
                    t = ChildTable()
                    t.len = table_len
                    t.set_pos(backline, t.len)
                    self.ele_list.append(t)

                    # 放置游戏凳子
                    s1_p0 = t_p2 - self.bed_wall.normal.p2 * int(table_len / 2) - \
                            self.bed_wall.normal.p2 * int(stool_len / 2)

                    s1_p1 = s1_p0 - self.door_wall.normal.p2 * int(stool_len / 2)
                    s1_p2 = s1_p0 + self.door_wall.normal.p2 * int(stool_len / 2)

                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s1_p1, s1_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s1 = ChildStool()
                    s1.len = stool_len
                    s1.set_pos(backline, s1.len)
                    self.ele_list.append(s1)

                    s3_p1 = s1_p2 + self.door_wall.normal.p2 * int(table_len)
                    s3_p2 = s1_p1 + self.door_wall.normal.p2 * int(table_len)

                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s3_p1, s3_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s3 = ChildStool()
                    s3.len = stool_len
                    s3.set_pos(backline, s3.len)
                    self.ele_list.append(s3)

                    s2_p0 = t_p3 + self.door_wall.normal.p2 * (int(table_len / 2) - int(stool_len / 2))
                    s2_p1 = s2_p0 - self.bed_wall.normal.p2 * int(stool_len / 2)
                    s2_p2 = s2_p1 + self.door_wall.normal.p2 * stool_len

                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s2_p1, s2_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s2 = ChildStool()
                    s2.len = stool_len
                    s2.set_pos(backline, s2.len)
                    self.ele_list.append(s2)

                    s4_p1 = s2_p2 + self.bed_wall.normal.p2 * int(table_len)
                    s4_p2 = s2_p1 + self.bed_wall.normal.p2 * int(table_len)
                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s4_p1, s4_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s4 = ChildStool()
                    s4.len = stool_len
                    s4.set_pos(backline, s4.len)
                    self.ele_list.append(s4)

                # 方案二：三个凳子
                if stool_len >= CHIDL_STOOL[-2] and door_mainwall_dis >= table_len2 and door_mainwall_dis < table_len1 :
                    t_p1 = childplay_p1 - \
                           self.bed_wall.normal.p2 * (play_len + DIS_CHILD_TABLE + int(stool_len / 2))
                    t_p2 = t_p1 - self.door_wall.normal.p2 * table_len
                    t_p3 = t_p2 - self.bed_wall.normal.p2 * table_len

                    table_p1, table_p2 = DY_segment. \
                        get_p1_p2_from_normal(p_op_wall.normal, t_p1, t_p2)

                    backline = DY_segment(table_p1, table_p2)
                    t = ChildTable()
                    t.len = table_len
                    t.set_pos(backline, t.len)
                    self.ele_list.append(t)

                    # 放置游戏凳子
                    s1_p0 = t_p2 - self.bed_wall.normal.p2 * int(table_len / 2) - \
                            self.bed_wall.normal.p2 * int(stool_len / 2)

                    s1_p1 = s1_p0 - self.door_wall.normal.p2 * int(stool_len / 2)
                    s1_p2 = s1_p0 + self.door_wall.normal.p2 * int(stool_len / 2)

                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s1_p1, s1_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s1 = ChildStool()
                    s1.len = stool_len
                    s1.set_pos(backline, s1.len)
                    self.ele_list.append(s1)

                    s2_p0 = t_p3 + self.door_wall.normal.p2 * (int(table_len / 2) - int(stool_len / 2))
                    s2_p1 = s2_p0 - self.bed_wall.normal.p2 * int(stool_len / 2)
                    s2_p2 = s2_p1 + self.door_wall.normal.p2 * stool_len

                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s2_p1, s2_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s2 = ChildStool()
                    s2.len = stool_len
                    s2.set_pos(backline, s2.len)
                    self.ele_list.append(s2)

                    s4_p1 = s2_p2 + self.bed_wall.normal.p2 * int(table_len)
                    s4_p2 = s2_p1 + self.bed_wall.normal.p2 * int(table_len)
                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s4_p1, s4_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s4 = ChildStool()
                    s4.len = stool_len
                    s4.set_pos(backline, s4.len)
                    self.ele_list.append(s4)

                if stool_len >= CHIDL_STOOL[1] and stool_len < CHIDL_STOOL[-2]:
                    table_len1 = table_len + stool_len * 2 + DIS_CHILD_TABLE * 2
                    table_len2 = table_len + stool_len + DIS_CHILD_TABLE

                    if door_mainwall_dis > table_len1:
                        t_p1 = childplay_p1 - \
                            self.bed_wall.normal.p2 * play_len - \
                            self.door_wall.normal.p2 * (DIS_CHILD_TABLE + stool_len)
                        t_p2 = t_p1 - self.door_wall.normal.p2 * table_len
                        t_p3 = t_p2 - self.bed_wall.normal.p2 * table_len

                        table_p1, table_p2 = DY_segment. \
                            get_p1_p2_from_normal(p_op_wall.normal, t_p1, t_p2)

                        backline = DY_segment(table_p1, table_p2)
                        t = ChildTable()
                        t.len = table_len
                        t.set_pos(backline, t.len)
                        self.ele_list.append(t)

                        s1_p0 = t_p2 - self.bed_wall.normal.p2 * int(table_len / 2) - \
                                self.bed_wall.normal.p2 * stool_len

                        s1_p1 = s1_p0 - self.door_wall.normal.p2 * stool_len
                        s1_p2 = s1_p0 + self.door_wall.normal.p2 * stool_len

                        stool_p1, stool_p2 = DY_segment. \
                            get_p1_p2_from_normal(self.bed_wall.normal, s1_p1, s1_p2)

                        backline = DY_segment(stool_p1, stool_p2)
                        s1 = ChildStool()
                        s1.len = stool_len * 2
                        s1.set_pos(backline, s1.len)
                        self.ele_list.append(s1)

                        s3_p1 = s1_p2 + self.door_wall.normal.p2 * int(table_len)
                        s3_p2 = s1_p1 + self.door_wall.normal.p2 * int(table_len)

                        stool_p1, stool_p2 = DY_segment. \
                            get_p1_p2_from_normal(self.bed_wall.normal, s3_p1, s3_p2)

                        backline = DY_segment(stool_p1, stool_p2)
                        s3 = ChildStool()
                        s3.len = stool_len * 2
                        s3.set_pos(backline, s3.len)
                        self.ele_list.append(s3)

                        s2_p0 = t_p3 + self.door_wall.normal.p2 * (int(table_len / 2) - stool_len )
                        s2_p1 = s2_p0 - self.bed_wall.normal.p2 * stool_len
                        s2_p2 = s2_p1 + self.door_wall.normal.p2 * stool_len * 2

                        stool_p1, stool_p2 = DY_segment. \
                            get_p1_p2_from_normal(self.bed_wall.normal, s2_p1, s2_p2)

                        backline = DY_segment(stool_p1, stool_p2)
                        s2 = ChildStool()
                        s2.len = stool_len * 2
                        s2.set_pos(backline, s2.len)
                        self.ele_list.append(s2)

                # 方案三：两个凳子
                if stool_len >= CHIDL_STOOL[-2] and door_mainwall_dis < table_len2:
                    t_p1 = childplay_p1 - \
                           self.bed_wall.normal.p2 * (play_len + DIS_CHILD_TABLE + int(stool_len / 2))
                    t_p2 = t_p1 - self.door_wall.normal.p2 * table_len
                    t_p3 = t_p2 - self.bed_wall.normal.p2 * table_len

                    table_p1, table_p2 = DY_segment. \
                        get_p1_p2_from_normal(p_op_wall.normal, t_p1, t_p2)

                    backline = DY_segment(table_p1, table_p2)
                    t = ChildTable()
                    t.len = table_len
                    t.set_pos(backline, t.len)
                    self.ele_list.append(t)

                    # 放置游戏凳子
                    s2_p0 = t_p3 + self.door_wall.normal.p2 * (int(table_len / 2) - int(stool_len / 2))
                    s2_p1 = s2_p0 - self.bed_wall.normal.p2 * int(stool_len / 2)
                    s2_p2 = s2_p1 + self.door_wall.normal.p2 * stool_len

                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s2_p1, s2_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s2 = ChildStool()
                    s2.len = stool_len
                    s2.set_pos(backline, s2.len)
                    self.ele_list.append(s2)

                    s4_p1 = s2_p2 + self.bed_wall.normal.p2 * int(table_len)
                    s4_p2 = s2_p1 + self.bed_wall.normal.p2 * int(table_len)
                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s4_p1, s4_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s4 = ChildStool()
                    s4.len = stool_len
                    s4.set_pos(backline, s4.len)
                    self.ele_list.append(s4)

                if stool_len == CHIDL_STOOL[0] and door_mainwall_dis > table_len1:
                    t_p1 = childplay_p1 - \
                           self.bed_wall.normal.p2 * play_len - \
                           self.door_wall.normal.p2 * (DIS_CHILD_TABLE + CHIDL_STOOL[-2])
                    t_p2 = t_p1 - self.door_wall.normal.p2 * table_len
                    t_p3 = t_p2 - self.bed_wall.normal.p2 * table_len

                    table_p1, table_p2 = DY_segment. \
                        get_p1_p2_from_normal(p_op_wall.normal, t_p1, t_p2)

                    backline = DY_segment(table_p1, table_p2)
                    t = ChildTable()
                    t.len = table_len
                    t.set_pos(backline, t.len)
                    self.ele_list.append(t)

                    s1_p0 = t_p2 - self.bed_wall.normal.p2 * int(table_len / 2) - \
                            self.bed_wall.normal.p2 * int(CHIDL_STOOL[-2]/2)

                    s1_p1 = s1_p0 - self.door_wall.normal.p2 * int(CHIDL_STOOL[-2]/2)
                    s1_p2 = s1_p0 + self.door_wall.normal.p2 * int(CHIDL_STOOL[-2]/2)

                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s1_p1, s1_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s1 = ChildStool()
                    s1.len = CHIDL_STOOL[-2]
                    s1.set_pos(backline, s1.len)
                    self.ele_list.append(s1)

                    s3_p1 = s1_p2 + self.door_wall.normal.p2 * int(table_len)
                    s3_p2 = s1_p1 + self.door_wall.normal.p2 * int(table_len)

                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s3_p1, s3_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s3 = ChildStool()
                    s3.len = CHIDL_STOOL[-2]
                    s3.set_pos(backline, s3.len)
                    self.ele_list.append(s3)

                if stool_len == CHIDL_STOOL[1] or stool_len == CHIDL_STOOL[2]:
                    table_len1 = table_len + stool_len * 2 + DIS_CHILD_TABLE * 2
                    table_len2 = table_len + stool_len + DIS_CHILD_TABLE

                    if door_mainwall_dis >= table_len2 and door_mainwall_dis < table_len1:
                        t_p1 = childplay_p1 - \
                           self.bed_wall.normal.p2 * play_len
                        t_p2 = t_p1 - self.door_wall.normal.p2 * table_len
                        t_p3 = t_p2 - self.bed_wall.normal.p2 * table_len

                        table_p1, table_p2 = DY_segment. \
                            get_p1_p2_from_normal(p_op_wall.normal, t_p1, t_p2)

                        backline = DY_segment(table_p1, table_p2)
                        t = ChildTable()
                        t.len = table_len
                        t.set_pos(backline, t.len)
                        self.ele_list.append(t)

                        s1_p0 = t_p2 - self.bed_wall.normal.p2 * int(table_len / 2) - \
                                self.bed_wall.normal.p2 * stool_len

                        s1_p1 = s1_p0 - self.door_wall.normal.p2 * stool_len
                        s1_p2 = s1_p0 + self.door_wall.normal.p2 * stool_len

                        stool_p1, stool_p2 = DY_segment. \
                            get_p1_p2_from_normal(self.bed_wall.normal, s1_p1, s1_p2)

                        backline = DY_segment(stool_p1, stool_p2)
                        s1 = ChildStool()
                        s1.len = stool_len * 2
                        s1.set_pos(backline, s1.len)
                        self.ele_list.append(s1)

                        s2_p0 = t_p3 + self.door_wall.normal.p2 * (int(table_len / 2) - stool_len)
                        s2_p1 = s2_p0 - self.bed_wall.normal.p2 * stool_len
                        s2_p2 = s2_p1 + self.door_wall.normal.p2 * stool_len * 2

                        stool_p1, stool_p2 = DY_segment. \
                            get_p1_p2_from_normal(self.bed_wall.normal, s2_p1, s2_p2)

                        backline = DY_segment(stool_p1, stool_p2)
                        s2 = ChildStool()
                        s2.len = stool_len * 2
                        s2.set_pos(backline, s2.len)
                        self.ele_list.append(s2)

                # 方案四：只有第一个凳子
                if stool_len == CHIDL_STOOL[1] or stool_len == CHIDL_STOOL[2]:
                    if door_mainwall_dis < table_len2:
                        table_len1 = table_len + stool_len * 2 + DIS_CHILD_TABLE * 2
                        table_len2 = table_len + stool_len + DIS_CHILD_TABLE
                        t_p1 = childplay_p1 - \
                               self.bed_wall.normal.p2 * play_len
                        t_p2 = t_p1 - self.door_wall.normal.p2 * table_len
                        t_p3 = t_p2 - self.bed_wall.normal.p2 * table_len

                        table_p1, table_p2 = DY_segment. \
                            get_p1_p2_from_normal(p_op_wall.normal, t_p1, t_p2)

                        backline = DY_segment(table_p1, table_p2)
                        t = ChildTable()
                        t.len = table_len
                        t.set_pos(backline, t.len)
                        self.ele_list.append(t)

                        s2_p0 = t_p3 + self.door_wall.normal.p2 * (int(table_len / 2) - stool_len)
                        s2_p1 = s2_p0 - self.bed_wall.normal.p2 * stool_len
                        s2_p2 = s2_p1 + self.door_wall.normal.p2 * stool_len * 2

                        stool_p1, stool_p2 = DY_segment. \
                            get_p1_p2_from_normal(self.bed_wall.normal, s2_p1, s2_p2)

                        backline = DY_segment(stool_p1, stool_p2)
                        s2 = ChildStool()
                        s2.len = stool_len * 2
                        s2.set_pos(backline, s2.len)
                        self.ele_list.append(s2)

                    if stool_len == CHIDL_STOOL[0] and door_mainwall_dis >= table_len2 and door_mainwall_dis < table_len1 + CHILD_TABLE[-2]:
                        t_p1 = childplay_p1 - \
                               self.bed_wall.normal.p2 * play_len
                        t_p2 = t_p1 - self.door_wall.normal.p2 * table_len
                        s1_p0 = t_p2 - self.bed_wall.normal.p2 * int(table_len / 2) - \
                                self.bed_wall.normal.p2 * int(CHIDL_STOOL[-2]/2)

                        s1_p1 = s1_p0 - self.door_wall.normal.p2 * int(CHIDL_STOOL[-2]/2)
                        s1_p2 = s1_p0 + self.door_wall.normal.p2 * int(CHIDL_STOOL[-2]/2)

                        stool_p1, stool_p2 = DY_segment. \
                            get_p1_p2_from_normal(self.bed_wall.normal, s1_p1, s1_p2)

                        backline = DY_segment(stool_p1, stool_p2)
                        s1 = ChildStool()
                        s1.len = CHIDL_STOOL[-2]
                        s1.set_pos(backline, s1.len)
                        self.ele_list.append(s1)

                # 方案五：没有凳子
                if stool_len == CHIDL_STOOL[0] and door_mainwall_dis < table_len2:
                    t_p1 = childplay_p1 - \
                           self.bed_wall.normal.p2 * play_len
                    t_p2 = t_p1 - self.door_wall.normal.p2 * table_len

                    table_p1, table_p2 = DY_segment. \
                        get_p1_p2_from_normal(p_op_wall.normal, t_p1, t_p2)

                    backline = DY_segment(table_p1, table_p2)
                    t = ChildTable()
                    t.len = table_len
                    t.set_pos(backline, t.len)
                    self.ele_list.append(t)

                # 5.放置帐篷
                if tent_len > 0 and bed_tent_len > 0:
                    tent_len = min(tent_len, bed_tent_len)
                    tent_p1 = closet_p2 + self.bed_wall.normal.p2 * (CHILDCLOSET_LEN + TENT_OFFSET + tent_len)-\
                              self.door_wall.normal.p2 * TENT_OFFSET
                    tent_p2 = tent_p1 - self.door_wall.normal.p2 * tent_len
                    childtent_p1, childtent_p2 = DY_segment. \
                        get_p1_p2_from_normal(p_op_wall.normal, tent_p1, tent_p2)

                    backline = DY_segment(childtent_p1, childtent_p2)
                    tent = ChildTent()
                    tent.len = tent_len
                    tent.set_pos(backline, tent.len)
                    self.ele_list.append(tent)

                if tent_len > 0 and bed_tent_len == 0:
                    bed_center = b.boundary.polygon.centroid
                    bed_dis = opposite_wall[0].line.distance(bed_center) - bed_width
                    if bed_dis > tent_len:
                        tent_p1 = closet_p1 + self.bed_wall.normal.p2 * (CHILDCLOSET_LEN + DIS_CHILDCLOSET + tent_len)
                        tent_p2 = tent_p1 - self.door_wall.normal.p2 * tent_len
                        childtent_p1, childtent_p2 = DY_segment. \
                            get_p1_p2_from_normal(p_op_wall.normal, tent_p1, tent_p2)

                        backline = DY_segment(childtent_p1, childtent_p2)
                        tent = ChildTent()
                        tent.len = tent_len
                        tent.set_pos(backline, tent.len)
                        self.ele_list.append(tent)

                if tent_len == 0 and bed_tent_len > 0:
                    table_center = t.boundary.polygon.centroid
                    table_dis = self.bed_wall.line.distance(table_center) - int(table_len / 2) - CHIDL_STOOL[2]
                    if table_dis > CHILD_TENT[-2]:
                            tent_p1 = b_p1 + self.door_wall.normal.p2 * DIS_BED
                            tent_p2 = tent_p1 + self.door_wall.normal.p2 * CHILD_TENT[-2]
                            childtent_p1, childtent_p2 = DY_segment. \
                                get_p1_p2_from_normal(self.bed_wall.normal, tent_p1, tent_p2)

                            backline = DY_segment(childtent_p1, childtent_p2)
                            tent = ChildTent()
                            tent.len = CHILD_TENT[-2]
                            tent.set_pos(backline, tent.len)
                            self.ele_list.append(tent)

        else:
            self.run411_another()

        return True

    def run411_another(self):

        # 1.判断床所在的墙，放置床
        door = get_eles(self.ele_list, CommonElement.Door)[0]
        door_center = door.boundary.polygon.centroid
        self.main_win_wall = self.vir_win
        self.door_wall = self.near_door_wall
        self.bed_wall = self.op_door_wall

        bed_clo_wall = get_opposite_bounds(self.door_wall, self.boundary)
        if bed_clo_wall[0].seg.length > bed_clo_wall[-1].seg.length:
            bed_clo_wall[0] = bed_clo_wall[0]
        else:
            bed_clo_wall[0] = bed_clo_wall[-1]

        bed_door_dis = self.bed_wall.line.distance(door_center) - int(CHILD_DOOR/2)
        if bed_door_dis < BED_LEN[0]:
            # 根据表格取床、衣柜、帐篷活动区最优值
            bed_play_dis = self.bed_wall.seg.length
            childbed_nearst_df = self.childbed_df.loc[self.childbed_df.childsum_len <= bed_play_dis]
            childbed_nearst_df = childbed_nearst_df.ix[childbed_nearst_df.childsum_len.idxmax]

            bed_width = childbed_nearst_df["childbed_len"]
            play_width = childbed_nearst_df["childplay_len"]
            table_len = childbed_nearst_df["childtable_len"]
            stool_len = childbed_nearst_df["childstool_len"]
            tent_len = childbed_nearst_df["childtent_len"]
            # 判断门所在的墙是否有窗户
            b_p0 = self.bed_wall.seg.intersection(bed_clo_wall[0].seg)[0]
            if bed_clo_wall[0] == self.main_win_wall:
                b_p0 = b_p0 + self.main_win_wall.normal.p2 * DIS_CURTAIN
            else:
                b_p0 = b_p0

            if self.bed_wall == self.main_win_wall:
                b_p0 = b_p0 + self.main_win_wall.normal.p2 * DIS_CURTAIN
            else:
                b_p0 = b_p0

            b_p1 = b_p0 + bed_clo_wall[0].normal.p2 * bed_width
            bl_bed_p1, bl_bed_p2 = DY_segment. \
                get_p1_p2_from_normal(self.bed_wall.normal, b_p0, b_p1)

            backline = DY_segment(bl_bed_p1, bl_bed_p2)
            b = Bed()
            b.len = BED_LEN[0]
            b.set_pos(backline, b.len)
            self.ele_list.append(b)

            # 2.放置儿童衣柜
            bed_clo_dis = bed_clo_wall[0].line.distance(door_center) - int(CHILD_DOOR / 2)
            if bed_clo_dis > CHILDCLOSET_WIDTH[-1]:
                clo_len = CHILDCLOSET_WIDTH[-1]
            else:
                clo_len = CHILDCLOSET_WIDTH[-1]

            bed_opposite_wall = get_opposite_bounds(self.bed_wall, self.boundary)
            closet_p0 = bed_clo_wall[0].seg.intersection(bed_opposite_wall[0].seg)[0]

            # 判断窗户位置
            if bed_clo_wall[0] == self.main_win_wall:
                closet_p0 = closet_p0 + self.main_win_wall.normal.p2 * DIS_CURTAIN
            else:
                closet_p0 = closet_p0

            if bed_opposite_wall[0] == self.main_win_wall:
                closet_p1 = closet_p0 + self.main_win_wall.normal.p2 * DIS_CURTAIN
            else:
                closet_p1 = closet_p0
            closet_p2 = closet_p1 + bed_clo_wall[0].normal.p2 * clo_len
            clo_bed_p1, clo_bed_p2 = DY_segment. \
                get_p1_p2_from_normal(bed_opposite_wall[0].normal, closet_p2, closet_p1)
            backline = DY_segment(clo_bed_p1, clo_bed_p2)
            clo = ChildCloset(backline)
            self.ele_list.append(clo)

            # 放置儿童玩具柜
            p_p0 = self.bed_wall.seg.intersection(self.door_wall.seg)[0]
            if self.door_wall == self.main_win_wall:
                p_p0 = p_p0 + self.main_win_wall.normal.p2 * DIS_CURTAIN
            else:
                p_p0 = p_p0

            if self.bed_wall == self.main_win_wall:
                p_p0 = p_p0 + self.main_win_wall.normal.p2 * DIS_CURTAIN
            else:
                p_p0 = p_p0

            p_p1 = p_p0 + self.door_wall.normal.p2 * play_width
            play_p1, play_p2 = DY_segment. \
                get_p1_p2_from_normal(self.bed_wall.normal, p_p0, p_p1)

            backline = DY_segment(play_p1, play_p2)
            p = ChildPlay()
            if bed_door_dis >= CHILD_PLAY_WIDTH[-1]:
                p_len = CHILD_PLAY_WIDTH[-1]
            else:
                p_len = CHILD_PLAY_WIDTH[-3]
            p.len = p_len
            p.set_pos(backline, p.len)
            self.ele_list.append(p)

            # 4.放置游戏桌和凳子
            if play_width != 0 and table_len != 0:
                table_len1 = table_len + stool_len + DIS_CHILD_TABLE * 2
                table_len2 = table_len + int(stool_len / 2) + DIS_CHILD_TABLE
                door_mainwall_dis = self.bed_wall.line.distance(door_center) - int(CHILD_DOOR / 2)

                # 方案一：四个凳子
                if door_mainwall_dis >= table_len1 and stool_len >= CHIDL_STOOL[-2]:
                    t_p1 = p_p1 + \
                           self.bed_wall.normal.p2 * (DIS_CHILD_TABLE + int(stool_len / 2)) + \
                           self.door_wall.normal.p2 * (DIS_CHILD_TABLE + int(stool_len / 2))

                    t_p2 = t_p1 + self.door_wall.normal.p2 * table_len

                    t_p3 = t_p1 + self.bed_wall.normal.p2 * table_len
                    table_p1, table_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, t_p1, t_p2)

                    backline = DY_segment(table_p1, table_p2)
                    t = ChildTable()
                    t.len = table_len
                    t.set_pos(backline, t.len)
                    self.ele_list.append(t)

                    # 放置游戏凳子
                    s1_p0 = t_p1 + self.bed_wall.normal.p2 * int(table_len / 2) - \
                            self.bed_wall.normal.p2 * int(stool_len / 2)

                    s1_p1 = s1_p0 - self.door_wall.normal.p2 * int(stool_len / 2)
                    s1_p2 = s1_p0 + self.door_wall.normal.p2 * int(stool_len / 2)

                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s1_p1, s1_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s1 = ChildStool()
                    s1.len = stool_len
                    s1.set_pos(backline, s1.len)
                    self.ele_list.append(s1)

                    s3_p1 = s1_p2 + self.door_wall.normal.p2 * int(table_len)
                    s3_p2 = s1_p1 + self.door_wall.normal.p2 * int(table_len)

                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s3_p1, s3_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s3 = ChildStool()
                    s3.len = stool_len
                    s3.set_pos(backline, s3.len)
                    self.ele_list.append(s3)

                    s2_p0 = t_p1 + self.door_wall.normal.p2 * (int(table_len / 2) - int(stool_len / 2))
                    s2_p1 = s2_p0 - self.bed_wall.normal.p2 * int(stool_len / 2)
                    s2_p2 = s2_p1 + self.door_wall.normal.p2 * stool_len

                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s2_p1, s2_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s2 = ChildStool()
                    s2.len = stool_len
                    s2.set_pos(backline, s2.len)
                    self.ele_list.append(s2)

                    s4_p1 = s2_p2 + self.bed_wall.normal.p2 * int(table_len)
                    s4_p2 = s2_p1 + self.bed_wall.normal.p2 * int(table_len)
                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s4_p1, s4_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s4 = ChildStool()
                    s4.len = stool_len
                    s4.set_pos(backline, s4.len)
                    self.ele_list.append(s4)

                # 方案二：三个凳子
                if stool_len >= CHIDL_STOOL[-2] and door_mainwall_dis >= table_len2 and door_mainwall_dis < table_len1:
                    t_p1 = p_p1 + \
                           self.bed_wall.normal.p2 * (DIS_CHILD_TABLE + int(stool_len / 2)) + \
                           self.door_wall.normal.p2 * (DIS_CHILD_TABLE + int(stool_len / 2))
                    t_p2 = t_p1 + self.door_wall.normal.p2 * table_len
                    t_p3 = t_p1 + self.bed_wall.normal.p2 * table_len

                    table_p1, table_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, t_p1, t_p2)

                    backline = DY_segment(table_p1, table_p2)
                    t = ChildTable()
                    t.len = table_len
                    t.set_pos(backline, t.len)
                    self.ele_list.append(t)

                    # 放置游戏凳子
                    s1_p0 = t_p1 + self.bed_wall.normal.p2 * int(table_len / 2) - \
                            self.bed_wall.normal.p2 * int(stool_len / 2)

                    s1_p1 = s1_p0 - self.door_wall.normal.p2 * int(stool_len / 2)
                    s1_p2 = s1_p0 + self.door_wall.normal.p2 * int(stool_len / 2)

                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s1_p1, s1_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s1 = ChildStool()
                    s1.len = stool_len
                    s1.set_pos(backline, s1.len)
                    self.ele_list.append(s1)

                    s3_p1 = s1_p2 + self.door_wall.normal.p2 * int(table_len)
                    s3_p2 = s1_p1 + self.door_wall.normal.p2 * int(table_len)

                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s3_p1, s3_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s3 = ChildStool()
                    s3.len = stool_len
                    s3.set_pos(backline, s3.len)
                    self.ele_list.append(s3)

                    s2_p0 = t_p1 + self.door_wall.normal.p2 * (int(table_len / 2) - int(stool_len / 2))
                    s2_p1 = s2_p0 - self.bed_wall.normal.p2 * int(stool_len / 2)
                    s2_p2 = s2_p1 + self.door_wall.normal.p2 * stool_len

                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s2_p1, s2_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s2 = ChildStool()
                    s2.len = stool_len
                    s2.set_pos(backline, s2.len)
                    self.ele_list.append(s2)

                if stool_len >= CHIDL_STOOL[1] and stool_len < CHIDL_STOOL[-2]:
                    if door_mainwall_dis > table_len1:

                        t_p1 = p_p1 + \
                               self.bed_wall.normal.p2 * (DIS_CHILD_TABLE + stool_len)
                        t_p2 = t_p1 + self.door_wall.normal.p2 * table_len
                        t_p3 = t_p1 + self.bed_wall.normal.p2 * table_len

                        table_p1, table_p2 = DY_segment. \
                            get_p1_p2_from_normal(self.bed_wall.normal, t_p1, t_p2)

                        backline = DY_segment(table_p1, table_p2)
                        t = ChildTable()
                        t.len = table_len
                        t.set_pos(backline, t.len)
                        self.ele_list.append(t)

                        s3_p0 = t_p2 + self.bed_wall.normal.p2 * int(table_len / 2) - \
                                self.bed_wall.normal.p2 * int(stool_len)
                        s3_p1 = s3_p0 + self.door_wall.normal.p2 * int(stool_len)
                        s3_p2 = s3_p0 - self.door_wall.normal.p2 * int(stool_len)
                        stool_p1, stool_p2 = DY_segment. \
                            get_p1_p2_from_normal(self.bed_wall.normal, s3_p1, s3_p2)

                        backline = DY_segment(stool_p1, stool_p2)
                        s3 = ChildStool()
                        s3.len = stool_len*2
                        s3.set_pos(backline, s3.len)
                        self.ele_list.append(s3)

                        s2_p0 = t_p1 + self.door_wall.normal.p2 * (int(table_len / 2) - stool_len)
                        s2_p1 = s2_p0 - self.bed_wall.normal.p2 * stool_len
                        s2_p2 = s2_p1 + self.door_wall.normal.p2 * stool_len*2

                        stool_p1, stool_p2 = DY_segment. \
                            get_p1_p2_from_normal(self.bed_wall.normal, s2_p1, s2_p2)

                        backline = DY_segment(stool_p1, stool_p2)
                        s2 = ChildStool()
                        s2.len = stool_len*2
                        s2.set_pos(backline, s2.len)
                        self.ele_list.append(s2)

                        s4_p1 = s2_p2 + self.bed_wall.normal.p2 * int(table_len)
                        s4_p2 = s2_p1 + self.bed_wall.normal.p2 * int(table_len)
                        stool_p1, stool_p2 = DY_segment. \
                            get_p1_p2_from_normal(self.bed_wall.normal, s4_p1, s4_p2)

                        backline = DY_segment(stool_p1, stool_p2)
                        s4 = ChildStool()
                        s4.len = stool_len*2
                        s4.set_pos(backline, s4.len)
                        self.ele_list.append(s4)

                # 方案三：两个凳子
                if stool_len >= CHIDL_STOOL[-2] and door_mainwall_dis < table_len2:
                    t_p1 = p_p1 + \
                           self.door_wall.normal.p2 * (DIS_CHILD_TABLE + int(stool_len / 2))
                    t_p2 = t_p1 + self.door_wall.normal.p2 * table_len
                    t_p3 = t_p1 + self.bed_wall.normal.p2 * table_len

                    table_p1, table_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, t_p1, t_p2)

                    backline = DY_segment(table_p1, table_p2)
                    t = ChildTable()
                    t.len = table_len
                    t.set_pos(backline, t.len)
                    self.ele_list.append(t)

                    # 放置游戏凳子
                    s1_p0 = t_p1 + self.bed_wall.normal.p2 * int(table_len / 2) - \
                            self.bed_wall.normal.p2 * int(stool_len / 2)

                    s1_p1 = s1_p0 - self.door_wall.normal.p2 * int(stool_len / 2)
                    s1_p2 = s1_p0 + self.door_wall.normal.p2 * int(stool_len / 2)

                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s1_p1, s1_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s1 = ChildStool()
                    s1.len = stool_len
                    s1.set_pos(backline, s1.len)
                    self.ele_list.append(s1)

                    s3_p1 = s1_p2 + self.door_wall.normal.p2 * int(table_len)
                    s3_p2 = s1_p1 + self.door_wall.normal.p2 * int(table_len)

                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s3_p1, s3_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s3 = ChildStool()
                    s3.len = stool_len
                    s3.set_pos(backline, s3.len)
                    self.ele_list.append(s3)

                if stool_len == CHIDL_STOOL[0] and door_mainwall_dis > table_len1 + CHILD_TABLE[-2]:
                    t_p1 = p_p1 + \
                           self.bed_wall.normal.p2 * (DIS_CHILD_TABLE + int(CHIDL_STOOL[-2]/2))
                    t_p2 = t_p1 + self.door_wall.normal.p2 * table_len
                    t_p3 = t_p1 + self.bed_wall.normal.p2 * table_len

                    table_p1, table_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, t_p1, t_p2)

                    backline = DY_segment(table_p1, table_p2)
                    t = ChildTable()
                    t.len = CHILD_TABLE[0]
                    t.set_pos(backline, t.len)
                    self.ele_list.append(t)

                    s2_p0 = t_p1 + self.door_wall.normal.p2 * (int(table_len / 2) - int(CHIDL_STOOL[-2] / 2))
                    s2_p1 = s2_p0 - self.bed_wall.normal.p2 * int(CHIDL_STOOL[-2] / 2)
                    s2_p2 = s2_p1 + self.door_wall.normal.p2 * CHIDL_STOOL[-2]

                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s2_p1, s2_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s2 = ChildStool()
                    s2.len = CHIDL_STOOL[-2]
                    s2.set_pos(backline, s2.len)
                    self.ele_list.append(s2)

                    s4_p1 = s2_p2 + self.bed_wall.normal.p2 * int(table_len)
                    s4_p2 = s2_p1 + self.bed_wall.normal.p2 * int(table_len)
                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s4_p1, s4_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s4 = ChildStool()
                    s4.len = CHIDL_STOOL[-2]
                    s4.set_pos(backline, s4.len)
                    self.ele_list.append(s4)

                if stool_len == CHIDL_STOOL[1] or stool_len == CHIDL_STOOL[2]:
                    if door_mainwall_dis >= table_len2 and door_mainwall_dis < table_len1:
                        t_p1 = p_p1
                        t_p2 = t_p1 + self.door_wall.normal.p2 * table_len
                        t_p3 = t_p1 + self.bed_wall.normal.p2 * table_len

                        table_p1, table_p2 = DY_segment. \
                            get_p1_p2_from_normal(self.bed_wall.normal, t_p1, t_p2)

                        backline = DY_segment(table_p1, table_p2)
                        t = ChildTable()
                        t.len = table_len
                        t.set_pos(backline, t.len)
                        self.ele_list.append(t)

                        s3_p0 = t_p2 + self.bed_wall.normal.p2 * int(table_len / 2) - \
                                self.bed_wall.normal.p2 * stool_len

                        s3_p1 = s3_p0 - self.door_wall.normal.p2 * stool_len
                        s3_p2 = s3_p0 + self.door_wall.normal.p2 * stool_len

                        stool_p1, stool_p2 = DY_segment. \
                            get_p1_p2_from_normal(self.bed_wall.normal, s3_p1, s3_p2)

                        backline = DY_segment(stool_p1, stool_p2)
                        s3 = ChildStool()
                        s3.len = stool_len * 2
                        s3.set_pos(backline, s3.len)
                        self.ele_list.append(s3)

                        s4_p0 = t_p3 + self.door_wall.normal.p2 * (int(table_len / 2) - stool_len)
                        s4_p1 = s4_p0 - self.bed_wall.normal.p2 * stool_len
                        s4_p2 = s4_p1 + self.door_wall.normal.p2 * stool_len * 2

                        stool_p1, stool_p2 = DY_segment. \
                            get_p1_p2_from_normal(self.bed_wall.normal, s4_p1, s4_p2)

                        backline = DY_segment(stool_p1, stool_p2)
                        s4 = ChildStool()
                        s4.len = stool_len * 2
                        s4.set_pos(backline, s4.len)
                        self.ele_list.append(s4)

                # 方案四：只有第一个凳子
                if stool_len == CHIDL_STOOL[1] or stool_len == CHIDL_STOOL[2]:
                    if door_mainwall_dis < table_len2:
                        table_len1 = table_len + stool_len * 2 + DIS_CHILD_TABLE * 2
                        table_len2 = table_len + stool_len + DIS_CHILD_TABLE
                        t_p1 = p_p1
                        t_p2 = t_p1 + self.door_wall.normal.p2 * table_len
                        t_p3 = t_p1 + self.bed_wall.normal.p2 * table_len

                        table_p1, table_p2 = DY_segment. \
                            get_p1_p2_from_normal(self.bed_wall.normal, t_p1, t_p2)

                        backline = DY_segment(table_p1, table_p2)
                        t = ChildTable()
                        t.len = table_len
                        t.set_pos(backline, t.len)
                        self.ele_list.append(t)

                        s3_p0 = t_p2 + self.bed_wall.normal.p2 * (int(table_len / 2) - stool_len)
                        s3_p1 = s3_p0 - self.door_wall.normal.p2 * stool_len
                        s3_p2 = s3_p1 + self.door_wall.normal.p2 * stool_len * 2

                        stool_p1, stool_p2 = DY_segment. \
                            get_p1_p2_from_normal(self.bed_wall.normal, s3_p1, s3_p2)

                        backline = DY_segment(stool_p1, stool_p2)
                        s3 = ChildStool()
                        s3.len = stool_len * 2
                        s3.set_pos(backline, s3.len)
                        self.ele_list.append(s3)

                if stool_len == CHIDL_STOOL[0] and door_mainwall_dis >= table_len2 and door_mainwall_dis < table_len1 + CHILD_TABLE[-2]:

                    t_p1 = p_p1
                    t_p2 = t_p1 + self.door_wall.normal.p2 * table_len
                    t_p3 = t_p1 + self.bed_wall.normal.p2 * table_len
                    table_p1, table_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, t_p1, t_p2)
                    backline = DY_segment(table_p1, table_p2)
                    t = ChildTable()
                    t.len = table_len
                    t.set_pos(backline, t.len)
                    self.ele_list.append(t)

                    s4_p0 = t_p3 + self.door_wall.normal.p2 * int(table_len / 2) - \
                            self.door_wall.normal.p2 * int(CHIDL_STOOL[-2]/2)

                    s4_p1 = s4_p0 - self.bed_wall.normal.p2 * int(CHIDL_STOOL[-2]/2)
                    s4_p2 = s4_p1 + self.door_wall.normal.p2 * CHIDL_STOOL[-2]

                    stool_p1, stool_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, s4_p1, s4_p2)

                    backline = DY_segment(stool_p1, stool_p2)
                    s4 = ChildStool()
                    s4.len = CHIDL_STOOL[-2]
                    s4.set_pos(backline, s4.len)
                    self.ele_list.append(s4)

                # 方案五：没有凳子
                if stool_len == CHIDL_STOOL[0] and door_mainwall_dis < table_len2:

                    t_p1 = p_p1
                    t_p2 = t_p1 + self.door_wall.normal.p2 * table_len

                    table_p1, table_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, t_p1, t_p2)

                    backline = DY_segment(table_p1, table_p2)
                    t = ChildTable()
                    t.len = table_len
                    t.set_pos(backline, t.len)
                    self.ele_list.append(t)

            # 5.放置帐篷
            if tent_len > 0:
                tent_p1 = b_p1 + bed_clo_wall[0].normal.p2 * (DIS_BED + TENT_OFFSET) + \
                          self.bed_wall.normal.p2 * TENT_OFFSET
                tent_p2 = tent_p1 - self.door_wall.normal.p2 * tent_len
                childtent_p1, childtent_p2 = DY_segment. \
                    get_p1_p2_from_normal(self.bed_wall.normal, tent_p1, tent_p2)

                backline = DY_segment(childtent_p1, childtent_p2)
                tent = ChildTent()
                tent.len = tent_len
                tent.set_pos(backline, tent.len)
                self.ele_list.append(tent)

        return True

    def __init(self):
        # 儿童衣柜、帐篷活动区、游戏桌、凳子、凳子区间创建表格
        sum_length_lst = []
        play_lst = []
        table_lst = []
        stool_lst = []
        tent_lst = []
        for play_b in CHILD_PLAY_LEN:
            for table_b in CHILD_TABLE:
                for stool_b in CHIDL_STOOL:
                    for tent_b in CHILD_TENT:
                        play_lst.append(play_b)
                        table_lst.append(table_b)
                        stool_lst.append(stool_b)
                        tent_lst.append(tent_b)

                        # 儿童衣柜、帐篷活动区、游戏桌、凳子、凳子区间
                        sum_len = DIS_CHILD_TABLE * 2 + CHILDCLOSET_LEN + DIS_CHILD_TENT + \
                                  play_b + table_b + stool_b + tent_b
                        sum_length_lst.append(sum_len)

        pd_dict = {
            "sum_len": sum_length_lst,
            "play_len": play_lst,
            "table_len": table_lst,
            "stool_len": stool_lst,
            "tent_len": tent_lst
        }
        self.df = pd.DataFrame(pd_dict)
        self.df = self.df.sort_values(by='sum_len')

        # 床、衣柜、帐篷活动区建立表格
        bed_lst = []
        closet_lst = []
        ten_lst = []
        bed_sum = []
        for bed in BED_WIDTH:
            for clo in CHILDCLOSET_WIDTH:
                for tent in CHILD_TENT:
                    bed_lst.append(bed)
                    closet_lst.append(clo)
                    ten_lst.append(tent)

                    bed_clo_sum = bed + clo + tent + DIS_BED + DIS_CURTAIN
                    bed_sum.append(bed_clo_sum)

        bed_dict = {
            "sum_len": bed_sum,
            "bed_len": bed_lst,
            "closet_len": closet_lst,
            "tent_len": ten_lst
        }
        self.bed_df = pd.DataFrame(bed_dict)
        self.bed_df = self.bed_df.sort_values(by='sum_len')

        # 床、玩具柜、帐篷活动区、桌子、凳子建立表格
        childbed_lst = []
        childplay_lst = []
        childtable_lst = []
        childstool_lst = []
        childten_lst = []
        child_sum = []
        table_list = [0]
        for i in CHILD_TABLE:
            table_list.append(i)
        for bed in BED_WIDTH:
            for play in CHILD_PLAY_LEN:
                for table in table_list:
                    for stool in CHIDL_STOOL:
                        for ten in CHILD_TENT:
                            childbed_lst.append(bed)
                            childplay_lst.append(play)
                            childtable_lst.append(table)
                            childstool_lst.append(stool)
                            childten_lst.append(ten)

                            child_paly_sum = bed + play + table + stool + ten + DIS_BED + DIS_CURTAIN + DIS_CHILD_TABLE * 2
                            child_sum.append(child_paly_sum)

        childbed_dict = {
            "childsum_len": child_sum,
            "childbed_len": childbed_lst,
            "childplay_len": childplay_lst,
            "childtable_len": childtable_lst,
            "childstool_len": childstool_lst,
            "childtent_len": childten_lst
        }
        self.childbed_df = pd.DataFrame(childbed_dict)
        self.childbed_df = self.childbed_df.sort_values(by='childsum_len')