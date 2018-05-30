from sympy import pi
from sympy.geometry import *
import matplotlib.pylab as plt
from matplotlib.lines import Line2D

import AutoLayout.settings as settings

def point_to_string(p):
    return str(p).split('D')[1]

class DY_segment(object):
    """DY_segment的nromal类似于法线，总是指向矢量右手边"""

    def __init__(self, p1, p2):
        # undo: 判断是否是横平竖直
        self.p1, self.p2 = p1, p2
        if p1.x == p2.x:
            self.horizontal = False
            self.vertical = True
        elif p1.y == p2.y:
            self.horizontal = True
            self.vertical = False
        # else:
        #     raise "error:线不是横平竖直的"

        self.__init()

    def __init(self):
        p1, p2 = self.p1, self.p2
        self.line = Line(p1, p2)
        self.seg = Segment(p1, p2)
        self.ray = Ray(p1, p2)
        r = Ray(p1, p2)
        p = Point(r.p2 - r.p1)
        len = self.seg.length
        self.normal = Ray((0, 0), (p.y / len, -p.x / len))
        self.dir = Ray((0, 0), (p.x / len, p.y / len))

    def cross_dir(self, seg):
        a = ((self.p2.x - self.p1.x), (self.p2.y - self.p1.y))
        b = ((seg.p2.x - seg.p1.x), (seg.p2.y - seg.p1.y))
        direc = (a[0] * b[1] - b[0] * a[1])
        if direc != 0:
            return direc/abs(direc)
        else:
            return 0

    @staticmethod
    def get_p1_p2_from_normal(normal, p1, p2):
        r = DY_segment(p1, p2)
        if r.normal.angle_between(normal) == 0:
            return p1, p2
        elif r.normal.angle_between(normal) == pi:
            return p2, p1
        else:
            assert True, "法线设置有误"

    def fliplr(self):
        """左右翻转(x,y)->(-x,y)"""
        self.p1 = Point(-self.p1.x, self.p1.y)
        self.p2 = Point(-self.p2.x, self.p2.y)
        self.__init()

    def flipup(self):
        """上下翻转(x,y)->(x,-y)"""
        self.p1 = Point(self.p1.x, -self.p1.y)
        self.p2 = Point(self.p2.x, -self.p2.y)
        self.__init()

    def rotate90_anticlockwise(self):
        """绕原点逆时针旋转90度(x,y)->(-y, x)"""
        self.p1 = Point(-self.p1.y, self.p1.x)
        self.p2 = Point(-self.p2.y, self.p2.x)
        self.__init()

    def rotate90_clockwise(self):
        """绕原点顺时针旋转90度(x,y)->(y, -x)"""
        self.p1 = Point(self.p1.y, -self.p1.x)
        self.p2 = Point(self.p2.y, -self.p2.x)
        self.__init()

    def to_string(self):
        res = point_to_string(self.p1) + ';' + point_to_string(self.p2)
        return res

    def draw(self, ax, ls='-', col='#000000'):
        xdata = (self.p1.x, self.p2.x)
        ydata = (self.p1.y, self.p2.y)
        ax.add_line(Line2D(xdata, ydata, linestyle=ls, color=col))


class DY_boundary(object):
    name = 'boundary'
    """DY boundary 的是由顺时针连接的DY segment组成"""

    def __init__(self, *args, **kwargs):
        # undo: 判断点是否顺时针
        # pt_list = self.update_boundary(*args)
        polygon_tmp = Polygon(*args, **kwargs)
        self.polygon = Polygon(*polygon_tmp.vertices)
        self.seg_list = []
        self.__set_seg_list()
        # v = self.polygon.vertices
        # for i in range(-len(v), 0):
        #     self.seg_list.append(DY_segment(v[i], v[i+1]))

    def update_boundary(*args):
        pt_list = list(args)
        pt_list.pop(0) # list 0 为DY_Boundary名
        for i in range(len(pt_list)):
            if i+1 == len(pt_list):
                j = 0
            else:
                j = i + 1
            delta_x = abs(pt_list[i][0] - pt_list[j][0])
            delta_y = abs(pt_list[i][1] - pt_list[j][1])
            if delta_x == 0 or delta_y == 0:
                continue
            if delta_x < delta_y and delta_x < settings.MAX_BOUNARY_SEG_CHANGE:
                # 水平
                x = (pt_list[i][0] + pt_list[j][0]) // 2
                pt_list[i] = Point2D(x, pt_list[i][1])
                pt_list[j] = Point2D(x, pt_list[j][1])
            elif delta_y < settings.MAX_BOUNARY_SEG_CHANGE:
                y = (pt_list[i][1] + pt_list[j][1]) // 2
                pt_list[i] = Point2D(pt_list[i][0], y)
                pt_list[j] = Point2D(pt_list[j][0], y)

        normed_pt_list = pt_list
        return normed_pt_list

    def to_string(self):
        res = ''
        for i in self.seg_list:
            res += point_to_string(i.p1) + ';'
        return res[:-1]

    def draw(self, ax, ls='-', col='#000000'):
        for s in self.seg_list:
            s.draw(ax, ls, col)

    def draw_single(self):
        figure, ax = plt.subplots()
        self.draw(ax)
        plt.plot()
        plt.show()

    def __set_seg_list(self):
        self.seg_list.clear()
        v = self.polygon.vertices
        for i in range(-len(v), 0):
            self.seg_list.append(DY_segment(v[i], v[i + 1]))

    def fliplr(self):
        """左右翻转(x,y)->(-x,y)"""
        vlist = []
        for v in self.polygon.vertices:
            vlist.append(Point(-v.x, v.y))
        v1 = [v for v in reversed(vlist)]
        eval_str = 'Polygon('
        for p in v1:
            if p != v1[-1]:
                eval_str += str(p) + ','
            else:
                eval_str += str(p)
        eval_str += ')'
        self.polygon = eval(eval_str)
        self.__set_seg_list()

    def flipup(self):
        """上下翻转(x,y)->(x,-y)"""
        vlist = []
        for v in self.polygon.vertices:
            vlist.append(Point(v.x, -v.y))
        v1 = [v for v in reversed(vlist)]
        eval_str = 'Polygon('
        for p in v1:
            if p != v1[-1]:
                eval_str += str(p) + ','
            else:
                eval_str += str(p)
        eval_str += ')'
        self.polygon = eval(eval_str)
        self.__set_seg_list()

    def rotate90_anticlockwise(self):
        """绕原点逆时针旋转90度(x,y)->(-y, x)"""
        vlist = []
        for v in self.polygon.vertices:
            vlist.append(Point(-v.y, v.x))
        v1 = [v for v in vlist]
        eval_str = 'Polygon('
        for p in v1:
            if p != v1[-1]:
                eval_str += str(p) + ','
            else:
                eval_str += str(p)
        eval_str += ')'
        self.polygon = eval(eval_str)
        self.__set_seg_list()

    def rotate90_clockwise(self):
        """绕原点顺时针旋转90度(x,y)->(y, -x)"""
        vlist = []
        for v in self.polygon.vertices:
            vlist.append(Point(v.y, -v.x))
        v1 = [v for v in vlist]
        eval_str = 'Polygon('
        for p in v1:
            if p != v1[-1]:
                eval_str += str(p) + ','
            else:
                eval_str += str(p)
        eval_str += ')'
        self.polygon = eval(eval_str)
        self.__set_seg_list()


class House(object):
    name = '东易'

    def __init__(self):
        self.floors = 0
        self.floor_list = []

    def add_floorplan(self, f):
        self.floor_list.append(f)
        self.floors += 1

    def draw(self, savename=None):
        if savename is not None:
            name1 = savename[:-4]
        for idx, f in enumerate(self.floor_list):
            figure, ax = plt.subplots()
            f.boundary.draw(ax)
            ele_list = []
            line_list = []
            bound_list = []
            for r in f.region_list:
                ele_list.extend(r.ele_list)
                line_list.extend(r.line_list)
                bound_list.append(r.boundary)
            for b in bound_list:
                b.draw(ax)
            for l in line_list:
                l.draw(ax)
            for e in ele_list:
                if e.is_multiple:
                    for ee in e.ele_list:
                        ee.draw(ax)
                e.draw(ax)
            ax.set_aspect(1)
            xlist = sorted(f.boundary.polygon.vertices, key=lambda v: v.x)
            ylist = sorted(f.boundary.polygon.vertices, key=lambda v: v.y)
            plt.xlim(int(xlist[0].x) - 500, int(xlist[-1].x) + 500)
            plt.ylim(int(ylist[0].y) - 500, int(ylist[-1].y) + 500)

            length = str(float((ylist[-1].y - ylist[0].y) / 1000)) + ' m'
            ypos = (int(ylist[0].y) + int(ylist[-1].y)) / 2
            ax.text(int(xlist[0].x) - 300, ypos, length, rotation='vertical')
            length = str(float((xlist[-1].x - xlist[0].x) / 1000)) + ' m'
            xpos = (int(xlist[0].x) + int(xlist[-1].x)) / 2
            ax.text(xpos, int(ylist[0].y) - 300, length)

            if savename is None:
                plt.show()
            if savename is not None:
                # savename1 = name1 + '_' + str(idx) + '.jpg'
                savename1 = name1 + '.png'
                plt.savefig(savename1)
            figure.clf()
            plt.clf()
            plt.close()
