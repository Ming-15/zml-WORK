import AutoLayout.DY_Line
from AutoLayout.BaseClass import *
import AutoLayout.helpers
import AutoLayout.settings

class Region(object):
    name = "区域"
    def __init__(self):
        self.boundary = None
        self.ID = 0
        self.uuid = '0'

        self.floor_id = -1
        self.skirting_line_id = -1
        self.plaster_line_id = -1
        self.doors = 0
        self.windows = 0
        self.borders = 0
        self.ele_list = []
        self.line_list = []
        self.flip_dict_num = {'fliplr':0, 'flipup':0, 'rot90':0, '-rot90':0}

        self.virtual_boundary = None
        self.virtual_borders = []


    def set_boundary(self, bound):
        self.boundary = bound

    def add_window(self, window):
        for s in self.boundary.seg_list:
            if s.seg.contains(window.p1) and s.seg.contains(window.p2):
                if window.normal.equals(s.normal):
                    win = window
                    win.wall = s
                    break
                else:
                    win = AutoLayout.DY_Line.Window(window.p2, window.p1)
                    win.set_boundary(window.boundary)
                    win.wall = s
                    break

        self.line_list.append(win)
        self.windows += 1

    def add_border(self, border):
        for s in self.boundary.seg_list:
            if s.seg.contains(border.p1) and s.seg.contains(border.p2):
                if border.normal.equals(s.normal):
                    bord = border
                    bord.wall = s
                    break
                else:
                    bord = AutoLayout.DY_Line.Border(border.p2, border.p1)
                    bord.connect_list = border.connect_list
                    bord.wall = s
                    break
        self.line_list.append(bord)
        self.borders += 1

    def add_door(self, door):
        self.ele_list.append(door)
        self.doors += 1

    def fliplr(self):
        """左右翻转(x,y)->(-x,y)"""
        self.boundary.fliplr()
        for e in self.ele_list:
            e.fliplr()
            if e.is_multiple:
                for ee in e.ele_list:
                    ee.fliplr()
        for l in self.line_list:
            l.fliplr()
            if hasattr(l, 'wall'):
                l.wall.fliplr()

    def flipup(self):
        """上下翻转(x,y)->(x,-y)"""
        self.boundary.flipup()
        for e in self.ele_list:
            e.flipup()
            if e.is_multiple:
                for ee in e.ele_list:
                    ee.flipup()
        for l in self.line_list:
            l.flipup()
            if hasattr(l, 'wall'):
                l.wall.fliplr()
    def rotate90_clockwise(self):
        """绕原点顺时针旋转90度(x,y)->(-y, x)"""
        self.boundary.rotate90_clockwise()
        for e in self.ele_list:
            e.rotate90_clockwise()
            if e.is_multiple:
                for ee in e.ele_list:
                    ee.rotate90_clockwise()
        for l in self.line_list:
            l.rotate90_clockwise()
            if hasattr(l, 'wall'):
                l.wall.rotate90_clockwise()
    def rotate90_anticlockwise(self):
        self.boundary.rotate90_anticlockwise()
        for e in self.ele_list:
            e.rotate90_anticlockwise()
            if e.is_multiple:
                for ee in e.ele_list:
                    ee.rotate90_anticlockwise()
        for l in self.line_list:
            l.rotate90_anticlockwise()
            if hasattr(l, 'wall'):
                l.wall.fliplr()

    def draw(self, savename=None, show_flag=True):
        figure, ax = plt.subplots()
        self.boundary.draw(ax)
        for l in self.line_list:
            l.draw(ax)
        for e in self.ele_list:
            if e.is_multiple:
                for ee in e.ele_list:
                    ee.draw(ax)
            e.draw(ax)

        ax.set_aspect(1)

        xlist = sorted(self.boundary.polygon.vertices, key=lambda v:v.x)
        ylist = sorted(self.boundary.polygon.vertices, key=lambda v:v.y)
        plt.xlim(int(xlist[0].x)-300, int(xlist[-1].x)+300)
        plt.ylim(int(ylist[0].y)-300, int(ylist[-1].y)+300)

        plt.plot()
        if show_flag:
            plt.show()

        if savename is not None:
            plt.savefig(savename)

        figure.clf()
        plt.clf()
        plt.close()
        return

class Element(object):
    name = "组件"
    """Element是所有家具的基类"""
    def __init__(self):
        self.angle = None # 对于旋转角度，朝北=0度，顺时针范围0-360度
        self.height = 0
        self.boundary = None
        self.dir = None
        self.len = 0
        self.backline = None # 面对家具时候，左后方点的世界坐标位置是backline.p1
        self.frontline = None
        self.point_list = []
        self.ID = -1
        self.is_multiple = False # undo:要有子xml结构 ?
        self.is_true = True # undo:只有TRUE组件才画图，同时写入xml

    def set_boundary(self, bound):
        self.point_list.clear()
        self.point_list = bound.polygon.vertices

        assert len(self.point_list) == 4, '家具组件只能有四个点'
        self.boundary = bound
    def set_backline(self, backline):
        assert self.boundary is not None, "Element必须先set_boundary()"
        new_backline = AutoLayout.helpers.get_new_backline_with_bound(backline, self.boundary)
        self.backline = new_backline
        self._set_angle()
        self.dir = self.backline.normal
        self.frontline = [seg for seg in self.boundary.seg_list
                          if seg.seg != backline.seg and seg.seg.is_parallel(backline.seg)][0]

    def set_pos(self, backline, len):
        self.len = len
        p1,p2 = backline.p1, backline.p2
        p3 = backline.p2 + backline.normal.p2 * len
        p4 = backline.p1 + backline.normal.p2 * len
        self.boundary = DY_boundary(p1, p2, p3, p4)
        self.backline = backline
        self._set_angle()
        self.point_list = self.boundary.polygon.vertices
        self.dir = self.backline.normal
        self.frontline = [seg for seg in self.boundary.seg_list
                          if seg.seg != backline.seg and seg.seg.is_parallel(backline.seg)][0]

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

    def fliplr(self):
        """左右翻转(x,y)->(-x,y)"""
        self.boundary.fliplr()
        self.backline.fliplr()
        self.dir = self.backline.normal
        self.point_list = self.boundary.polygon.vertices
    def flipup(self):
        """上下翻转(x,y)->(x,-y)"""
        self.boundary.flipup()
        self.backline.flipup()
        self.dir = self.backline.normal
        self.point_list = self.boundary.polygon.vertices
    def rotate90_clockwise(self):
        self.boundary.rotate90_clockwise()
        self.backline.rotate90_clockwise()
        self.dir = self.backline.normal
        self.point_list = self.boundary.polygon.vertices
    def rotate90_anticlockwise(self):
        self.boundary.rotate90_anticlockwise()
        self.backline.rotate90_anticlockwise()
        self.dir = self.backline.normal
        self.point_list = self.boundary.polygon.vertices

    def draw(self, ax): # FF3030  000000
        if self.is_multiple is True:
            return None
        self.boundary.draw(ax, col='#000000')
        linestyle = '--' if self.is_multiple else '-'

        l0 = Line(self.point_list[0], self.point_list[2])
        l1 = Line(self.point_list[1], self.point_list[3])
        xdata = (l0.p1.x, l0.p2.x)
        ydata = (l0.p1.y, l0.p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle=linestyle))
        xdata = (l1.p1.x, l1.p2.x)
        ydata = (l1.p1.y, l1.p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle=linestyle))
        p = sorted(self.boundary.polygon.vertices, key=lambda v:v.y)
        center = Segment(p[0], p[1]).midpoint
        ax.text(center.x, center.y, self.name)

class FloorPlan(Region):
    name = "户型图"
    def __init__(self):
        super(FloorPlan, self).__init__()
        self.regions = 0
        self.region_list = []
        self.height = AutoLayout.settings.DEFAULT_ROOM_HEIGHT

    def add_region(self, main_bedroom):
        self.region_list.append(main_bedroom)
        self.regions += 1
