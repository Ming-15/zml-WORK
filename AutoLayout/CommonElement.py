from AutoLayout.BaseModual import *
from AutoLayout.settings import *

class Door(Element):
    name = "门"
    """门是一个虚拟的家具组件，可以放置在所属功能区域之外"""
    def __init__(self):
        super(Door, self).__init__()
        self.name = "门"
        self.door_body = None #决定了开门的位置
        self.connect_list = []
        self.type = None

    # def set_boundary(self, bound, back_line, door_body):
    #     super(Door, self).set_boundary(bound, back_line)
    #     self.door_body = door_body
    def set_type(self, type):
        if type not in DOOR_TYPE:
            raise Exception("unknow door type")
        self.type = type

    def set_backline(self, bkl):
        # if self.boundary is None:
        # # 推拉门宽度设为1 mm，要符合顺时针原则
        #     if bkl.p1.x == bkl.p2.x:
        #         if bkl.p1.y > bkl.p2.y:
        #             p3 = Point(bkl.p2.x - 1, bkl.y)
        #             p4 = Point(bkl.p1.x - 1, bkl.y)
        #         else:
        #             p3 = Point(bkl.p2.x + 1, bkl.y)
        #             p4 = Point(bkl.p1.x + 1, bkl.y)
        #     elif bkl.p1.y == bkl.p1.y:
        #         if bkl.p1.x > bkl.p2.x:
        #             p3 = Point(bkl.p2.x, bkl.p2.y + 1)
        #             p4 = Point(bkl.p1.x, bkl.p1.y + 1)
        #         else:
        #             p3 = Point(bkl.p2.x, bkl.p2.y + 1)
        #             p4 = Point(bkl.p1.x, bkl.p1.y + 1)
        #     b = DY_boundary(bkl.p1, bkl.p2, p3, p4)
        #     self.set_boundary(b)
        super(Door, self).set_backline(bkl)

    def set_connect_list(self, name1, name2):
        # undo: check name sting
        self.connect_list.clear()
        self.connect_list.append(name1)
        self.connect_list.append(name2)

    def set_body(self, seg):
        # undo: check in boundary
        self.door_body = seg

    def draw(self, ax):
        self.boundary.draw(ax, ls='-', col='#9AFF9A') # 门用绿色表示

        xdata = (self.backline.p1.x, self.backline.p2.x)
        ydata = (self.backline.p1.y, self.backline.p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#FFFFFF'))# 门墙结合处没有颜色
        # xdata = (self.door_body.p1.x, self.door_body.p2.x)
        # ydata = (self.door_body.p1.y, self.door_body.p2.y)
        # ax.add_line(Line2D(xdata, ydata, color='#9AFF9A'))

        l0 = Line(self.point_list[0], self.point_list[2])
        l1 = Line(self.point_list[1], self.point_list[3])
        xdata = (l0.p1.x, l0.p2.x)
        ydata = (l0.p1.y, l0.p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#9AFF9A'))
        xdata = (l1.p1.x, l1.p2.x)
        ydata = (l1.p1.y, l1.p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#9AFF9A'))

class Curtain(Element):
    name = "窗帘"
    def __init__(self):
        super(Curtain, self).__init__()
        self.len = CURTAIN_LEN

class NightTable(Element):
    name = "床头柜"
    def __init__(self):
        super(NightTable, self).__init__()
        self.len = BEDSIDE_NIGHTTABLE_LEN

class Recliner(Element):
    name = "躺椅"
    def __init__(self):
        super(Recliner, self).__init__()
        self.len = RECLINERS_WIDTH_LEN[1]
    def __init__(self, backline):
        super(Recliner, self).__init__()
        self.len = RECLINERS_WIDTH_LEN[1]
        self.set_pos(backline, self.len)

class Closet(Element):
    name = "衣柜"
    def __init__(self):
        super(Closet, self).__init__()
        self.len = CLOSET_LEN
    def __init__(self, backline):
        super(Closet, self).__init__()
        self.len = CLOSET_LEN
        self.set_pos(backline, self.len)

class Drawers(Element):
    name = "屉柜"
    def __init__(self):
        super(Drawers, self).__init__()
        self.len = DRAWER_LEN
    def __init__(self, backline):
        super(Drawers, self).__init__()
        self.len = DRAWER_LEN
        self.set_pos(backline, self.len)

class WritingDeskAndChair(Element):
    name = "写字桌单椅组件"
    def __init__(self, backline):
        super(WritingDeskAndChair, self).__init__()
        self.len = WRITING_DESK_LEN + int(CHAIR_LEN / 2)
        self.set_pos(backline, self.len)
        self.is_multiple = True
        self.ele_list = []
        # 放置写字桌
        desk = WritingDesk(self.backline)
        self.ele_list.append(desk)
        # 放置单椅
        mid = self.backline.seg.midpoint
        p1 = mid + self.backline.normal.p2 * self.len + self.backline.dir.p2 * int(CHAIR_WIDTH / 2)
        p2 = mid + self.backline.normal.p2 * self.len - self.backline.dir.p2 * int(CHAIR_WIDTH / 2)
        ch_normal = Ray(Point(0,0), self.backline.normal.p2 * (-1))
        p1, p2 = DY_segment.get_p1_p2_from_normal(ch_normal, p1, p2)
        bl = DY_segment(p1, p2)
        chair = Chair(bl)
        self.ele_list.append(chair)

    # def draw(self, ax):
    #     self.boundary.draw(ax, col='#000000')
    #     desk = Element()
    #     desk.set_pos(self.backline, WRITING_DESK_LEN)
    #     desk.boundary.draw(ax, col='#000000')
    #
    #     mid = self.backline.seg.midpoint
    #     p1 = mid + self.backline.normal.p2 * self.len + self.backline.dir.p2 * int(CHAIR_WIDTH / 2)
    #     p2 = mid + self.backline.normal.p2 * self.len - self.backline.dir.p2 * int(CHAIR_WIDTH / 2)
    #     ch_normal = Ray(Point(0,0), self.backline.normal.p2 * (-1))
    #     p1, p2 = DY_segment.get_p1_p2_from_normal(ch_normal, p1, p2)
    #     bl = DY_segment(p1, p2)
    #     chair = Element()
    #     chair.set_pos(bl, CHAIR_LEN)
    #     chair.boundary.draw(ax)

class WritingDesk(Element):
    name = "写字桌"
    def __init__(self, backline):
        super(WritingDesk, self).__init__()
        self.set_pos(backline, WRITING_DESK_LEN)

class Chair(Element):
    name = "单椅"
    def __init__(self, backline):
        super(Chair, self).__init__()
        self.set_pos(backline, CHAIR_LEN)



