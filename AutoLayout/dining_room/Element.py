from AutoLayout.BaseModual import *
from AutoLayout.dining_room.settings import *

class SideboardCabinet(Element):
    name = "餐边柜"
    def __init__(self, backline, length):
        super(SideboardCabinet, self).__init__()
        self.set_pos(backline, length)

class RoundDiningTable(Element):
    name = "圆餐桌"
    def __init__(self):
        super(RoundDiningTable, self).__init__()

class SquareDiningTable(Element):
    name = "方餐桌"
    def __init__(self, backline, length):
        super(SquareDiningTable, self).__init__()
        self.set_pos(backline, length)

class DiningChair(Element):
    name = "餐椅"
    def __init__(self, backline, length):
        super(DiningChair, self).__init__()
        self.set_pos(backline, length)

class DeckSofa(Element):
    name = "卡座沙发"
    def __init__(self):
        super(DeckSofa, self).__init__()

"""
class DiningTableChairArea(Element):
    name = "餐厅桌椅组件"
    def __init__(self):
        super(DiningTableChairArea, self).__init__()
        self.is_multiple = True
        self.is_true = False
        self.ele_list = []

    def run(self):
        arrangement_dict = {
            0:self.run1, # 4人桌椅
            1:self.run2  # 6人桌椅
        }
        key = 1
        arrangement_dict.get(key)()

    def run1(self):
        pass

    def run2(self):
        # 放置餐桌
        desk = SquareDiningTable(self.backline, self.len)
        self.ele_list.append(desk)
        # 放置餐椅
        mid = self.backline.seg.midpoint
        p1 = mid + self.backline.dir.p2 * (self.len) + self.backline.normal.p2 * int(DINING_CHAIR)
        p2 = mid + self.backline.dir.p2 * (self.len) - self.backline.normal.p2 * int(DINING_CHAIR)
        ch_normal = Ray(Point(0,0), self.backline.normal.p2 * (-1))
        p1, p2 = DY_segment.get_p1_p2_from_normal(ch_normal, p1, p2)
        bl = DY_segment(p1, p2)
        chair = DiningChair(bl)
        self.ele_list.append(chair)
"""

