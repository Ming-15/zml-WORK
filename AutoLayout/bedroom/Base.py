# -*- coding:utf-8 -*-
import pandas as pd

import AutoLayout.CommonElement as CommonElement
import AutoLayout.helpers as helpers
import AutoLayout.main_bedroom.utility as mb_uti
from AutoLayout.bedroom.Element import *
from AutoLayout.main_bedroom.utility import *


class Bedroom(Region):
    def __init__(self):
        # 调用父类中的初始化方法,防止覆盖
        super(Bedroom, self).__init__()
        self.main_win_wall = None
        self.__init()

        self.win_list = []
        ''' ---attr for virtual ---- ML --- '''
        self.door_list = []
        self.vir_door_list = []
        self.entrance = None
        self.vir_win_list = []
        self.vir_win = None

    def run(self):
        #定义一个字典,键为户型的类型,值为户型类型对应的函数
        arrangement_dict = {
            (4, 1, 1): self.run411,  # 顶点，门，窗
            (6, 1, 1): self.run611,
        }
        # self.boundary.polygon.vertices户型的顶点    比如411等
        key = (len(self.boundary.polygon.vertices), self.doors, self.windows)
        # 判断输入的户型是否满足字典中的key
        if not arrangement_dict.get(key, False) or self.borders != 0:
            # raise Exception("客房暂时不支持这种户型")
            self.run_anytype()
            return True
        # 获取键对应的值,并调用相应的函数
        res = arrangement_dict.get(key)()
        # # print(res)

    def get_entrance_point(self, vir_dr_mid_p):
        vir_ver_list = []
        for p in self.virtual_boundary.polygon.vertices:
            long = helpers.point_distance(p, vir_dr_mid_p)
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
                dr = helpers.get_vir_door(door, self.boundary)
                bal_dr = dr
                bal_dr_list.append(dr)
            elif 'Bathroom' in door.connect_list or 's' in door.connect_list:
                ''' ---这儿添加不是入口的门的种类，后期避开---'''
                dr = helpers.get_vir_door(door, self.boundary)
                self.avoid_dr_win[0].append(dr)
            else:
                '''待完全定型后决定是过道还是什么情况的门为入口'''
                entrance_list.append(door)
        if len(entrance_list) == 1:
            self.entrance = entrance_list[0]

        else:
            # print('这个门数量奇葩')
            self.entrance = entrance_list[0]
        vir_door = helpers.get_vir_door(self.entrance, self.boundary)
        vir_door_line = helpers.get_mother_boundary(vir_door, self.boundary)
        '''返回虚映射门'''
        return vir_door, vir_door_line, bal_tag, bal_dr

    def run_anytype(self):
        def set_bed(sp, rl, vir_win, be_len, bes_len, began_dis, tag):
            p1 = sp + vir_win.normal.p2 * began_dis
            p2 = p1 + vir_win.normal.p2 * be_len
            bed_p1, bed_p2 = DY_segment.get_p1_p2_from_normal(rl.normal, p1, p2)
            v_backline = DY_segment(bed_p1, bed_p2)
            bed = Bed()
            bed.set_pos(v_backline, bed.len)
            self.ele_list.append(bed)
            # 两个床头柜
            besp1 = p1
            besp2 = besp1 - vir_win.normal.p2 * bes_len
            bes1, bes2 = DY_segment.get_p1_p2_from_normal(rl.normal, besp1, besp2)
            backline = DY_segment(bes1, bes2)
            bes = NightTable()
            bes.ID = 0
            bes.set_pos(backline, bes.len)
            self.ele_list.append(bes)
            if tag:  # tag表示两个床头柜
                besp1 = p2
                besp2 = besp1 + vir_win.normal.p2 * bes_len
                bes1, bes2 = DY_segment.get_p1_p2_from_normal(rl.normal, besp1, besp2)
                backline = DY_segment(bes1, bes2)
                bes = NightTable()
                bes.ID = 0
                bes.set_pos(backline, bes.len)
                self.ele_list.append(bes)

        def set_cloth(p, bl_dir, bl_normal, ele_len, ele):
            ps1 = p
            ps2 = p + bl_dir.normal.p2 * ele_len
            op_normal = helpers.get_op_normal(bl_normal.normal)
            p1, p2 = DY_segment.get_p1_p2_from_normal(helpers.get_op_normal(bl_normal.normal), ps1, ps2)
            v_backline = DY_segment(p1, p2)
            if ele:
                el = Closet(v_backline)
            else:
                el = Drawers(v_backline)
            self.ele_list.append(el)

        def vector_replaced(rl, vir_win):  # 布局边，阳台边，
            def one_or_two(remain_len):
                if remain_len > 900:
                    remain_len = remain_len / 2
                    bes_len = helpers.best_fit(BEDSIDE_NIGHTTABLE_WIDTH, remain_len)
                    return 1, bes_len
                else:
                    bes_len = helpers.best_fit(BEDSIDE_NIGHTTABLE_WIDTH, remain_len)
                    return 0, bes_len

            def rl_replace(cloth_re_len):
                r_rl_len = rl_len - cloth_re_len
                remain_len = r_rl_len
                if remain_len > max(BED_WIDTH) + min(BEDSIDE_NIGHTTABLE_WIDTH):
                    t = 1
                elif remain_len > min(BED_WIDTH) + min(BEDSIDE_NIGHTTABLE_WIDTH):
                    t = 2
                else:
                    t = 0
                if t == 1:
                    be_len = max(BED_WIDTH)
                    r_rl_len -= be_len
                    tag, bes_len = one_or_two(r_rl_len)

                elif t == 2:
                    bes_len = min(BEDSIDE_NIGHTTABLE_WIDTH)
                    r_rl_len -= bes_len
                    be_len = helpers.best_fit(BED_WIDTH, r_rl_len)
                    r_rl_len = r_rl_len + bes_len - be_len
                    tag, bes_len = one_or_two(r_rl_len)
                else:
                    # too small
                    be_len = min(BED_WIDTH)
                    bes_len = min(BEDSIDE_NIGHTTABLE_WIDTH)
                    tag = 0
                return t, be_len, bes_len, tag

            # 初始化
            too_small_tag = 0
            be_len = bes_len = tag = 0
            sp = rl.seg.intersection(vir_win.seg)[0]
            ep = helpers.another_p(rl, sp)
            np = helpers.another_p(vir_win, sp)
            rl_len = rl.seg.length - win_move_dis
            # 优先计算两个放置边的剩余长度
            if dr.line.is_parallel(rl.line):
                dis_rl_dr = rl.line.distance(dr_mid_p) - (DOOR_LENGTH - DOOR_WALL_LEN)
                dis_win_dr = vir_win.line.distance(dr_mid_p) - dr.seg.length / 2
            else:
                dis_rl_dr = rl.line.distance(dr_mid_p) - dr.seg.length / 2
                dis_win_dr = vir_win.line.distance(dr_mid_p) - (DOOR_LENGTH - DOOR_WALL_LEN)
                # 虚拟门映射情况下，同边需要避开吧的距离，# 正常门就是正常门数据
                # 反正优先考虑的都是dis_rl_dr
            if dis_win_dr > min(CLOSET_WIDTH) and vir_win.seg.length > BED_LEN + BED_END_THRE_DIS + CLOSET_LEN:
                # 房间备用位置够放衣柜
                cloth_re_len = CLOSET_LEN + C_FRONT
                t_rl_tag, be_len, bes_len, tag = rl_replace(cloth_re_len)
                if t_rl_tag == 0:
                    t, be_len, bes_len, tag = rl_replace(0)  # 这个t这里没有也行
                    if t == 0:
                        # print('太小户,不放衣柜也放不下')
                        pass
                    # 衣柜放边角
                    clo_len = helpers.best_fit(CLOSET_WIDTH, dis_win_dr)
                    p = np + vir_win.normal.p2 * win_move_dis
                    set_cloth(p, vir_win, rl, clo_len, 1)
                else:
                    # 衣柜正常放置
                    clo_len = helpers.best_fit(CLOSET_WIDTH, dis_rl_dr)
                    set_cloth(ep, rl, vir_win, clo_len, 1)

            elif dis_win_dr > min(DRAWER_WIDTH) and vir_win.seg.length > BED_LEN + BED_END_THRE_DIS + DRAWER_LEN:
                cloth_re_len = DRAWER_LEN + C_FRONT
                t_rl_tag, be_len, bes_len, tag = rl_replace(cloth_re_len)
                if t_rl_tag == 0:
                    t, be_len, bes_len, tag = rl_replace(0)
                    if t == 0:
                        too_small_tag = 1
                        # print('太小户')
                    dra_len = helpers.best_fit(DRAWER_WIDTH, dis_win_dr)
                    p = np + vir_win.normal.p2 * win_move_dis
                    set_cloth(p, vir_win, rl, dra_len, 0)
                    # 柜放边角
                else:
                    dra_len = helpers.best_fit(DRAWER_WIDTH, dis_rl_dr)
                    set_cloth(ep, rl, vir_win, dra_len, 0)


            else:
                # 窄
                cloth_re_len = CLOSET_LEN + C_FRONT
                t_rl_tag, be_len, bes_len, tag = rl_replace(cloth_re_len)
                if t_rl_tag == 0:
                    # 衣柜不行，换小提柜
                    cloth_re_len = DRAWER_LEN + C_FRONT
                    t, be_len, bes_len, tag = rl_replace(cloth_re_len)  # 这个t这里没有也行
                    if t == 0:
                        # print('放不下柜子了')
                        pass
                    # 衣柜放边角
                    else:

                        dra_len = helpers.best_fit(DRAWER_WIDTH, dis_rl_dr)
                        set_cloth(ep, rl, vir_win, dra_len, 0)
                else:
                    clo_len = helpers.best_fit(CLOSET_WIDTH, dis_rl_dr)
                    set_cloth(ep, rl, vir_win, clo_len, 1)

            began_dis = win_move_dis + bes_len
            set_bed(sp, rl, vir_win, be_len, bes_len, began_dis, tag)

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
            inner = helpers.get_inner_point(self.boundary)
            inner_list = []
            for i in inner:
                if helpers.is_inner_point(i, self.virtual_boundary) == 2:
                    inner_list.append(i)

            tp = None
            if vir_dr_tag == 1:  # 1 代表多种类型的吧
                for s in self.virtual_boundary.seg_list:
                    if s.seg.intersection(door_line.seg) != []:
                        tp = s.seg.intersection(door_line.seg)[0]
                        t_doorline = s
                        break
                if tp == None:
                    t_doorline = helpers.get_nearest_parallel_line(door_line, self.virtual_boundary)
                if True:
                    '''确定离把近的点'''
                    tp_list = []
                    for i in inner:
                        if t_doorline.seg.contains(i):
                            tp_list.append(i)
                    if tp_list == []:
                        # print('不合理')  # 但还是要继续进行
                        if True:
                            tp_list = helpers.get_adj_seg(a, self.virtual_boundary)
                            if tp_list[0].seg == t_doorline.seg:
                                t_doorline = tp_list[1]
                            else:
                                t_doorline = tp_list[0]
                            tdr = []
                            for i in tp_list:
                                tdr.append([i, helpers.point_distance(i, a)])
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
                            tdr.append([i, helpers.point_distance(i, a)])
                        tdr.sort(key=lambda x: x[1])
                        dr = DY_segment(a, tdr[1][0])
                        dr_mid_p = dr.seg.midpoint()
            else:
                tp_list = helpers.get_adj_seg(a, self.virtual_boundary)
                if tp_list[0].line.contains(dr_mid_p):
                    t_doorline = tp_list[1]
                else:
                    t_doorline = tp_list[0]
                for i in inner_list:
                    if t_doorline.seg.contains(i):
                        tp = i
                if tp == None:
                    # print('不合理')
                    pass
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
            self.vir_win = helpers.get_mother_boundary(bal_door, self.boundary)  # self.vir_win 就是指所在墙
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
                backline = helpers.get_nearest_parallel_line(self.vir_win, self.virtual_boundary)

            if backline.line.contains(dr_mid_p):
                # print('留个标记')
                pass

            main_curtain.set_pos(backline, main_curtain.len)
            self.ele_list.append(main_curtain)
            vir_win = backline  # 阳台位置信息，统一用vir——win
            win_mid_p = vir_win.seg.midpoint
        else:
            # 无窗户型
            win_move_dis = 0
            vir_win = helpers.get_opposite_bounds(door_line, self.virtual_boundary)[0]
            win_mid_p = vir_win.seg.midpoint

        '''现有标志，bal_tag 阳台标志，win_tag 虚拟窗标志，门的信息已经被虚拟门代替了。
                    door-line是门墙，
                '''
        '''-----下面开始其他组件，由门边信息和阳台边vir_win信息来决定-------'''
        tp_list = helpers.get_adj_seg(a, self.virtual_boundary)
        if tp_list[0].line.contains(dr_mid_p):
            near_door_wall = tp_list[1]
        else:
            near_door_wall = tp_list[0]
        far_door_wall = helpers.get_opposite_bounds(near_door_wall, self.virtual_boundary)[0]
        op_door_wall = helpers.get_opposite_bounds(door_line, self.virtual_boundary)[0]
        if vir_win.line.distance(dr_mid_p) == 0:
            # 将门假映射到对面
            # print('窗户在门墙这边，注意')
            door_line = op_door_wall
            dr_mid_p = helpers.another_p(near_door_wall, a)
            dr = DY_segment(dr_mid_p - op_door_wall.dir.p2 * 1, dr_mid_p + op_door_wall.dir.p2 * 1)
            vector_replaced(far_door_wall, vir_win)
        else:
            if door_line.line.is_parallel(vir_win.line):
                vector_replaced(far_door_wall, vir_win)
            # elif far_door_wall.line.contains(win_mid_p):
            else:
                vector_replaced(op_door_wall, vir_win)

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
        # print(intersec_list)
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

        # #通过翻转、旋转归一化户型，使得过道在左下角
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
        if xlen > BEDROOM_MAX_LEN or xlen < BEDROOM_MIN_LEN or \
                        ylen > BEDROOM_MAX_LEN or ylen < BEDROOM_MIN_LEN:
            self.run_anytype()
            return
        if abs(self.boundary.polygon.area) < BEDROOM_MIN_LEN * BEDROOM_MIN_LEN:
            self.run_anytype()
            return

        self.run411()

        return True

    def run411(self):
        (xmin, ymin, xmax, ymax) = self.boundary.polygon.bounds
        xlen = xmax - xmin
        ylen = ymax - ymin

        if xlen > BEDROOM_MAX_LEN or xlen < BEDROOM_MIN_LEN or \
                        ylen > BEDROOM_MAX_LEN or ylen < BEDROOM_MIN_LEN:
            self.run_anytype()
            return
        if abs(self.boundary.polygon.area) < BEDROOM_MIN_LEN * BEDROOM_MIN_LEN:
            self.run_anytype()
            return

        # 放置窗帘
        self.win_list, self.main_curtain, self.main_win_wall = \
            mb_uti.arrange_main_curtain(self.line_list, self.ele_list)
        # [<DY_Line.Window object at 0x00000236274FB4E0>] <CommonElement.Curtain object at 0x0000023627436048> <BaseClass.DY_segment object at 0x00000236274FB1D0>
        # 找到bed_wall
        # 从门对象的列表中取出门对象
        door = helpers.get_eles(self.ele_list, CommonElement.Door)[0]
        # 取出门的中心点坐标  即门四边形的中心
        door_center = door.boundary.polygon.centroid
        # 获取与窗户相邻的两堵墙
        adj_win_list = helpers.get_adjacent_bounds(self.main_win_wall, self.boundary)
        dis = 0
        for s in adj_win_list:
            dis0 = s.line.distance(door_center)
            if dis0 > dis:
                dis = dis0
                self.bed_wall = s
        # 得到bed_wall 与对面墙的距离
        opposite_walls = helpers.get_opposite_bounds(self.main_win_wall, self.boundary)
        # print(opposite_walls)
        # =======================================================================================
        lists1_l = []
        for i in opposite_walls:
            lists1_l.append(i.seg.length)
        max_length = max(lists1_l)
        # ===============================================================================================
        # 取得是主窗正对着的长度较长墙的垂直距离
        dis = [int(l.line.distance(self.main_win_wall.p1)) for l in opposite_walls if l.seg.length == max_length]
        dis = sorted(dis, reverse=True)[0]
        # 通过窗户与对面墙的距离，在表格中选择最接近的组合
        nearst_df = self.df.loc[self.df.sum_len <= (dis - CURTAIN_LEN)]
        nearst_df = nearst_df.ix[nearst_df.sum_len.idxmax]

        p0 = self.bed_wall.seg.intersection(self.main_win_wall.seg)[0]
        p0 = p0 + self.main_win_wall.normal.p2 * CURTAIN_LEN
        table_width = nearst_df['bedside_width']
        bed_width = nearst_df['bed_width']
        table_num = nearst_df['bedside_num']
        if nearst_df.is_ob_chair_lst:  # 如果在nearst_df中is_ob_chair_lst为True则在次卧只能给放置斜单椅
            # 放置斜单椅
            dis_wall_obchair = BED_LEN - OB_CHAIR_DIS_BED_END - OBLIQUE_CHAIR_WIDTH_LEN[1]
            p1 = p0 + self.bed_wall.normal.p2 * dis_wall_obchair
            p2 = p1 + self.main_win_wall.normal.p2 * OBLIQUE_CHAIR_WIDTH_LEN[0]
            p1, p2 = DY_segment.get_p1_p2_from_normal(self.bed_wall.normal, p1, p2)
            bl = DY_segment(p1, p2)
            ob_ch = ObliqueChair(bl)
            self.ele_list.append(ob_ch)
            # 放置床
            dis_wall_bed = OBLIQUE_CHAIR_WIDTH_LEN[0] + OB_CHAIR_DIS_BED_SIDE
            p1 = p0 + self.main_win_wall.normal.p2 * dis_wall_bed
            p2 = p1 + self.main_win_wall.normal.p2 * bed_width
            bl_bed_p1, bl_bed_p2 = DY_segment. \
                get_p1_p2_from_normal(self.bed_wall.normal, p1, p2)
            backline = DY_segment(bl_bed_p1, bl_bed_p2)
            b = Bed()
            b.set_pos(backline, b.len)
            self.ele_list.append(b)
            # 放置床头柜0
            bl_tab_p1 = b.backline.p1
            bl_tab_p2 = b.backline.p1 - b.backline.dir.p2 * table_width
            bl_tab_p1, bl_tab_p2 = DY_segment. \
                get_p1_p2_from_normal(self.bed_wall.normal, bl_tab_p1, bl_tab_p2)

            backline = DY_segment(bl_tab_p1, bl_tab_p2)
            n_tab0 = CommonElement.NightTable()
            n_tab0.ID = 0
            n_tab0.set_pos(backline, n_tab0.len)
            self.ele_list.append(n_tab0)
            # 放置床头柜1
            bl_tab_p1 = b.backline.p2
            bl_tab_p2 = b.backline.p2 + b.backline.dir.p2 * table_width
            bl_tab_p1, bl_tab_p2 = DY_segment. \
                get_p1_p2_from_normal(self.bed_wall.normal, bl_tab_p1, bl_tab_p2)
            backline = DY_segment(bl_tab_p1, bl_tab_p2)
            n_tab1 = CommonElement.NightTable()
            n_tab1.set_pos(backline, n_tab1.len)
            self.ele_list.append(n_tab1)
        else:
            # 放置床
            if table_num == 2:
                dis_wall_bed = table_width
            else:  # table_num == 1
                dis_wall_bed = 0
            p1 = p0 + self.main_win_wall.normal.p2 * dis_wall_bed
            p2 = p1 + self.main_win_wall.normal.p2 * bed_width
            bl_bed_p1, bl_bed_p2 = DY_segment. \
                get_p1_p2_from_normal(self.bed_wall.normal, p1, p2)
            backline = DY_segment(bl_bed_p1, bl_bed_p2)
            b = Bed()
            b.set_pos(backline, b.len)
            self.ele_list.append(b)  # 此时在ele_list中,有着门,窗帘,床   ele_list中存着的是放入次卧的元素
            # 放置床头柜1
            bl_tab_p1 = p0 + self.main_win_wall.normal.p2 \
                             * (bed_width + (table_num - 1) * table_width)
            bl_tab_p2 = bl_tab_p1 + self.main_win_wall.normal.p2 * table_width
            bl_tab_p1, bl_tab_p2 = DY_segment. \
                get_p1_p2_from_normal(self.bed_wall.normal, bl_tab_p1, bl_tab_p2)
            backline = DY_segment(bl_tab_p1, bl_tab_p2)
            n_tab0 = CommonElement.NightTable()
            n_tab0.ID = 0
            n_tab0.set_pos(backline, n_tab0.len)
            self.ele_list.append(n_tab0)
            if table_num == 2:
                bl_tab_p1 = p0
                bl_tab_p2 = bl_tab_p1 + self.main_win_wall.normal.p2 * table_width
                bl_tab_p1, bl_tab_p2 = DY_segment. \
                    get_p1_p2_from_normal(self.bed_wall.normal, bl_tab_p1, bl_tab_p2)
                backline = DY_segment(bl_tab_p1, bl_tab_p2)
                n_tab1 = CommonElement.NightTable()
                n_tab1.ID = 0
                n_tab1.set_pos(backline, n_tab0.len)
                self.ele_list.append(n_tab1)
        # 放置衣柜
        win_op_wall = sorted(opposite_walls, key=lambda x: x.seg.length, reverse=True)[0]
        closet_bl_p1 = self.bed_wall.seg.intersection(win_op_wall.seg)
        p_tmp = closet_bl_p1[0] - self.main_win_wall.normal.p2 * CLOSET_LEN
        closet_flag = True
        drawer_flag = True
        for e in self.ele_list:
            # 如果e的backline包含了p_tmp的点,则衣柜为False
            if e.backline.seg.contains(p_tmp):
                closet_flag = False
        if closet_flag:
            line = Line(p_tmp, p_tmp + self.bed_wall.normal.p2)
            if len(door.boundary.polygon.intersection(line)) == 0:
                # 不相交，则衣柜所在墙宽是衣柜的最大长度
                dis = win_op_wall.seg.length
            else:
                # 相交，要找和门的最大距离
                l_list = []
                for s in door.boundary.seg_list:
                    if s.line.is_perpendicular(self.bed_wall.normal):
                        l_list.append(s)
                l1 = l_list[0].line.distance(p_tmp)
                l2 = l_list[1].line.distance(p_tmp)
                dis = min(l1, l2)
            # 距离不能小于衣柜的最小宽度
            if dis > CLOSET_WIDTH[0]:
                wid = 100000
                for i, l in enumerate(CLOSET_WIDTH[::-1]):
                    if float(dis) / float(l) >= 1.:
                        idx = i
                        break
                idx = len(CLOSET_WIDTH) - 1 - idx
                clo_p1 = closet_bl_p1[0]
                clo_p2 = clo_p1 + self.bed_wall.normal.p2 * CLOSET_WIDTH[idx]
                clo_p1, clo_p2 = DY_segment. \
                    get_p1_p2_from_normal(win_op_wall.normal, clo_p1, clo_p2)
                backline = DY_segment(clo_p1, clo_p2)
                clo = CommonElement.Closet(backline)
                self.ele_list.append(clo)

        else:
            # 放置衣柜代替屉柜
            drawer_flag = False
            len_list = []
            len_list.append(0)
            bed_op_wall = helpers.get_opposite_bounds(self.bed_wall, self.boundary)
            for wall in bed_op_wall:
                len_list.append(wall.seg.length)
            idx = len_list.index(max(len_list))
            bed_op_wall = bed_op_wall[idx - 1]
            # closet_bl_p1 = self.main_win_wall.seg.intersection(bed_op_wall.seg)[0] \
            #                + bed_op_wall.dir.p2 * CURTAIN_LEN
            # 判断衣柜长度扩展处是否有即将要布局的element,有则需要取消布置一项
            # p_tmp = closet_bl_p1 - self.main_win_wall.normal.p2 * CLOSET_LEN
            for e in self.ele_list:
                # if e.backline.seg.contains(p_tmp):
                #     closet_flag = False#？应该挪动躺椅的位置！
                if isinstance(e, CommonElement.Door):
                    door = e
            # 需要判断门和窗的相对关系来定位衣柜的摆放位置
            win_door_dis = self.main_win_wall.line.distance(
                door.backline.seg.midpoint)  # door.backline.seg.midpoint求出的是门底部中点的位置
            win_op_door_dis = win_op_wall.line.distance(door.backline.seg.midpoint)
            # 主窗法线与门的backline法线平行时衣柜的位置
            if self.main_win_wall.normal.is_parallel(door.backline.normal):  # normal法线
                # 衣柜的摆放位置
                if win_door_dis > win_op_door_dis:
                    closet_bl_p1 = self.main_win_wall.seg.intersection(bed_op_wall.seg)[0] \
                                   + self.main_win_wall.normal.p2 * CURTAIN_LEN
                else:
                    closet_bl_p1 = win_op_wall.seg.intersection(bed_op_wall.seg)[0]
            # 主窗法线与门的backline法线垂直时衣柜的位置
            if self.main_win_wall.normal.is_perpendicular(door.backline.normal):
                if win_door_dis > win_op_door_dis:
                    closet_bl_p1 = self.main_win_wall.seg.intersection(bed_op_wall.seg)[0] \
                                   + self.main_win_wall.normal.p2 * CURTAIN_LEN
                else:
                    closet_bl_p1 = win_op_wall.seg.intersection(bed_op_wall.seg)[0]
            p_tmp = closet_bl_p1 - self.bed_wall.normal.p2 * CLOSET_LEN
            # Undo for adj
            # for e in self.ele_list:
            # if e.backline.seg.contains(p_tmp):
            #     closet_flag = False#？应该挪动躺椅的位置！
            # 判断衣柜和门的延长线是否相交
            line = Line(p_tmp, p_tmp + self.main_win_wall.normal.p2)
            if len(door.boundary.polygon.intersection(line)) == 0:
                # 此时衣柜的宽度为所在墙的最大宽度
                dis = bed_op_wall.seg.length
            else:
                # 得到与门的最近距离
                double_line = []
                for s in door.boundary.seg_list:
                    if s.line.is_perpendicular(self.main_win_wall.normal):
                        double_line.append(s)
                d1 = double_line[0].line.distance(p_tmp)
                d2 = double_line[1].line.distance(p_tmp)
                # dis必须大于衣柜尺寸组合里的最小尺寸
                # if self.main_win_wall.line.distance(door.backline.seg.midpoint) == 0:
                if len(door.boundary.polygon.intersection(self.main_win_wall.line)) != 0:
                    dis = min(d1, d2)
                    # print(dis)
                else:
                    dis = min(d1, d2) - CURTAIN_LEN
            if dis > CLOSET_WIDTH[0]:
                for i, l in enumerate(CLOSET_WIDTH[::-1]):  # enumerate枚举
                    if float(dis) / float(l) >= 1.:
                        idx = i
                        if l == bed_op_wall.seg.length:
                            idx += 1
                        break

                idx = len(CLOSET_WIDTH) - 1 - idx
                clo_p1 = closet_bl_p1
                if self.main_win_wall.normal.is_perpendicular(door.backline.normal):
                    if win_door_dis < win_op_door_dis:
                        clo_p2 = clo_p1 - self.main_win_wall.normal.p2 * CLOSET_WIDTH[idx]
                    else:
                        clo_p2 = clo_p1 + self.main_win_wall.normal.p2 * CLOSET_WIDTH[idx]
                else:
                    if win_door_dis < win_op_door_dis:
                        clo_p2 = clo_p1 - self.main_win_wall.normal.p2 * CLOSET_WIDTH[idx]
                    else:
                        clo_p2 = clo_p1 + self.main_win_wall.normal.p2 * CLOSET_WIDTH[idx]
                clo_p1, clo_p2 = DY_segment.get_p1_p2_from_normal(bed_op_wall.normal, clo_p1, clo_p2)
                clo_bl = DY_segment(clo_p1, clo_p2)
                clo = CommonElement.Closet(clo_bl)
                if b.boundary.polygon.intersection(clo.boundary.polygon) != []:
                    pass
                else:
                    self.ele_list.append(clo)
            else:
                drawer_flag = True

        # 放置屉柜
        if drawer_flag:
            bed_end_p = []
            for p in b.boundary.polygon.vertices:
                if p not in b.backline.line.args:
                    bed_end_p.append(p)
            mid_bed_end = Segment(bed_end_p[0], bed_end_p[1]).midpoint
            mid_ray = DY_segment(mid_bed_end, mid_bed_end + b.dir.p2 * 1)
            mb_uti.arrange_drawers(mid_ray, self.ele_list, self.boundary, bed_instance=Bed)
        return True

    def __init(self):
        sum_length_lst = []
        bedside_num_lst = []
        bedside_wid_lst = []
        bed_wid_lst = []
        is_ob_chair_lst = []
        for bed_w in BED_WIDTH:
            if bed_w < BED_DOUBLE_THRESHOLD:
                bedside_num_max = 1  # 1： 1个床头柜 2：两个
                is_ob_chair_max = 1  # 1: 无斜单椅 2： 有斜单椅
            else:
                bedside_num_max = 2
                is_ob_chair_max = 2
            for bside_n in range(1, bedside_num_max + 1):
                for bside_w in BEDSIDE_NIGHTTABLE_WIDTH:
                    for ob_cha in range(0, is_ob_chair_max):
                        ob_len = 0 if ob_cha == 0 \
                            else OBLIQUE_CHAIR_WIDTH_LEN[0] - OB_CHAIR_DIS_BED_SIDE
                        sum_len = CLOSET_LEN + bed_w + bside_n * bside_w + ob_len
                        sum_length_lst.append(sum_len)
                        bedside_wid_lst.append(bside_w)
                        bedside_num_lst.append(bside_n)
                        bed_wid_lst.append(bed_w)
                        is_ob_chair_lst.append(False if ob_cha == 0 else True)
        pd_dict = {
            "sum_len": sum_length_lst,
            "bedside_num": bedside_num_lst,
            "bedside_width": bedside_wid_lst,
            "bed_width": bed_wid_lst,
            "is_ob_chair_lst": is_ob_chair_lst
        }
        self.df = pd.DataFrame(pd_dict)
        self.df = self.df.sort_values(by='sum_len')
