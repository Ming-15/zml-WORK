# -*- coding:utf-8 -*-
import AutoLayout.bedroom.Base as bd
import AutoLayout.BaseClass as BaseClass
import AutoLayout.DY_Line as DY_Line, AutoLayout.CommonElement as CommonElement
import AutoLayout.helpers as helpers
import AutoLayout.BaseModual as BaseModual

import sympy.geometry as sge

DOOR_LEN = 900
DOOR_OFF = 200

def test_411(len, wid, win_pos_type, win_offset, win_len, door_pos_type):
    p0 = sge.Point(0, 0)
    p1 = sge.Point(p0.x, p0.y + len)
    p2 = sge.Point(p0.x + wid, p0.y + len)
    p3 = sge.Point(p0.x + wid, p0.y)

    brm = bd.Bedroom()
    brm.set_boundary(BaseClass.DY_boundary(p0, p1, p2, p3))

    if win_pos_type == 0:
        # p0 向上偏移
        win_p0 = sge.Point(p0.x, p0.y + win_offset)
        win_p1 = sge.Point(win_p0.x, win_p0.y + win_len)
        win = DY_Line.Window(win_p0, win_p1)
        brm.add_window(win)

    dr = CommonElement.Door()
    if door_pos_type == 1:
        # p1 向右
        dr_p0 = sge.Point(p1.x + DOOR_OFF, p1.y)
        dr_p1 = sge.Point(dr_p0.x + DOOR_LEN, dr_p0.y)
        dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)
    brm.add_door(dr)

    hou = BaseClass.House()
    fp = BaseModual.FloorPlan()
    fp.set_boundary(BaseClass.DY_boundary(p0, p1, p2, p3))
    fp.add_region(brm)
    hou.add_floorplan(fp)
    # brm.draw()
    helpers.save_house_to_xml(hou, r'E:/h.xml')

if __name__=="__main__":
    test_411(3000, 3000, 0, 500, 1000, 1)
