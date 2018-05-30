# -*- coding:utf-8 -*-
# import AutoLayout.livingroom.Base
from sympy.geometry import Segment2D

import AutoLayout.CommonElement as CommonElement
from AutoLayout import BaseClass
from AutoLayout import DY_Line


def get_idx_probability(length_list, rand):
    """在可选择范围内，越接近，几率越大
    如idx: 1,2,3的几率为 (1/14, 4/14, 9/14)"""
    length_list = sorted(length_list)
    prob_list = [(i + 1) ** 2 for i in range(len(length_list))]
    prob_list = [i / sum(prob_list) for i in prob_list]
    threshold_list = []
    total = 0
    for p in prob_list:
        total += p
        threshold_list.append(total)
    for i, prob in enumerate(threshold_list):
        if rand / prob < 1:
            idx = i
            break
    return idx


def get_two_wall_dis(wall1, wall2):
    mid1 = wall1.seg.midpoint
    mid2 = wall2.seg.midpoint
    dis = mid1.distance(mid2)
    return dis


# 存在阳台的情况下,得到虚拟边界中据阳台
def ele_connect_wall(ele, boundary):
    main_wall = []
    for seg in boundary.seg_list:
        if seg.line.is_parallel(ele.line):
            main_wall.append(seg)
    dis0 = main_wall[0].seg.distance(ele.seg.midpoint)
    dis1 = main_wall[1].seg.distance(ele.seg.midpoint)
    if dis0 > dis1:
        main_wall.remove(main_wall[0])
    else:
        main_wall.remove(main_wall[1])
    return main_wall


# 确定放置电视柜,沙发所在墙
def tv_sofa_wall_func(main_wall, boundary):
    wall_list = []
    tv_or_wall_1 = DY_Line.Ray(main_wall.seg.p1, main_wall.dir.p2)
    all_list = tv_or_wall_1.intersection(boundary.polygon)


# 门窗在虚拟边界的映射
def dr_win_in_virtual_boundary(ele, virtual_boundary):
    par_list = []
    midpoint1 = ele.boundary.polygon.centroid
    '''
    窗的映射暂时删掉，布局时窗户无需避开
    if isinstance(ele, DY_Line.Window):
        midpoint2 = ele.seg.midpoint
        seg_length = ele.seg.length
    '''
    if isinstance(ele, CommonElement.Door):
        midpoint2 = ele.backline.seg.midpoint
        seg_length = ele.backline.seg.length
    for seg in virtual_boundary.seg_list:
        '''
        if isinstance(ele, DY_Line.Window):
            if seg.line.is_parallel(ele.line):
                par_list.append(seg)
        '''
        if isinstance(ele, CommonElement.Door):
            if seg.line.is_parallel(ele.backline.line):
                par_list.append(seg)
    # distance方法必须是线到点的距离,顺序不可变
    dis0 = par_list[0].seg.distance(midpoint1)
    dis1 = par_list[1].seg.distance(midpoint1)
    if dis0 < dis1:
        par_list.remove(par_list[1])
    else:
        par_list.remove(par_list[0])
    line_dr_win = DY_Line.Line(midpoint1, midpoint2)
    inter_list_point = par_list[0].seg.intersection(line_dr_win)
    if inter_list_point != []:
        p1 = inter_list_point[0] + par_list[0].dir.p2 * (seg_length / 2)
        p2 = inter_list_point[0] - par_list[0].dir.p2 * (seg_length / 2)
        win_or_dr = BaseClass.DY_segment(p1, p2)
    else:
        win_or_dr = None
    return win_or_dr


# 确定电视柜墙, 沙发墙
def tv_sofa_area_wall(seg, boundary):
    inter_list = seg.seg.intersection(boundary.polygon)
    length_seg = []
    seg_list = []
    for i in inter_list:
        if isinstance(i, Segment2D):
            length_seg.append(i.length)
            seg_list.append(i)
    for s in seg_list:
        if s.length == max(length_seg):
            wall = s

    wall = BaseClass.DY_segment(wall.p1, wall.p2)
    return wall


# 更新沙发电视柜所在墙
def update_tv_sofa_wall(seg, ele, main_wall, main_wall_normal):
    if main_wall.seg.distance(seg.seg.p1) < main_wall.seg.distance(seg.seg.p2):
        p11 = seg.seg.p1
        p22 = p11 + main_wall_normal.p2 * 1
    else:
        p11 = seg.seg.p2
        p22 = p11 + main_wall_normal.p2 * 1

    tv_or_wall_1 = DY_Line.Ray(p11, p22)

    all_list = tv_or_wall_1.intersection(ele.seg)
    avoid_area = all_list[0]
    if main_wall.seg.distance(avoid_area.p1) < main_wall.seg.distance(avoid_area.p2):
        p1 = avoid_area.p1
    else:
        p1 = avoid_area.p2
    if p1 == p11:
        p11 = p1 + seg.dir.p2 * 1
    new_wall = BaseClass.DY_segment(p11, p1)
    return new_wall


# 布置主窗的窗帘
def arrange_main_curtain(win, line_list, ele_list, virtual_boundary):
    main_win_wall = win.wall
    main_curtain = CommonElement.Curtain()

    full_flag = True
    for e in ele_list:
        backline = dr_win_in_virtual_boundary(e, virtual_boundary)
        if backline != None:
            if main_win_wall.seg.contains(backline.seg):
                full_flag = False
    for bor in line_list:
        if isinstance(bor, DY_Line.Border):
            if main_win_wall.seg.contains(bor.seg):
                full_flag = False
    if full_flag is True:
        backline = win.wall
        main_curtain.set_pos(backline, main_curtain.len)
    else:
        backline = BaseClass.DY_segment(win.p1, win.p2)
        main_curtain.set_pos(backline, main_curtain.len)

    ele_list.append(main_curtain)
    return win, main_curtain, main_win_wall


def get_win_list(line_list):
    win_list = []
    for l in line_list:
        if isinstance(l, DY_Line.Window):
            win_list.append(l)

    return win_list
