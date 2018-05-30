# -*- coding:utf-8 -*-
from AutoLayout.BaseModual import *
from AutoLayout.balcony.settings import *
import random
import AutoLayout.helpers
from AutoLayout.balcony.Element import *

class Balcony(AutoLayout.BaseModual.Region):

    def __init__(self):
        super(Balcony, self).__init__()
        self.main_win_wall = None

    def run(self):
        xmin, ymin, xmax, ymax = self.boundary.polygon.bounds
        xlen = xmax - xmin
        ylen = ymax - ymin
        if xlen < MIN_SIZE or xlen > MAX_SIZE or ylen < MIN_SIZE or \
                        ylen > MAX_SIZE:
            raise Exception("warning:阳台功能区长度或者宽度不满足")
        if abs(self.boundary.polygon.area) < MIN_SIZE * MIN_SIZE:
            raise Exception("warning:阳台功能区面积不满足")
        #暂时不考虑户型直接放置阳台的套件
        mid = Point2D(int(self.boundary.polygon.centroid.x),int(self.boundary.polygon.centroid.y))
        long_seg = [seg for seg in self.boundary.seg_list \
                    if seg.seg.length == max(xlen,ylen)]
        rand = random.randint(0,1)
        rand = 0
        long_seg_op = AutoLayout.helpers.get_opposite_bounds(long_seg[rand],self.boundary)[0]
        multi_mid = mid + long_seg[rand].normal.p2 * int(CIRCLEDESK_D / 2)
        p1 = multi_mid + long_seg[rand].dir.p2 * int(MULTI_WID / 2)
        p2 = multi_mid - long_seg[rand].dir.p2 * int(MULTI_WID / 2)
        p1,p2 = AutoLayout.BaseModual.DY_segment.\
            get_p1_p2_from_normal(long_seg_op.normal,p1,p2)
        leisure_zone_bl = AutoLayout.BaseModual.DY_segment(p1,p2)
        leisure_zone = Leisure_Chairs_and_Tables(leisure_zone_bl)
        self.ele_list.append(leisure_zone)