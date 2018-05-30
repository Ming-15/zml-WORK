# -*- coding:utf-8 -*-

import AutoLayout.livingroom.Base as lb
import AutoLayout.BaseClass as BaseClass
import AutoLayout.DY_Line as DY_Line, AutoLayout.CommonElement as CommonElement, AutoLayout.BaseModual as BaseModual
import AutoLayout.helpers as helpers

import sympy.geometry as sge

DOOR_LEN = 900
DOOR_OFF = 200

def test4111(xlen, ylen, border_type, win_type, door_type, save_name):
    """
    win_type, border_type 0: 靠下; 1: left; 2: up; 3: right
    door_type: 0, 1: down right, d left;
              2, 3: left down, l up;
              4, 5: up left, up right;
              6, 7: right up, r down;
    """
    p0 = sge.Point(0, 0)
    p1 = sge.Point(p0.x, p0.y + ylen)
    p2 = sge.Point(p0.x + xlen, p0.y + ylen)
    p3 = sge.Point(p0.x + xlen, p0.y)

    lvr = lb.Livingroom()
    lvr.set_boundary(BaseClass.DY_boundary(p0, p1, p2, p3))

    if border_type == 0:
        lvr.add_border(DY_Line.Border(p0, p3))
    elif border_type == 1:
        lvr.add_border(DY_Line.Border(p0, p1))
    elif border_type == 2:
        lvr.add_border(DY_Line.Border(p1, p2))
    elif border_type == 3:
        lvr.add_border(DY_Line.Border(p2, p3))

    if win_type == 0:
        win_off, win_len = int(xlen * 0.2), int(xlen * 0.6)
        win_p0 = sge.Point(p3.x - win_off, p3.y)
        win_p1 = sge.Point(win_p0.x - win_len, win_p0.y)
        lvr.add_window(DY_Line.Window(win_p0, win_p1))
    elif win_type == 1:
        win_off, win_len = int(ylen * 0.2), int(ylen * 0.6)
        win_p0 = sge.Point(p0.x, p0.y + win_off)
        win_p1 = sge.Point(win_p0.x, win_p0.y + win_len)
        lvr.add_window(DY_Line.Window(win_p0, win_p1))
    elif win_type == 2:
        win_off, win_len = int(xlen * 0.2), int(xlen * 0.6)
        win_p0 = sge.Point(p1.x + win_off, p1.y)
        win_p1 = sge.Point(win_p0.x + win_len, win_p0.y)
        lvr.add_window(DY_Line.Window(win_p0, win_p1))
    elif win_type == 3:
        win_off, win_len = int(ylen * 0.2), int(ylen * 0.6)
        win_p0 = sge.Point(p2.x, p2.y - win_off)
        win_p1 = sge.Point(win_p0.x, win_p0.y - win_len)
        lvr.add_window(DY_Line.Window(win_p0, win_p1))

    dr = CommonElement.Door()
    if door_type == 0:
        dr_p0 = sge.Point(p3.x - DOOR_LEN - DOOR_OFF, p3.y)
        dr_p1 = sge.Point(dr_p0.x + DOOR_LEN, dr_p0.y)
        dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1),DOOR_LEN)
    elif door_type == 1:
        dr_p0 = sge.Point(p0.x + DOOR_OFF, p0.y)
        dr_p1 = sge.Point(dr_p0.x + DOOR_LEN, p0.y)
        dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1),DOOR_LEN)
    elif door_type == 2:
        dr_p0 = sge.Point(p0.x, p0.y + DOOR_LEN + DOOR_OFF)
        dr_p1 = sge.Point(dr_p0.x, dr_p0.y - DOOR_LEN)
        dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)
    elif door_type == 3:
        dr_p0 = sge.Point(p1.x, p1.y - DOOR_OFF)
        dr_p1 = sge.Point(dr_p0.x, dr_p0.y - DOOR_LEN)
        dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)
    elif door_type == 4:
        dr_p0 = sge.Point(p1.x + DOOR_OFF + DOOR_LEN, p1.y)
        dr_p1 = sge.Point(dr_p0.x - DOOR_LEN, dr_p0.y)
        dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)
    elif door_type == 5:
        dr_p0 = sge.Point(p2.x - DOOR_OFF, p2.y)
        dr_p1 = sge.Point(dr_p0.x - DOOR_LEN, dr_p0.y)
        dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)
    elif door_type == 6:
        dr_p0 = sge.Point(p2.x, p2.y - DOOR_LEN - DOOR_OFF)
        dr_p1 = sge.Point(dr_p0.x, dr_p0.y + DOOR_LEN)
        dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)
    elif door_type == 7:
        dr_p0 = sge.Point(p3.x, p3.y + DOOR_OFF)
        dr_p1 = sge.Point(dr_p0.x, dr_p0.y + DOOR_LEN)
        dr.set_pos(BaseClass.DY_segment(dr_p0, dr_p1), DOOR_LEN)
    lvr.add_door(dr)

    hou = BaseClass.House()
    fp = BaseModual.FloorPlan()
    fp.set_boundary(BaseClass.DY_boundary(p0, p1, p2, p3))
    fp.add_region(lvr)
    hou.add_floorplan(fp)
    lvr.draw(save_name[:-3] + 'png')
    helpers.save_house_to_xml(hou, save_name)

def batch_test():
    length_width = [(3600, 4200), (4000, 4500), (4500, 5100),
                    (4800, 6300), (4500, 4000), (5100, 4500)]
    save_path = r'E:\lv_test'
    cnter = 0
    for xlen, ylen in length_width:
        for brd_type in range(4):
            for w_type in range(4):
                if w_type == brd_type:
                    continue
                for dr_type in range(8):
                    tmpID = int(dr_type / 2)
                    if tmpID == w_type or tmpID == brd_type:
                        continue
                    s_name = save_path + '\\' + str(cnter) + '.xml'
                    test4111(xlen, ylen, brd_type, w_type, dr_type, s_name)
                    cnter = cnter + 1

if __name__ == "__main__":
    pass
