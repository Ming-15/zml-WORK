#—*— coding: utf-8 _*_
__author__ = 'jxh'

from AutoLayout.BaseModual import Element, DY_segment
from AutoLayout.balcony.settings import *
from AutoLayout.helpers import *


class Leisure_Chairs_and_Tables(Element):
    name = "阳台休闲桌椅套件"
    def __init__(self,backline):
        super(Leisure_Chairs_and_Tables, self).__init__()
        self.len = CIRCLEDESK_D
        self.set_pos(backline,self.len)
        self.is_multiple = True
        self.ele_list = []
        #put the Desk
        mid = Point2D(int(self.backline.seg.midpoint.x),int(self.backline.seg.midpoint.y))
        p1 = mid + self.backline.dir.p2 * int(CIRCLEDESK_D / 2)
        p2 = mid - self.backline.dir.p2 * int(CIRCLEDESK_D / 2)
        desk_p1,desk_p2 = DY_segment.get_p1_p2_from_normal(self.backline.normal,p1,p2)
        desk_bl = DY_segment(desk_p1,desk_p2)
        desk = CircleDesk(desk_bl)
        self.ele_list.append(desk)
        #put two chairs beside the desk
        mid1 = mid + self.backline.dir.p2 * (int(CIRCLEDESK_D / 2) +
                INTERNAL_LEN + int(LEISURE_CHAIR_WID_LEN / 2))+ self.backline.normal.p2 * int(CIRCLEDESK_D / 2)
        mid2 = mid - self.backline.dir.p2 * (int(CIRCLEDESK_D / 2) +
                INTERNAL_LEN + int(LEISURE_CHAIR_WID_LEN / 2)) + self.backline.normal.p2 * int(CIRCLEDESK_D / 2)
        chair1_p1 = mid1 + self.backline.dir.p2 * int(LEISURE_CHAIR_WID_LEN / 2)
        chair1_p2 = mid1 - self.backline.dir.p2 * int(LEISURE_CHAIR_WID_LEN / 2)
        chair1_p1,chair1_p2 = DY_segment.get_p1_p2_from_normal(self.backline.normal,chair1_p1, chair1_p2)
        chair1_bl = DY_segment(chair1_p1,chair1_p2)
        chair1 = LeisureChair(chair1_bl)
        self.ele_list.append(chair1)
        chair2_p1 = mid2 + self.backline.dir.p2 * int(LEISURE_CHAIR_WID_LEN / 2)
        chair2_p2 = mid2 - self.backline.dir.p2 * int(LEISURE_CHAIR_WID_LEN / 2)
        chair2_p1, chair2_p2 = DY_segment.get_p1_p2_from_normal(self.backline.normal, chair2_p1, chair2_p2)
        chair2_bl = DY_segment(chair2_p1, chair2_p2)
        chair2 = LeisureChair(chair2_bl)
        self.ele_list.append(chair2)

class CircleDesk(Element):
    name = "阳台圆桌"
    def __init__(self, backline):
        super(CircleDesk, self).__init__()
        self.set_pos(backline, CIRCLEDESK_D)

class LeisureChair(Element):
    name = "休闲单椅"
    def __init__(self, backline):
        super(LeisureChair, self).__init__()
        self.set_pos(backline, LEISURE_CHAIR_WID_LEN)