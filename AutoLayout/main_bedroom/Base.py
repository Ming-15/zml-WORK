# -*- coding:utf-8 -*-
import cmath
import random
import xlrd

import AutoLayout.hard_deco.Element
import AutoLayout.hard_deco.settings
from AutoLayout.BaseModual import *
from AutoLayout.CommonElement import Curtain, Door, NightTable, Recliner, Closet, Drawers
from AutoLayout.DY_Line import Window
import AutoLayout.helpers as helpers
from AutoLayout.main_bedroom.Element import *
from AutoLayout.main_bedroom.settings import *
from AutoLayout.main_bedroom.utility import *
from AutoLayout.settings import *


class MainBedroom(AutoLayout.BaseModual.Region):
    name = "主卧"
    def __init__(self):
        super(MainBedroom, self).__init__()
        self.main_curtain = None
        self.main_win_wall = None
        self.sub_curtain = None
        self.sub_win_wall = None
        self.bed_wall = None

        self.win_list = []
        ''' ---attr for virtual ---- ML --- '''
        self.door_list = []
        self.vir_door_list = []
        self.entrance = None
        self.vir_win_list = []
        self.vir_win = None
        self.avoid_dr_win = [[], []]

    def run(self):

        arrangement_dict = {
            (4, 1, 1): self.run411,
            (4, 1, 2): self.run412,
            (6, 1, 1): self.run611,
            (6, 1, 2): self.run612
        }

        key = (len(self.boundary.polygon.vertices), self.doors, self.windows)

        if not arrangement_dict.get(key, False) or self.borders != 0:
            # raise Exception("warning:主卧暂时不支持这种户型")
            self.run_anytype()
            return True
        if arrangement_dict.get(key) == self.run411:
            xmin, ymin, xmax, ymax = self.boundary.polygon.bounds
            xlen = xmax - xmin
            ylen = ymax - ymin
            if xlen > MAINBED_MAX_LEN or xlen < MAINBED_MIN_LEN or \
                            ylen > MAINBED_MAX_LEN or ylen < MAINBED_MIN_LEN:
                # raise Exception("warning:主卧功能区长宽不足")
                self.run_anytype()
                return True
            if abs(self.boundary.polygon.area) < MAINBED_MIN_LEN * MAINBED_MIN_LEN:
                # raise Exception("warning:主卧功能区面积不足")
                self.run_anytype()
                return True
            pass
        res = arrangement_dict.get(key)()
        self.hard_deco()

    def check_model(self, dataset):
        b_list = []
        for i in self.boundary.seg_list:
            b_list.append(i)
        if b_list[0].seg.length > b_list[-1].seg.length:
            l_wall = b_list[0]
            s_wall = b_list[-1]

        if b_list[0].seg.length > b_list[-2].seg.length:
            l_wall = b_list[0]
            s_wall = b_list[-2]

        ExcelFile = xlrd.open_workbook(dataset)
        # ['主卧', '客厅', '客房', '榻榻米', '餐厅', '厨房', '卫生间', '儿童房', '主材', '阳台', '过道', '分类数据']
        name = ExcelFile.sheet_names()[0]
        sheet = ExcelFile.sheet_by_name(name)
        # 获取整行或者整列的值
        cols_name = sheet.col_values(2)  # 第三列内容
        p1 = b_list[0].seg.intersection(b_list[-1].seg)[0]
        for i in range(1, len(cols_name)):
            raw = sheet.row_values(i)  # 第i行内容
            if raw[4] == settings.DEFAULT_VARIABLE_VALUE:
                raw[4] = 100

            p2 = p1 + s_wall.normal.p2 * int(raw[4])
            bl_bed_p1, bl_bed_p2 = DY_segment. \
                get_p1_p2_from_normal(l_wall.normal, p1, p2)
            backline = DY_segment(bl_bed_p1, bl_bed_p2)
            id = raw[0] + settings.DEFAULT_CONNECT_STR + raw[1]
            b = Element()
            b.ID = id
            b.len = int(raw[5])
            b.set_pos(backline, b.len)
            self.ele_list.append(b)
            p1 = p2
        return True

    def init_vir_point(self, vir_dr_mid_p):
        vir_ver_list = []
        for p in self.virtual_boundary.polygon.vertices:
            long = helpers.point_distance(p, vir_dr_mid_p)
            vir_ver_list.append([p, long])
        vir_ver_list.sort(key=lambda x: x[1], reverse=False)
        # 不在需要门的位置了，用顶点距离来表征门等的相对位置。
        # 最近点就是门附近，布局从远点开始就行，也可以不用care镜像
        # 降序排列，最近的一个定为A点。
        a, c = vir_ver_list[0][0], vir_ver_list[3][0]
        b, d = vir_ver_list[1][0], vir_ver_list[2][0]
        t = vir_ver_list[1][0]
        if c.x > a.x:
            if c.y > a.y:
                if t.x == a.x:
                    b = t
                    d = vir_ver_list[2][0]
                else:
                    d = t
                    b = vir_ver_list[2][0]
            else:
                if t.x > a.x:
                    b = t
                    d = vir_ver_list[2][0]
                else:
                    d = t
                    b = vir_ver_list[2][0]
        else:
            if c.y > a.y:
                if t.x < a.x:
                    b = t
                    d = vir_ver_list[2][0]
                else:
                    d = t
                    b = vir_ver_list[2][0]
            else:
                if t.x == a.x:
                    b = t
                    d = vir_ver_list[2][0]
                else:
                    d = t
                    b = vir_ver_list[2][0]
        return a, b, c, d, vir_ver_list

    def init_seg_boundary(self, a, b, c, d):
        ab = DY_segment(a, b)
        bc = DY_segment(b, c)
        cd = DY_segment(c, d)
        da = DY_segment(d, a)
        return ab, bc, cd, da

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
            self.entrance = entrance_list[0]
        vir_door = helpers.get_vir_door(self.entrance, self.boundary)
        vir_door_line = helpers.get_mother_boundary(vir_door, self.boundary)
        '''返回虚映射门'''
        return vir_door, vir_door_line, bal_tag, bal_dr

    def run_anytype(self):
        def set_bed(sp, rl, vir_win, be_len, bes_len, began_dis):
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
            besp1 = p2
            besp2 = besp1 + vir_win.normal.p2 * bes_len
            bes1, bes2 = DY_segment.get_p1_p2_from_normal(rl.normal, besp1, besp2)
            backline = DY_segment(bes1, bes2)
            bes = NightTable()
            bes.ID = 0
            bes.set_pos(backline, bes.len)
            self.ele_list.append(bes)

        def set_cloth(p, bl_dir, bl_normal, ele_len, ele):
            # ele表明1为衣柜
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

        def set_dra(p, bl_dir, bl_normal, dra_len):  # 记得传入的bl_normal 必然是反向的。
            ps1 = p
            ps2 = p + bl_dir.normal.p2 * dra_len
            p1, p2 = DY_segment.get_p1_p2_from_normal(helpers.get_op_normal(bl_normal.normal), ps1, ps2)
            backline = DY_segment(p1, p2)
            dra = Drawers(backline)
            self.ele_list.append(dra)

        def set_clo(p, bl_dir, bl_normal, clo_le):  # 记得传入的bl_normal 必然是反向的。
            ps1 = p
            ps2 = p + bl_dir.normal.p2 * clo_le
            op_normal = helpers.get_op_normal(bl_normal.normal)
            p1, p2 = DY_segment.get_p1_p2_from_normal(helpers.get_op_normal(bl_normal.normal), ps1, ps2)
            v_backline = DY_segment(p1, p2)
            clo = Closet(v_backline)
            self.ele_list.append(clo)

        def vector_replaced(rl, vir_win):  # 布局边，阳台边，
            def rl_fit(taken_len, tag):
                r_rl_len = rl_len - taken_len
                if tag:
                    remain_len = r_rl_len - min(BEDSIDE_NIGHTTABLE_WIDTH)
                    be_len = helpers.best_fit(MAINBED_BED_WIDTH, remain_len)
                    bes_len = helpers.best_fit(BEDSIDE_NIGHTTABLE_WIDTH, (r_rl_len - be_len))
                else:
                    # l两个床头柜

                    remain_len = r_rl_len - 2 * min(BEDSIDE_NIGHTTABLE_WIDTH)
                    be_len = helpers.best_fit(MAINBED_BED_WIDTH, remain_len)
                    bes_len = helpers.best_fit(BEDSIDE_NIGHTTABLE_WIDTH, (r_rl_len - be_len) / 2)
                return be_len, bes_len

            tangyi_tag = yigui_qiang_tag = 0  # 躺椅和衣柜
            if rl.seg.length > MAINBED_RECLINERS_THRE_DIS and \
                                    rl.seg.length * vir_win.seg.length > MAINBED_RECLINERS_THRE_AREA:
                tangyi_tag = 1
            # 初始化
            sp = rl.seg.intersection(vir_win.seg)[0]
            ep = helpers.another_p(rl, sp)
            np = helpers.another_p(vir_win, sp)
            t_move_dis = 0  # 躺椅造成的移动距离，效果和win_mov_dis一样
            if tangyi_tag:
                t_move_dis = RECLINERS_WIDTH_LEN[0] + MAINBED_RECLINERS_DIS_BED
                p1 = sp + vir_win.normal.p2 * (win_move_dis)
                p1 = p1 + rl.normal.p2 * (MAINBED_BED_LEN + MAINBED_RECLINERS_FAR_DIS)  # 躺椅需要移动到窗未来的为边上
                p2 = p1 + vir_win.normal.p2 * RECLINERS_WIDTH_LEN[0]
                pt1, pt2 = DY_segment.get_p1_p2_from_normal(helpers.get_op_normal(rl.normal), p1, p2)
                v_backline = DY_segment(pt1, pt2)
                rec = Recliner(v_backline)
                self.ele_list.append(rec)
                r_cd_len = rl.seg.length - win_move_dis - RECLINERS_WIDTH_LEN[0] - R_FRONT

            rl_len = rl.seg.length
            # 开始看看衣柜的放置，优先放置大的衣柜
            # 优先计算两个放置边的剩余长度
            if dr.line.is_parallel(rl.line):
                dis_rl_dr = rl.line.distance(dr_mid_p) - (DOOR_LENGTH - DOOR_WALL_LEN)
                dis_win_dr = vir_win.line.distance(dr_mid_p) - dr.seg.length / 2
            else:
                dis_rl_dr = rl.line.distance(dr_mid_p) - dr.seg.length / 2
                dis_win_dr = vir_win.line.distance(dr_mid_p) - (DOOR_LENGTH - DOOR_WALL_LEN)
                # 虚拟门映射情况下，同边需要避开吧的距离，# 正常门就是正常门数据

            cloth_taken_len = 0  # rl边考虑衣柜占据
            cloth_rec_avoid = 0  # 窗这条边却要考虑躺椅的影响
            judge_t_move_dis = win_move_dis + t_move_dis + (1 - tangyi_tag) * min(BEDSIDE_NIGHTTABLE_WIDTH)
            # 这个变量用于rl边可用长度的变化
            if dis_rl_dr > min(DRAWER_WIDTH) and rl_len > DRAWER_LEN + C_FRONT + RANGE_LEN[1] + judge_t_move_dis:
                # 窗对边满足最小放置
                # 先使用最大组件
                if dis_rl_dr > min(CLOSET_WIDTH) and \
                                rl_len > CLOSET_LEN + C_FRONT + RANGE_LEN[0] + judge_t_move_dis:
                    ele = 1
                    cloth_taken_len = CLOSET_LEN + C_FRONT
                    ele_len = helpers.best_fit(CLOSET_WIDTH, dis_rl_dr)

                else:
                    ele = 0
                    cloth_taken_len = DRAWER_LEN + C_FRONT
                    ele_len = helpers.best_fit(DRAWER_WIDTH, dis_rl_dr)

                p = ep
                set_cloth(p, rl, vir_win, ele_len, ele)


            elif vir_win.seg.length > (MAINBED_BED_LEN + MAINBED_BED_END_THRE_DIS + CLOSET_LEN) \
                    and dis_win_dr > min(DRAWER_WIDTH):
                if tangyi_tag:
                    if vir_win.seg.length < (MAINBED_BED_LEN + MAINBED_RECLINERS_FAR_DIS + CLOSET_LEN):
                        cloth_rec_avoid = RECLINERS_WIDTH_LEN[0]
                        np = np + vir_win.normal.p2 * cloth_rec_avoid
                        # 窗户这边进行布局是要将布局点提前定位的

                if dis_win_dr > min(CLOSET_WIDTH) + cloth_rec_avoid:
                    ele = 1
                    ele_len = helpers.best_fit(CLOSET_WIDTH, dis_win_dr - cloth_rec_avoid)


                else:
                    ele = 0
                    ele_len = helpers.best_fit(DRAWER_WIDTH, dis_rl_dr - cloth_rec_avoid)

                p = np + vir_win.normal.p2 * win_move_dis
                set_cloth(p, vir_win, rl, ele_len, ele)

            '''
            衣柜的占据距离可能是0 或者衣柜长和C_FRONT区域
            躺椅的纵向锤子距离cloth rec avoid 只是在放衣柜时可能有用而已，
            在床这儿只需要用到 t_move_dis，有躺椅配适函数传入一表示一个床头柜配适
            '''
            be_len, bes_len = rl_fit(cloth_taken_len + t_move_dis + win_move_dis, tangyi_tag)
            judge_t_move_dis = win_move_dis + t_move_dis + (1 - tangyi_tag) * bes_len
            set_bed(sp, rl, vir_win, be_len, bes_len, judge_t_move_dis)

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
                        print('不合理')  # 但还是要继续进行
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
                print('留个标记')

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
            print('窗户在门墙这边，注意')
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
        """六个顶点，一门一窗, 首先判断门是否在过道内"""

        # 找到六边形内部的点
        xmin, ymin, xmax, ymax = self.boundary.polygon.bounds
        for p in self.boundary.polygon.vertices:
            if p.x != xmin and p.x != xmax and p.y != ymin and p.y != ymax:
                inner_point = p
        # 找到过道区域, 先找内部点划分后比较短的线段
        pp = inner_point
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
            passage_pt = p0  # 过道边界的交点
            xlen = inner_point.distance(p1)
            ylen = ymax - ymin
        else:
            passage_pt = p1
            xlen = xmax - xmin
            ylen = inner_point.distance(p0)

        # 在找到划分面积比较小的区域
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
            small_rec = Polygon(p1, p2, p3, p4)
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
        # 判断过道区域内是否有门
        for d in self.ele_list:
            if isinstance(d, Door):
                door = d
                break
        found_door = False

        for seg in small_rec.sides:
            if seg.contains(door.backline.seg):
                found_door = True
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
        if xlen > MAINBED_MAX_LEN or xlen < MAINBED_MIN_LEN or \
                        ylen > MAINBED_MAX_LEN or ylen < MAINBED_MIN_LEN:
            raise Exception("warning:主卧功能区长宽不足")
        if abs(self.boundary.polygon.area) < MAINBED_MIN_LEN * MAINBED_MIN_LEN:
            raise Exception("warning:主卧功能区面积不足")
        self.run411()
        return True

    def run612(self):
        """六个顶点，一门一窗, 首先判断门是否在过道内"""

        # 找到六边形内部的点
        xmin, ymin, xmax, ymax = self.boundary.polygon.bounds
        for p in self.boundary.polygon.vertices:
            if p.x != xmin and p.x != xmax and p.y != ymin and p.y != ymax:
                inner_point = p
        # 找到过道区域, 先找内部点划分后比较短的线段
        pp = inner_point
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
            passage_pt = p0  # 过道边界的交点
            xlen = inner_point.distance(p1)
            ylen = ymax - ymin
        else:
            passage_pt = p1
            xlen = xmax - xmin
            ylen = inner_point.distance(p0)
        # 在找到划分面积比较小的区域
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
            small_rec = Polygon(p1, p2, p3, p4)
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
        # 判断过道区域内是否有门
        for d in self.ele_list:
            if isinstance(d, Door):
                door = d
                break
        found_door = False
        for seg in small_rec.sides:
            if seg.contains(door.backline.seg):
                found_door = True
        if found_door == False:
            raise Exception("暂时不支持门不在过道内的六边形户型")

        # 通过翻转、旋转归一化户型，使得过道在左下角
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
        # 此时和412情况相同
        if xlen > MAINBED_MAX_LEN or xlen < MAINBED_MIN_LEN or \
                        ylen > MAINBED_MAX_LEN or ylen < MAINBED_MIN_LEN:
            raise Exception("warning:主卧功能区长宽不足")
        if abs(self.boundary.polygon.area) < MAINBED_MIN_LEN * MAINBED_MIN_LEN:
            raise Exception("warning:主卧功能区面积不足")
        self.run412()
        return True

    def run411(self):
        # 1. 放置窗帘
        self.win_list, self.main_curtain, self.main_win_wall = \
            arrange_main_curtain(self.line_list, self.ele_list)

        # 得到bed_wall
        dis = 0
        for d in self.ele_list:
            if isinstance(d, Door):
                door = d
                break
        door_center = door.boundary.polygon.centroid
        adj_win_list = helpers.get_adjacent_bounds(self.main_win_wall, self.boundary)
        for s in adj_win_list:
            dis0 = s.line.distance(door_center)
            if dis0 > dis:
                dis = dis0
                self.bed_wall = s

        # 2. 判断是否放置躺椅
        opposite_walls = helpers.get_opposite_bounds(self.main_win_wall, self.boundary)
        opposite_walls = sorted(opposite_walls, key=lambda l: l.seg.length, reverse=True)
        dis = opposite_walls[0].line.distance(self.main_win_wall.p1)  # 最长墙的距离
        bed_width, table_width, recliner_width = self.get_combine_bed_sizes(dis)

        # 窗帘在床墙上的点，同时不再床墙端点，就是床头柜的一个端点
        vlist = helpers.get_ele_vertices_on_seg(self.main_curtain, self.bed_wall)
        for v in vlist:
            if v != self.bed_wall.p1 and v != self.bed_wall.p2:
                p0 = v
                break
        # main_win_wall 与 bed_wall的交点
        p0 = self.bed_wall.seg.intersection(self.main_win_wall.seg)[0]

        # 3. 放置床相关：床、床头柜、躺椅
        if recliner_width == 0:  # 没躺椅
            # 放置床
            dis_wall_bed = table_width + CURTAIN_LEN
            p1 = p0 + self.main_win_wall.normal.p2 * dis_wall_bed
            p2 = p1 + self.main_win_wall.normal.p2 * bed_width
            bl_bed_p1, bl_bed_p2 = DY_segment. \
                get_p1_p2_from_normal(self.bed_wall.normal, p1, p2)
            backline = DY_segment(bl_bed_p1, bl_bed_p2)
            b = Bed()
            b.set_pos(backline, b.len)
            self.ele_list.append(b)
            # 放置床头柜1
            bl_tab_p1 = b.backline.p1
            bl_tab_p2 = b.backline.p1 - b.backline.dir.p2 * table_width
            bl_tab_p1, bl_tab_p2 = DY_segment. \
                get_p1_p2_from_normal(self.bed_wall.normal, bl_tab_p1, bl_tab_p2)
            backline = DY_segment(bl_tab_p1, bl_tab_p2)
            n_tab0 = NightTable()
            n_tab0.ID = 0
            n_tab0.set_pos(backline, n_tab0.len)
            self.ele_list.append(n_tab0)
            # 放置床头柜2
            bl_tab_p1 = b.backline.p2
            bl_tab_p2 = b.backline.p2 + b.backline.dir.p2 * table_width
            bl_tab_p1, bl_tab_p2 = DY_segment. \
                get_p1_p2_from_normal(self.bed_wall.normal, bl_tab_p1, bl_tab_p2)
            backline = DY_segment(bl_tab_p1, bl_tab_p2)
            n_tab1 = NightTable()
            n_tab1.set_pos(backline, n_tab1.len)
            self.ele_list.append(n_tab1)

        else:  # 有躺椅
            # 躺椅离墙的距离
            dis_wall_recliner = MAINBED_COMBINED_BED_RECLINERS_LEN - RECLINERS_WIDTH_LEN[1]
            p0 = p0 + self.main_win_wall.normal.p2 * CURTAIN_LEN
            backline_rec_p1 = p0 + self.bed_wall.normal.p2 * dis_wall_recliner
            backline_rec_p2 = backline_rec_p1 + self.main_win_wall.normal.p2 * RECLINERS_WIDTH_LEN[0]
            backline_rec_p1, backline_rec_p2 = DY_segment. \
                get_p1_p2_from_normal(self.bed_wall.normal, backline_rec_p1, backline_rec_p2)
            backline = DY_segment(backline_rec_p1, backline_rec_p2)
            rec = Recliner(backline)
            self.ele_list.append(rec)
            # 判断躺椅和门是否相交
            if helpers.is_boundary_intersection(rec, door):
                # 找到离床墙最近的门边界
                l = self.bed_wall.line
                drs = [s for s in door.boundary.seg_list if l.is_parallel(s.line)]
                drs = sorted(drs, key=lambda d: l.distance(d.p1))[0]
                rec_back_dis = RECLINERS_WIDTH_LEN[1] - drs.line.distance(rec.backline.p1)
                backline_rec_p1 = backline_rec_p1 - self.bed_wall.normal.p2 * rec_back_dis
                backline_rec_p2 = backline_rec_p2 - self.bed_wall.normal.p2 * rec_back_dis
                backline = DY_segment(backline_rec_p1, backline_rec_p2)
                rec = Recliner(backline)
                self.ele_list.pop()
                self.ele_list.append(rec)
            # 放置床
            dis_wall_bed = MAINBED_RECLINERS_DIS_BED + RECLINERS_WIDTH_LEN[0]
            bl_bed_p1 = p0 + self.main_win_wall.normal.p2 * dis_wall_bed
            bl_bed_p2 = bl_bed_p1 + self.main_win_wall.normal.p2 * bed_width
            bl_bed_p1, bl_bed_p2 = DY_segment. \
                get_p1_p2_from_normal(self.bed_wall.normal, bl_bed_p1, bl_bed_p2)
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
            n_tab0 = NightTable()
            n_tab0.ID = 0
            n_tab0.set_pos(backline, n_tab0.len)
            self.ele_list.append(n_tab0)
            # 放置床头柜1
            bl_tab_p1 = b.backline.p2
            bl_tab_p2 = b.backline.p2 + b.backline.dir.p2 * table_width
            bl_tab_p1, bl_tab_p2 = DY_segment. \
                get_p1_p2_from_normal(self.bed_wall.normal, bl_tab_p1, bl_tab_p2)
            backline = DY_segment(bl_tab_p1, bl_tab_p2)
            n_tab1 = NightTable()
            n_tab1.set_pos(backline, n_tab1.len)
            self.ele_list.append(n_tab1)

        # 4. 放置衣柜
        win_op_wall = sorted(opposite_walls, key=lambda x: x.seg.length, reverse=True)[0]
        # bed_op_wall = get_opposite_bounds(self.bed_wall, self.boundary)[0]
        closet_bl_p1 = self.bed_wall.seg.intersection(win_op_wall.seg)

        # 衣柜与床头柜最近的距离点
        p_tmp = closet_bl_p1[0] - self.main_win_wall.normal.p2 * CLOSET_LEN
        # 这个点如果在床头柜backline上，说明距离不够放置衣柜
        closet_flag = True
        drawer_flag = True
        for e in self.ele_list:
            if e.backline.seg.contains(p_tmp):
                closet_flag = False

        if closet_flag:
            for e in self.ele_list:
                if isinstance(e, Door):
                    door = e
                    break
            # 判断衣柜的延长线是否与门相交
            line = Line(p_tmp, p_tmp + self.bed_wall.normal.p2)
            if len(door.boundary.polygon.intersection(line)) == 0:
                # 不相交，则衣柜所在墙宽是衣柜的最大长度
                dis = win_op_wall.seg.length
            else:
                # 相交，要找和门的最小距离
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
                clo = Closet(backline)

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
                if isinstance(e, Door):
                    door = e
                    # 需要判断门和窗的相对关系来定位衣柜的摆放位置
            win_door_dis = self.main_win_wall.line.distance(door.backline.seg.midpoint)
            win_op_door_dis = win_op_wall.line.distance(door.backline.seg.midpoint)
            if self.main_win_wall.normal.is_parallel(door.backline.normal):
                if win_door_dis > win_op_door_dis:
                    closet_bl_p1 = self.main_win_wall.seg.intersection(bed_op_wall.seg)[0] \
                                   + self.main_win_wall.normal.p2 * CURTAIN_LEN
                else:
                    closet_bl_p1 = win_op_wall.seg.intersection(bed_op_wall.seg)[0]
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
                else:
                    dis = min(d1, d2) - CURTAIN_LEN

            if dis > CLOSET_WIDTH[0]:
                for i, l in enumerate(CLOSET_WIDTH[::-1]):
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
                clo = Closet(clo_bl)
                self.ele_list.append(clo)
            else:
                drawer_flag = True

        # 5. 放置屉柜
        if drawer_flag:
            bed_end_p = []
            for p in b.boundary.polygon.vertices:
                if p not in b.backline.line.args:
                    bed_end_p.append(p)
            mid_bed_end = Segment(bed_end_p[0], bed_end_p[1]).midpoint
            mid_ray = DY_segment(mid_bed_end, mid_bed_end + b.dir.p2 * 1)
            arrange_drawers(mid_ray, self.ele_list, self.boundary)

            # 6. 放置写字桌
            arrange_writing_desk(self.ele_list, self.boundary, self.main_win_wall, self.bed_wall)

        return True

    def run412(self):
        # 1. 放置窗帘
        self.win_list, self.main_curtain, self.main_win_wall = \
            arrange_main_curtain(self.line_list, self.ele_list)

        self.sub_curtain, self.sub_win_wall = \
            arrange_sub_curtain(self.line_list, self.ele_list)

        # 得到bed_wall
        dis = 0
        for d in self.ele_list:
            if isinstance(d, Door):
                door = d
                break
        door_center = door.boundary.polygon.centroid
        adj_win_list = helpers.get_adjacent_bounds(self.main_win_wall, self.boundary)
        for s in adj_win_list:
            dis0 = s.line.distance(door_center)
            if dis0 > dis:
                dis = dis0
                self.bed_wall = s

        # 2. 判断是否放置躺椅
        opposite_walls = helpers.get_opposite_bounds(self.main_win_wall, self.boundary)
        opposite_walls = sorted(opposite_walls, key=lambda l: l.seg.length, reverse=True)
        dis = opposite_walls[0].line.distance(self.main_win_wall.p1)  # 最长墙的距离
        bed_width, table_width, recliner_width = self.get_combine_bed_sizes(dis)

        bed_flag = self.bed_wall.seg.contains(self.sub_win_wall.seg)
        while bed_flag:
            p0 = self.sub_curtain.point_list[0]
            sub_win_len = DY_segment(self.sub_curtain.point_list[0], self.sub_curtain.point_list[1]).seg.length
            sub_win_min_len = table_width + CURTAIN_LEN
            if self.sub_curtain.point_list[1] != self.main_win_wall.p1:
                if self.sub_curtain.point_list[1].x == self.main_win_wall.p1.x or \
                                self.sub_curtain.point_list[1].y == self.main_win_wall.p1.y:
                    sub_win_to_main_win_seg = DY_segment(self.sub_curtain.point_list[1], self.main_win_wall.p1).seg
                else:
                    sub_win_to_main_win_seg = DY_segment(self.sub_curtain.point_list[1], self.main_win_wall.p2).seg
                sub_win_to_main_win = sub_win_to_main_win_seg.length
            else:
                sub_win_to_main_win = 0
            if sub_win_len > sub_win_min_len and \
                            sub_win_to_main_win <= 100:
                # 3. 放置床相关：床、床头柜、躺椅
                if recliner_width == 0:  # 没躺椅
                    # 放置床
                    p1 = p0 + self.main_win_wall.normal.p2 * 1
                    p2 = p1 + self.main_win_wall.normal.p2 * bed_width
                    bl_bed_p1, bl_bed_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, p1, p2)
                    backline = DY_segment(bl_bed_p1, bl_bed_p2)
                    b = Bed()
                    b.set_pos(backline, b.len)
                    self.ele_list.append(b)
                    # 放置床头柜1
                    bl_tab_p1 = b.backline.p1
                    bl_tab_p2 = b.backline.p1 - b.backline.dir.p2 * table_width
                    bl_tab_p1, bl_tab_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, bl_tab_p1, bl_tab_p2)
                    backline = DY_segment(bl_tab_p1, bl_tab_p2)
                    n_tab0 = NightTable()
                    n_tab0.ID = 0
                    n_tab0.set_pos(backline, n_tab0.len)
                    self.ele_list.append(n_tab0)
                    # 放置床头柜2
                    bl_tab_p1 = b.backline.p2
                    bl_tab_p2 = b.backline.p2 + b.backline.dir.p2 * table_width
                    bl_tab_p1, bl_tab_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, bl_tab_p1, bl_tab_p2)
                    backline = DY_segment(bl_tab_p1, bl_tab_p2)
                    n_tab1 = NightTable()
                    n_tab1.set_pos(backline, n_tab1.len)
                    self.ele_list.append(n_tab1)

                else:  # 有躺椅
                    # 躺椅离墙的距离
                    dis_wall_recliner = MAINBED_COMBINED_BED_RECLINERS_LEN - RECLINERS_WIDTH_LEN[1]
                    p_0 = self.bed_wall.seg.intersection(self.main_win_wall.seg)[0]
                    p_0 = p_0 + self.main_win_wall.normal.p2 * CURTAIN_LEN
                    backline_rec_p1 = p_0 + self.bed_wall.normal.p2 * dis_wall_recliner
                    backline_rec_p2 = backline_rec_p1 + self.main_win_wall.normal.p2 * RECLINERS_WIDTH_LEN[0]
                    backline_rec_p1, backline_rec_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, backline_rec_p1, backline_rec_p2)
                    backline = DY_segment(backline_rec_p1, backline_rec_p2)
                    rec = Recliner(backline)
                    self.ele_list.append(rec)
                    # 放置床
                    dis_wall_bed = MAINBED_RECLINERS_DIS_BED + RECLINERS_WIDTH_LEN[0]
                    bl_bed_p1 = p_0 + self.main_win_wall.normal.p2 * dis_wall_bed
                    bl_bed_p2 = bl_bed_p1 + self.main_win_wall.normal.p2 * bed_width
                    bl_bed_p1, bl_bed_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, bl_bed_p1, bl_bed_p2)
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
                    n_tab0 = NightTable()
                    n_tab0.ID = 0
                    n_tab0.set_pos(backline, n_tab0.len)
                    self.ele_list.append(n_tab0)
                    # 放置床头柜1
                    bl_tab_p1 = b.backline.p2
                    bl_tab_p2 = b.backline.p2 + b.backline.dir.p2 * table_width
                    bl_tab_p1, bl_tab_p2 = DY_segment. \
                        get_p1_p2_from_normal(self.bed_wall.normal, bl_tab_p1, bl_tab_p2)
                    backline = DY_segment(bl_tab_p1, bl_tab_p2)
                    n_tab1 = NightTable()
                    n_tab1.set_pos(backline, n_tab1.len)
                    self.ele_list.append(n_tab1)

                break

            else:
                bed_flag = False

        else:
            # 窗帘在床墙上的点，同时不再床墙端点，就是床头柜的一个端点
            vlist = helpers.get_ele_vertices_on_seg(self.main_curtain, self.bed_wall)
            for v in vlist:
                if v != self.bed_wall.p1 and v != self.bed_wall.p2:
                    p0 = v
                    break
            # main_win_wall 与 bed_wall的交点
            p0 = self.bed_wall.seg.intersection(self.main_win_wall.seg)[0]

            # 3. 放置床相关：床、床头柜、躺椅
            if recliner_width == 0:  # 没躺椅
                # 放置床
                dis_wall_bed = table_width + CURTAIN_LEN
                p1 = p0 + self.main_win_wall.normal.p2 * dis_wall_bed
                p2 = p1 + self.main_win_wall.normal.p2 * bed_width
                bl_bed_p1, bl_bed_p2 = DY_segment. \
                    get_p1_p2_from_normal(self.bed_wall.normal, p1, p2)
                backline = DY_segment(bl_bed_p1, bl_bed_p2)
                b = Bed()
                b.set_pos(backline, b.len)
                self.ele_list.append(b)
                # 放置床头柜1
                bl_tab_p1 = b.backline.p1
                bl_tab_p2 = b.backline.p1 - b.backline.dir.p2 * table_width
                bl_tab_p1, bl_tab_p2 = DY_segment. \
                    get_p1_p2_from_normal(self.bed_wall.normal, bl_tab_p1, bl_tab_p2)
                backline = DY_segment(bl_tab_p1, bl_tab_p2)
                n_tab0 = NightTable()
                n_tab0.ID = 0
                n_tab0.set_pos(backline, n_tab0.len)
                self.ele_list.append(n_tab0)
                # 放置床头柜2
                bl_tab_p1 = b.backline.p2
                bl_tab_p2 = b.backline.p2 + b.backline.dir.p2 * table_width
                bl_tab_p1, bl_tab_p2 = DY_segment. \
                    get_p1_p2_from_normal(self.bed_wall.normal, bl_tab_p1, bl_tab_p2)
                backline = DY_segment(bl_tab_p1, bl_tab_p2)
                n_tab1 = NightTable()
                n_tab1.set_pos(backline, n_tab1.len)
                self.ele_list.append(n_tab1)

            else:  # 有躺椅
                # 躺椅离墙的距离
                dis_wall_recliner = MAINBED_COMBINED_BED_RECLINERS_LEN - RECLINERS_WIDTH_LEN[1]
                p0 = p0 + self.main_win_wall.normal.p2 * CURTAIN_LEN
                backline_rec_p1 = p0 + self.bed_wall.normal.p2 * dis_wall_recliner
                backline_rec_p2 = backline_rec_p1 + self.main_win_wall.normal.p2 * RECLINERS_WIDTH_LEN[0]
                backline_rec_p1, backline_rec_p2 = DY_segment. \
                    get_p1_p2_from_normal(self.bed_wall.normal, backline_rec_p1, backline_rec_p2)
                backline = DY_segment(backline_rec_p1, backline_rec_p2)
                rec = Recliner(backline)
                self.ele_list.append(rec)
                # 放置床
                dis_wall_bed = MAINBED_RECLINERS_DIS_BED + RECLINERS_WIDTH_LEN[0]
                bl_bed_p1 = p0 + self.main_win_wall.normal.p2 * dis_wall_bed
                bl_bed_p2 = bl_bed_p1 + self.main_win_wall.normal.p2 * bed_width
                bl_bed_p1, bl_bed_p2 = DY_segment. \
                    get_p1_p2_from_normal(self.bed_wall.normal, bl_bed_p1, bl_bed_p2)
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
                n_tab0 = NightTable()
                n_tab0.ID = 0
                n_tab0.set_pos(backline, n_tab0.len)
                self.ele_list.append(n_tab0)
                # 放置床头柜1
                bl_tab_p1 = b.backline.p2
                bl_tab_p2 = b.backline.p2 + b.backline.dir.p2 * table_width
                bl_tab_p1, bl_tab_p2 = DY_segment. \
                    get_p1_p2_from_normal(self.bed_wall.normal, bl_tab_p1, bl_tab_p2)
                backline = DY_segment(bl_tab_p1, bl_tab_p2)
                n_tab1 = NightTable()
                n_tab1.set_pos(backline, n_tab1.len)
                self.ele_list.append(n_tab1)

        # 4. 放置衣柜
        opposite_walls = helpers.get_opposite_bounds(self.main_win_wall, self.boundary)
        win_op_wall = opposite_walls[0]
        if win_op_wall.seg.contains(self.sub_win_wall.seg):
            pass
        else:
            win_op_wall = opposite_walls[0]
            bed_op_wall = helpers.get_opposite_bounds(self.bed_wall, self.boundary)[0]

            closet_bl_p1 = self.bed_wall.seg.intersection(win_op_wall.seg)

            # 衣柜与床头柜最近的距离点
            p_tmp = closet_bl_p1[0] - self.main_win_wall.normal.p2 * CLOSET_LEN

            # 这个点如果在床头柜backline上，说明距离不够放置衣柜
            closet_flag = True
            for e in self.ele_list:
                if e.backline.seg.contains(p_tmp):
                    closet_flag = False

            if closet_flag:
                for e in self.ele_list:
                    if isinstance(e, Door):
                        door = e
                        break
                # 判断衣柜的延长线是否与门相交
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
                    clo = Closet(backline)

                    self.ele_list.append(clo)

        # 5. 放置屉柜
        bed_end_p = []
        for p in b.boundary.polygon.vertices:
            if p not in b.backline.line.args:
                bed_end_p.append(p)
        mid_bed_end = Segment(bed_end_p[0], bed_end_p[1]).midpoint
        mid_ray = DY_segment(mid_bed_end, mid_bed_end + b.dir.p2 * 1)
        arrange_drawers(mid_ray, self.ele_list, self.boundary)

        # 6. 放置写字桌
        arrange_writing_desk(self.ele_list, self.boundary, self.main_win_wall, self.bed_wall)

        return True

    # def arrange_main_curtain(self):
    #     # 对所有窗排序
    #     self.win_list.clear()
    #     win_list = []
    #     for l in self.line_list:
    #         if isinstance(l, DY_Line.Window):
    #             win_list.append(l)
    #
    #     self.win_list = sorted(win_list, key=lambda w: w.seg.length, reverse=True)
    #
    #     cur = Curtain()
    #     backline = self.win_list[0].wall
    #     cur.set_pos(backline, cur.len)
    #     self.ele_list.append(cur)
    #     self.main_win_wall = backline
    #     self.main_curtain = cur
    #     # self.get_bed_wall()

    # def get_bed_wall(self):
    #     dis = 0
    #     # 找到与客厅相通的门
    #     for d in self.ele_list:
    #         if isinstance(d, Door):
    #             out_door_name = get_out_door_name(self.name, d)
    #             if out_door_name == LivingRoom.name:
    #                 door = d
    #                 break
    #     door_center = door.boundary.centroid
    #
    #     # 找出与主窗相连的两个边界
    #     adj_win_list = get_adjacent_bounds(self.main_win_wall, self.boundary)
    #
    #     for s in adj_win_list:
    #         dis0 = s.distance(door_center)
    #         if dis0 > dis:
    #             dis = dis0
    #             self.bed_wall = s

    def get_curtain_on_bed_wall(self):
        curtain_on_bed_wall = []
        for e in self.ele_list:
            if not isinstance(e, AutoLayout.DY_Line.Window):
                continue
            if self.bed_wall.contains(e.backline.p1) and self.bed_wall.contains(e.backline.p2):
                curtain_on_bed_wall.append(e)
        return curtain_on_bed_wall

    def get_combine_bed_sizes(self, dis):
        """ return (bed_width, table_width, recliner_width)
        undo: 没有躺椅时，有一种选择方案尺度重合
        """
        if dis >= MAINBED_RECLINERS_THRE_DIS \
                and abs(self.boundary.polygon.area) >= MAINBED_RECLINERS_THRE_AREA:
            recliner_width = RECLINERS_WIDTH_LEN[0]
            diff = MAINBED_RECLINERS_THRE_DIS - MAINBED_COMBINED_BED_RECLINERS_WIDTH[0]
            combine_list = [x + diff for x in MAINBED_COMBINED_BED_RECLINERS_WIDTH]

            for i, l in enumerate(combine_list[::-1]):
                if float(dis) / float(l) >= 1.:
                    idx = i
                    break
            idx = len(combine_list) - 1 - idx
            table_width = MAINBED_COMBINED_BED_RECLINERS_TABLESIZE[idx]
            bed_width = MAINBED_COMBINED_BED_RECLINERS_BEDSIZE[idx]

        else:
            recliner_width = 0
            diff = MAINBED_MIN_LEN - MAINBED_COMBINED_BED_NO_RECLINERS_WIDTH[0]
            combine_list = [x + diff for x in MAINBED_COMBINED_BED_NO_RECLINERS_WIDTH]

            for i, l in enumerate(combine_list[::-1]):
                if float(dis) / float(l) >= 1.:
                    idx = i
                    break
            idx = len(combine_list) - 1 - idx
            table_width = MAINBED_COMBINED_BED_NO_RECLINERS_TABLESIZE[idx]
            bed_width = MAINBED_COMBINED_BED_NO_RECLINERS_BEDSIZE[idx]
        return (bed_width, table_width, recliner_width)

    def check_floor_plan(self):
        for e in self.ele_list:
            if isinstance(e, Door):
                for l in self.line_list:
                    if len(e.backline.seg.intersection(l.seg)) > 0:
                        raise Exception("warning:户型错误，主卧门、窗、虚拟边界连接或重合")

    def hard_deco(self):
        # floor's id, skirting_line's id, plaster_line's id
        self.floor_id = AutoLayout.hard_deco.settings.FLOOR_ID
        self.skirting_line_id = AutoLayout.hard_deco.settings.SKIRTING_LINE_ID
        self.plaster_line_id = AutoLayout.hard_deco.settings.PLASTER_LINE_ID

        # wall_paper
        wall_paper = AutoLayout.hard_deco.Element.Wallpaper(self.bed_wall.p1, self.bed_wall.p2)
        wall_paper.ID = AutoLayout.hard_deco.settings.WALLPAPER_ID
        self.line_list.append(wall_paper)

        # find the position of ceiling_lamp where it is between bed's back_front_line(1/3 near the front)
        bed = [e for e in self.ele_list if isinstance(e, Bed)][0]
        mid = Point2D(int(bed.frontline.seg.midpoint.x), int(bed.frontline.seg.midpoint.y)) \
              - bed.backline.normal.p2 * int((1 / 3) * bed.len * (1 / 2))
        half_len = int(AutoLayout.hard_deco.settings.CEILING_LAMP_W_L_H['test_cl'][1] / 2)
        half_wid = int(AutoLayout.hard_deco.settings.CEILING_LAMP_W_L_H['test_cl'][0] / 2)
        p1 = mid - bed.backline.normal.p2 * half_len + bed.backline.dir.p2 * half_wid
        p2 = mid - bed.backline.normal.p2 * half_len - bed.backline.dir.p2 * half_wid
        p1, p2 = DY_segment. \
            get_p1_p2_from_normal(bed.backline.normal, p1, p2)
        ceil_bl = DY_segment(p1, p2)
        ceil_lamp = AutoLayout.hard_deco.Element.Ceiling_lamp(ceil_bl)
        self.ele_list.append(ceil_lamp)
