# _*_ coding:utf-8 _*_
from AutoLayout.BaseModual import *
from AutoLayout.livingroom.settings import *
import random
import AutoLayout.main_bedroom.utility as mb_uti

class TVbench(Element):
    name = "电视柜"
    def __init__(self, backline):
        super(TVbench, self).__init__()
        self.set_pos(backline, LIVINGROOM_TV_BENCH_LEN)

class Sofa_Tea_area(Element):
    name = "沙发茶几边几组件"
    def __init__(self):
        super(Sofa_Tea_area, self).__init__()
        self.is_multiple = True
        self.is_true = False
        self.ele_list = []
    def run(self):
        arrangement_dict = {
            0:self._run0, # 一字沙发布局
            1:self._run1, # L沙发布局  zhuc: 暂时删掉
        }
        key = random.randint(0, 1)
        arrangement_dict.get(key)()
    def _run0(self):
        width_list = [x for x in SOFA1_WIDTH if x <= self.backline.seg.length]
        sofa_width = SOFA1_WIDTH[random.randint(0, len(width_list) - 1)]
        mid = Point2D(int(self.backline.seg.midpoint.x),int(self.backline.seg.midpoint.y))
        p1 = mid + self.backline.dir.p2 * int(sofa_width/2)
        p2 = p1 - self.backline.dir.p2 * sofa_width
        p1, p2 = DY_segment.get_p1_p2_from_normal(self.backline.normal, p1, p2)
        sofa_bl = DY_segment(p1, p2)
        sofa = Sofa_1(sofa_bl)
        self.ele_list.append(sofa)
        # 配置边几
        max_sidetable_wid = int((self.backline.seg.length - sofa_width) / 2)
        width = [x for x in SIDE_TABLE_WIDTH if x < max_sidetable_wid]
        if len(width):
            p1 = sofa_bl.p2
            p2 = p1 + sofa_bl.dir.p2 * width[-1]
            p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_bl.normal, p1, p2)
            side1_bl = DY_segment(p1, p2)
            sidetable0 = SideTable(side1_bl)
            self.ele_list.append(sidetable0)

            p1 = sofa_bl.p1
            p2 = p1 - sofa_bl.dir.p2 * width[-1]
            p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_bl.normal, p1, p2)
            side1_bl = DY_segment(p1, p2)
            sidetable1 = SideTable(side1_bl)
            self.ele_list.append(sidetable1)
        # 配置茶几
        tea_tab = self.get_tea_table()
        wid_list = [w for w in tea_tab.wid_len.keys() if w < sofa_bl.seg.length]
        # wid_list = sorted(wid_list)
        tea_wid = wid_list[random.randint(0, len(wid_list)-1)]
        tea_len = tea_tab.wid_len.get(tea_wid)

        tea_len_th = self.len - sofa.len - DIS_SOFA_TEA
        if tea_len > tea_len_th:

            tea_wid_list = [w for w in wid_list if tea_tab.wid_len.get(w) <= tea_len_th]
            if len(tea_wid):
                tea_wid = tea_wid_list[random.randint(0, len(tea_wid_list) - 1)]
                tea_len = tea_tab.wid_len.get(tea_wid)
            else:
                return

        # while tea_len > (self.len - sofa.len - DIS_SOFA_TEA):
        #     tea_wid = wid_list[random.randint(0, len(wid_list) - 1)]
        #     tea_len = tea_tab.wid_len.get(tea_wid)
        # tea_wid = wid_list[-1]

        p0 =  mid + self.backline.normal.p2 * (sofa.len + DIS_SOFA_TEA)
        p1 = p0 + self.backline.dir.p2 * int(tea_wid / 2)
        p2 = p1 - self.backline.dir.p2 * tea_wid
        p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_bl.normal, p1, p2)
        tea_bl = DY_segment(p1, p2)
        tea_tab.set_pos(tea_bl, tea_len)
        self.ele_list.append(tea_tab)

    def _run1(self):
        l13_list = [ (x + SOFAL_L3)/2 for x in SOFAL_L1_L2.keys()]
        width_list = [x for x in l13_list if x <= self.backline.seg.length/2]
        if len(width_list):
            sofa_width = width_list[random.randint(0, len(width_list) - 1)]
            sofa_width = int(sofa_width * 2 - SOFAL_L3)
            mid = Point2D(int(self.backline.seg.midpoint.x),int(self.backline.seg.midpoint.y))
            case = random.randint(0, 1) # 生成沙发转角的方向
            mid_l0 = int((sofa_width + SOFAL_L3) / 2) # 长方向
            mid_l1 = int((sofa_width - SOFAL_L3) / 2) # 短方向
            if case == 0: # 转角在 backline前段,p2
                p1 = mid + self.backline.dir.p2 * int(mid_l0)
                p2 = mid - self.backline.dir.p2 * int(mid_l1)
                p1, p2 = DY_segment.get_p1_p2_from_normal(self.backline.normal, p1, p2)
                bl = DY_segment(p1, p2)
                sofa = RightSofa_L(bl, SOFAL_L1_L2.get(bl.seg.length))
            elif case == 1:# 转角在 backline后段,p1
                p1 = mid + self.backline.dir.p2 * int(mid_l1)
                p2 = mid - self.backline.dir.p2 * int(mid_l0)
                p1, p2 = DY_segment.get_p1_p2_from_normal(self.backline.normal, p1, p2)
                bl = DY_segment(p1, p2)
                sofa = LeftSofa_L(bl, SOFAL_L1_L2.get(bl.seg.length))
            self.ele_list.append(sofa)
            # 配置边几
            max_sidetable_wid = int(self.backline.seg.length/2 - mid_l1/2)
            width = [x for x in SIDE_TABLE_WIDTH if x < max_sidetable_wid][-1]
            if case == 0:
                p1 = sofa.backline.p1
                p2 = p1 - sofa.backline.dir.p2 * width
            if case == 1:
                p1 = sofa.backline.p2
                p2 = p1 + sofa.backline.dir.p2 * width
            p1, p2 = DY_segment.get_p1_p2_from_normal(bl.normal, p1, p2)
            side1_bl = DY_segment(p1, p2)
            sidetable0 = SideTable(side1_bl)
            self.ele_list.append(sidetable0)
            # 配置茶几
            tea_tab = self.get_tea_table()
            max_tea_wid2 = int((sofa.backline.seg.length - SOFAL_L3) / 2 - DIS_SOFA_TEA)
            wid_list = [w for w in tea_tab.wid_len.keys() if w <= max_tea_wid2 * 2]
            wid_list = sorted(wid_list)
            tea_wid = wid_list[-1]
            tea_len = tea_tab.wid_len.get(tea_wid)

            tea_len_th = self.len - SOFAL_L3  - DIS_SOFA_TEA
            if tea_len > tea_len_th:

                tea_wid_list = [w for w in wid_list if tea_tab.wid_len.get(w) <= tea_len_th]
                if len(tea_wid):
                    tea_wid = tea_wid_list[random.randint(0, len(tea_wid_list) - 1)]
                    tea_len = tea_tab.wid_len.get(tea_wid)
                else:
                    return

            if case == 0:
                p1 = sofa.backline.p2
                p2 = p1 + sofa.backline.normal.p2 * sofa.len
                p3 = p2 - sofa.backline.dir.p2 * SOFAL_L3
                p4 = p3 + sofa.backline.normal.p2 * (-1) * (sofa.len - SOFAL_L3)
                p5 = p4 + sofa.backline.dir.p2 * (-1) * (sofa.backline.seg.length - SOFAL_L3)
                p6 = sofa.backline.p1

            else:
                p1 = sofa.backline.p1
                p2 = sofa.backline.p2
                p3 = p2 + sofa.backline.normal.p2 * SOFAL_L3
                p4 = p3 + sofa.backline.dir.p2 * (-1) * (sofa.backline.seg.length - SOFAL_L3)
                p5 = p4 + sofa.backline.normal.p2 * (sofa.len - SOFAL_L3)
                p6 = p5 + sofa.backline.dir.p2 * (-1) * SOFAL_L3
            sofa.boundary = DY_boundary(p1, p2, p3, p4, p5, p6)
            front_line = sorted([seg for seg in sofa.boundary.seg_list], key=lambda seg:seg.seg.length)
            for seg in front_line:
                if seg.line.is_parallel(sofa.backline.line) and not seg.seg.contains(sofa.backline.p1 and \
                    sofa.backline.p2):
                    front_line = seg
            sofa.front_mid = front_line.seg.midpoint
            p0 = sofa.front_mid + self.backline.normal.p2 * DIS_SOFA_TEA
            p1 = p0 + self.backline.dir.p2 * int(tea_wid / 2)
            p2 = p1 - self.backline.dir.p2 * tea_wid
            p1, p2 = DY_segment.get_p1_p2_from_normal(bl.normal, p1, p2)
            tea_bl = DY_segment(p1, p2)
            tea_tab.set_pos(tea_bl, tea_len)
            self.ele_list.append(tea_tab)
        else:
            width_list = [x for x in SOFA1_WIDTH if x <= self.backline.seg.length]
            sofa_width = SOFA1_WIDTH[random.randint(0, len(width_list) - 1)]
            mid = Point2D(int(self.backline.seg.midpoint.x),int(self.backline.seg.midpoint.y))
            p1 = mid + self.backline.dir.p2 * int(sofa_width / 2)
            p2 = p1 - self.backline.dir.p2 * sofa_width
            p1, p2 = DY_segment.get_p1_p2_from_normal(self.backline.normal, p1, p2)
            sofa_bl = DY_segment(p1, p2)
            sofa = Sofa_1(sofa_bl)
            self.ele_list.append(sofa)
            # 配置边几
            max_sidetable_wid = int((self.backline.seg.length - sofa_width) / 2)
            width = [x for x in SIDE_TABLE_WIDTH if x < max_sidetable_wid]
            if len(width):
                p1 = sofa_bl.p2
                p2 = p1 + sofa_bl.dir.p2 * width[-1]
                p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_bl.normal, p1, p2)
                side1_bl = DY_segment(p1, p2)
                sidetable0 = SideTable(side1_bl)
                self.ele_list.append(sidetable0)

                p1 = sofa_bl.p1
                p2 = p1 - sofa_bl.dir.p2 * width[-1]
                p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_bl.normal, p1, p2)
                side1_bl = DY_segment(p1, p2)
                sidetable1 = SideTable(side1_bl)
                self.ele_list.append(sidetable1)
            # 配置茶几
            tea_tab = self.get_tea_table()
            wid_list = [w for w in tea_tab.wid_len.keys() if w < sofa_bl.seg.length]
            # wid_list = sorted(wid_list)
            tea_wid = wid_list[random.randint(0, len(wid_list) - 1)]
            tea_len = tea_tab.wid_len.get(tea_wid)

            # tea_wid = wid_list[-1]
            tea_len_th = self.len - sofa.len - DIS_SOFA_TEA
            if tea_len > tea_len_th:

                tea_wid_list = [w for w in wid_list if tea_tab.wid_len.get(w) <= tea_len_th]
                if len(tea_wid):
                    tea_wid = tea_wid_list[random.randint(0, len(tea_wid_list) - 1)]
                    tea_len = tea_tab.wid_len.get(tea_wid)
                else:
                    return


            # while tea_len > (self.len - sofa.len - DIS_SOFA_TEA):
            #     tea_wid = wid_list[random.randint(0, len(wid_list) - 1)]
            #     tea_len = tea_tab.wid_len.get(tea_wid)

            p0 = mid + self.backline.normal.p2 * (sofa.len + DIS_SOFA_TEA)
            p1 = p0 + self.backline.dir.p2 * int(tea_wid / 2)
            p2 = p1 - self.backline.dir.p2 * tea_wid
            p1, p2 = DY_segment.get_p1_p2_from_normal(sofa_bl.normal, p1, p2)
            tea_bl = DY_segment(p1, p2)
            tea_tab.set_pos(tea_bl, tea_len)
            self.ele_list.append(tea_tab)

    def get_tea_table(self):
        case = random.randint(0,2)
        if case == 0: # 长方形茶几
            return RectangleTeaTable()
        elif case == 1: # 方形茶几
            return SquareTeaTable()
        elif case == 2: # 圆形茶几
            return CircleTeaTable()

class Sofa_1(Element):
    name = "一字沙发"
    def __init__(self, backline):
        super(Sofa_1, self).__init__()
        self.set_pos(backline, SOFA1_LEN)
        self.front_mid = Point2D(int(self.frontline.seg.midpoint.x),
                                 int(self.frontline.seg.midpoint.y))

class RightSofa_L(Element):
    name = "右转角沙发"
    def __init__(self, backline, length):
        super(RightSofa_L, self).__init__()
        self.set_pos(backline, length)

    def draw(self, ax):
        backlength = self.backline.seg.length
        xdata = (self.backline.p1.x,self.backline.p2.x)
        ydata = (self.backline.p1.y,self.backline.p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-',linewidth=3))
        p1 = self.backline.p2
        p2 = p1 + self.backline.normal.p2 * self.len
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle='-'))
        p1 = p2
        p2 = p1 - self.backline.dir.p2 * SOFAL_L3
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle='-'))
        p1 = p2
        p2 = p1 + self.backline.normal.p2 * (-1) *(self.len - SOFAL_L3)
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle='-'))
        p1 = p2
        p2 = p1 + self.backline.dir.p2 * (-1) * (backlength - SOFAL_L3)
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle='-'))
        p1 = p2
        p2 = self.backline.p1
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle='-'))

        p = sorted(self.boundary.polygon.vertices, key=lambda v: v.y)
        center = Segment(p[2], p[3]).midpoint
        ax.text(center.x, center.y - 100, self.name, color='#000000')
        front_line = sorted([ i for i in self.boundary.seg_list], key=lambda i:i.seg.length)
        self.front_mid = (front_line[-2]).seg.midpoint


class LeftSofa_L(Element):
    name = "左转角沙发"
    def __init__(self, backline, length):
        super(LeftSofa_L, self).__init__()
        self.set_pos(backline, length)

    def draw(self, ax):
        backlength = self.backline.seg.length
        xdata = (self.backline.p1.x,self.backline.p2.x)
        ydata = (self.backline.p1.y,self.backline.p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-',linewidth=3))
        p1 = self.backline.p1
        p2 = p1 + self.backline.normal.p2 * self.len
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle='-'))
        p1 = p2
        p2 = p1 + self.backline.dir.p2  * SOFAL_L3
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle='-'))
        p1 = p2
        p2 = p1 + self.backline.normal.p2 * (-1) * (self.len - SOFAL_L3)
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle='-'))
        p1 = p2
        p2 = p1 + self.backline.dir.p2 * (backlength - SOFAL_L3)
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle='-'))
        p1 = p2
        p2 = p1 + self.backline.normal.p2 * (-1) * (SOFAL_L3)
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle='-'))

        p = sorted(self.boundary.polygon.vertices, key=lambda v: v.y)
        center = Segment(p[2], p[3]).midpoint
        ax.text(center.x, center.y - 100, self.name, color='#000000')

class Sofa_L():
    name = "L型沙发"
    def __init__(self, backline, case):
        self.angle = None
        self.height = 0
        self.ID = -1
        self.backline = backline
        self._set_angle()
        self.case = case
        # case 哪个方向安放转角
        if case == 0: # 在backline顶端放置转角
            l2 = SOFAL_L1_L2.get(backline.seg.length)
            p1 = backline.p2
            p2 = p1 + backline.normal.p2 * l2
            p3 = p2 - backline.dir.p2 * SOFAL_L3
            p4 = p3 - backline.normal.p2 * (l2 - SOFAL_L4)
            p5 = backline.p1 + backline.normal.p2 * SOFAL_L4
            p6 = backline.p1
            self.boundary = DY_boundary(p1, p2, p3, p4, p5, p6)
            self.front_mid = Point2D(int(self.boundary.seg_list[3].seg.midpoint.x),
                                     int(self.boundary.seg_list[3].seg.midpoint.y))
            self.draw_point_list = [p1, p3, p5]

        elif case == 1: # 在backline底端放置
            l2 = SOFAL_L1_L2.get(backline.seg.length)
            p1 = backline.p2
            p2 = p1 + backline.normal.p2 * SOFAL_L4
            p3 = p2 - backline.dir.p2 * (backline.seg.length - SOFAL_L3)
            p4 = p3 + backline.normal.p2 * (l2 - SOFAL_L4)
            p5 = backline.p1 + backline.normal.p2 * l2
            p6 = backline.p1
            self.boundary = DY_boundary(p1, p2, p3, p4, p5, p6)
            self.front_mid = Point2D(int(self.boundary.seg_list[1].seg.midpoint.x),
                                     int(self.boundary.seg_list[1].seg.midpoint.y))
            self.draw_point_list = [p6, p4, p2]

    def draw(self, ax ):
        self.boundary.draw(ax, col='#000000')
        xdata = (self.draw_point_list[0].x, self.draw_point_list[1].x)
        ydata = (self.draw_point_list[0].y, self.draw_point_list[1].y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle='-'))
        xdata = (self.draw_point_list[0].x, self.draw_point_list[2].x)
        ydata = (self.draw_point_list[0].y, self.draw_point_list[2].y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle='-'))
        p = sorted(self.boundary.polygon.vertices, key=lambda v:v.y)
        center = Segment(p[2], p[3]).midpoint
        ax.text(center.x, center.y - 100, self.name)

    def _set_angle(self):
        if self.backline.normal.p2 == Point2D(0, 1):
            self.angle = 0
        elif self.backline.normal.p2 == Point2D(1, 0):
            self.angle = 90
        elif self.backline.normal.p2 == Point2D(0, -1):
            self.angle = 180
        elif self.backline.normal.p2 == Point2D(-1, 0):
            self.angle = 270
    def get_xyz_str(self):
        """y is height, default y = 0"""
        tmp0 = str(self.backline.p2).split('D')[1] # (***,***)
        tmp1 = tmp0.split(',')
        tmp1.insert(1, str(self.height))
        res = ','.join(tmp1)
        return res

class RectangleTeaTable(Element):
    name = "长方形茶几"
    def __init__(self):
        super(RectangleTeaTable, self).__init__()
        self.wid_len = REC_TEA_WIDTH_LEN

class SquareTeaTable(Element):
    name = "正方形茶几"
    def __init__(self):
        super(SquareTeaTable, self).__init__()
        self.wid_len = SQUARE_TEA_WIDTH_LEN

class CircleTeaTable(Element):
    name = "圆形茶几"
    def __init__(self):
        super(CircleTeaTable, self).__init__()
        self.wid_len = CIRCLE_TEA_WIDTH_LEN

class SideTable(Element):
    name = "边几"
    def __init__(self, backline):
        super(SideTable, self).__init__()
        self.set_pos(backline, SIDE_TABLE_LEN)

