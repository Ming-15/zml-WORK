# -*- coding:utf-8 -*-
from AutoLayout.CommonElement import *
import AutoLayout.DY_Line as DY_Line

def arrange_tatami_main_curtain(line_list,ele_list):
    win_list = get_win_list(line_list)
    main_win_wall = win_list[0].wall
    main_curtain = Curtain()

    backline = DY_segment(win_list[0].p1, win_list[0].p2)
    main_curtain.set_pos(backline, main_curtain.len)

    ele_list.append(main_curtain)
    return win_list, main_curtain, main_win_wall
def get_win_list(line_list):
    """最长的窗户被认为是主窗，位于win_list[0]"""
    win_list = []
    for l in line_list:
        if isinstance(l, DY_Line.Window):
            win_list.append(l)
    win_list = sorted(win_list, key=lambda w: w.seg.length, reverse=True)

    return win_list