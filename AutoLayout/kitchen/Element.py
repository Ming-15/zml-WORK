# -*- coding:utf-8 -*-
from AutoLayout.BaseModual import *
from AutoLayout.kitchen.settings import *

class Refrigerator(Element):
    name = "冰箱"
    def __init__(self, backline, length):
        super(Refrigerator, self).__init__()
        self.set_pos(backline, length)


class RangehoodCabinet(Element):
    name = "烟机柜"
    def __init__(self, backline, length):
        super(RangehoodCabinet, self).__init__()
        self.set_pos(backline, length)

class SinkCabinet(Element):
    name = "水槽柜"
    def __init__(self, backline, length):
        super(SinkCabinet, self).__init__()
        self.set_pos(backline, length)


class RightCornerCabinet(Element):
    name = "右转角地柜"
    def __init__(self, backline, length):
        super(RightCornerCabinet, self).__init__()
        self.set_pos(backline, length)

class LeftCornerCabinet(Element):
    name = "左转角地柜"
    def __init__(self, backline, length):
        super(LeftCornerCabinet, self).__init__()
        self.set_pos(backline, length)

class AdjustingPanel(Element):
    name = "调节板"
    def __init__(self, backline, length):
        super(AdjustingPanel, self).__init__()
        self.set_pos(backline, length)

# class KitchenBoard(Element):
#     name = "案板"
#     def __init__(self, backline, length):
#         super(KitchenBoard, self).__init__()
#         self.set_pos(backline, length)
#
# class CornerCabinet(Element):
#     name = "转角地柜"
#     def __init__(self, backline, length):
#         super(CornerCabinet, self).__init__()
#         self.set_pos(backline, length)

class SingleCabinet(Element):
    name = "单开门地柜"
    def __init__(self, backline, length):
        super(SingleCabinet, self).__init__()
        self.set_pos(backline, length)

class DoubleCabinet(Element):
    name = "双开门地柜"
    def __init__(self, backline, length):
        super(DoubleCabinet, self).__init__()
        self.set_pos(backline, length)

class DrawerCabinet(Element):
    name = "抽屉地柜"
    def __init__(self, backline, length):
        super(DrawerCabinet, self).__init__()
        self.set_pos(backline, length)

class PullBasket(Element):
    name = "拉篮"
    def __init__(self, backline, length):
        super(PullBasket, self).__init__()
        self.set_pos(backline, length)

class RanHangingCabinet(Element):
    name = "烟机吊柜"
    def __init__(self,backline,length):
        super(RanHangingCabinet, self).__init__()
        self.set_pos(backline,length)
        self.height = KITCHEN_HANGING_H

    def draw(self, ax):
        xdata = (self.backline.p1.x, self.backline.p2.x)
        ydata = (self.backline.p1.y, self.backline.p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle='-'))
        p1 = self.backline.p1
        p2 = p1 + self.backline.normal.p2 * HANGING_CABINET_L
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-'))
        p1 = p2
        p2 = p1 + self.backline.dir.p2 * self.backline.seg.length
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-'))
        p1 = p2
        p2 = p1 - self.backline.normal.p2 * HANGING_CABINET_L
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-'))
        p = sorted(self.boundary.polygon.vertices, key=lambda v:v.y)
        center = Segment(p[2], p[3]).midpoint
        ax.text(center.x, center.y - 100, self.name,color='#990033')
class SingleHangingCabinet(Element):
    name = "单开门吊柜"
    def __init__(self, backline, length):
        super(SingleHangingCabinet, self).__init__()
        self.set_pos(backline, length)
        self.height = KITCHEN_HANGING_H

    def draw(self, ax):
        xdata = (self.backline.p1.x, self.backline.p2.x)
        ydata = (self.backline.p1.y, self.backline.p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle='-'))
        p1 = self.backline.p1
        p2 = p1 + self.backline.normal.p2 * HANGING_CABINET_L
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-'))
        p1 = p2
        p2 = p1 + self.backline.dir.p2 * self.backline.seg.length
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-'))
        p1 = p2
        p2 = p1 - self.backline.normal.p2 * HANGING_CABINET_L
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-'))
        p = sorted(self.boundary.polygon.vertices, key=lambda v:v.y)
        center = Segment(p[2], p[3]).midpoint
        ax.text(center.x, center.y - 100, self.name,color='#990033')

class DoubleHangingCabinet(Element):
    name = "双开门吊柜"
    def __init__(self, backline, length):
        super(DoubleHangingCabinet, self).__init__()
        self.set_pos(backline, length)
        self.height = KITCHEN_HANGING_H

    def draw(self, ax):
        xdata = (self.backline.p1.x, self.backline.p2.x)
        ydata = (self.backline.p1.y, self.backline.p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle='-'))
        p1 = self.backline.p1
        p2 = p1 + self.backline.normal.p2 * HANGING_CABINET_L
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-'))
        p1 = p2
        p2 = p1 + self.backline.dir.p2 * self.backline.seg.length
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-'))
        p1 = p2
        p2 = p1 - self.backline.normal.p2 * HANGING_CABINET_L
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-'))
        p = sorted(self.boundary.polygon.vertices, key=lambda v:v.y)
        center = Segment(p[2], p[3]).midpoint
        ax.text(center.x, center.y - 100, self.name,color='#990033')
class HangingAdjustingPanel(Element):
    name = "吊柜调节板"
    def __init__(self, backline, length):
        super(HangingAdjustingPanel, self).__init__()
        self.set_pos(backline, length)
        self.height = KITCHEN_HANGING_H

    def draw(self, ax):
        xdata = (self.backline.p1.x, self.backline.p2.x)
        ydata = (self.backline.p1.y, self.backline.p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle='-'))
        p1 = self.backline.p1
        p2 = p1 + self.backline.normal.p2 * HANGING_CABINET_L
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-'))
        p1 = p2
        p2 = p1 + self.backline.dir.p2 * self.backline.seg.length
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-'))
        p1 = p2
        p2 = p1 - self.backline.normal.p2 * HANGING_CABINET_L
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-'))
        p = sorted(self.boundary.polygon.vertices, key=lambda v:v.y)
        center = Segment(p[2], p[3]).midpoint
        ax.text(center.x, center.y - 100, self.name,color='#990033')


class HangingBaseConer(Element):
    name = "转角吊柜"
    def __init__(self, backline, length):
        super(HangingBaseConer, self).__init__()
        self.set_pos(backline, length)
        self.height = KITCHEN_HANGING_H
        # self.back_dir_line = DY_segment(backline.p2,
        # backline.p2 + backline.normal.p2 * HANGING_BASE_CORNER_LW[0])

    def draw(self, ax):
        backlength = self.backline.seg.length
        xdata = (self.backline.p1.x, self.backline.p2.x)
        ydata = (self.backline.p1.y, self.backline.p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#000000', linestyle='-'))
        p1 = self.backline.p2
        p2 = p1 + self.backline.normal.p2 * self.len
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-'))
        p1 = self.backline.p1
        p2 = p1 + self.backline.normal.p2 * HANGING_CABINET_L
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-'))
        p1 = p2
        p2 = p1 + self.backline.dir.p2 * (backlength - HANGING_CABINET_L)
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-'))
        p1 = p2
        p2 = p1 + self.backline.normal.p2 * (backlength - HANGING_CABINET_L)
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-'))
        p1 = p2
        p2 = p1 + self.backline.dir.p2 * HANGING_CABINET_L
        xdata = (p1.x, p2.x)
        ydata = (p1.y, p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#990033', linestyle='-'))
        p = sorted(self.boundary.polygon.vertices, key=lambda v:v.y)
        center = Segment(p[2], p[3]).midpoint
        ax.text(center.x, center.y - 100, self.name,color='#990033')

