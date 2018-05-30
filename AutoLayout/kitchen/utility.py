# -*- coding:utf-8 -*-
from AutoLayout.kitchen.settings import *
from AutoLayout.kitchen.Element import *
from sympy.geometry import Point2D, Segment2D
import AutoLayout.BaseClass as BaseClass
from AutoLayout.BaseClass import DY_segment, DY_boundary
import AutoLayout.helpers as helpers
import AutoLayout.settings as settings


def room_size_judgement(boundary):
    xmin, ymin, xmax, ymax = boundary.polygon.bounds
    xlen = xmax - xmin
    ylen = ymax - ymin

    l, w = (xlen, ylen) if xlen > ylen else (ylen, xlen)
    # if l > KITCHEN_MAX_LEN or l < KITCHEN_MIN_LEN:
    #     raise Exception("warning:厨房功能区长宽不足")
    # if w > KITCHEN_MAX_LEN or w < KITCHEN_MIN_LEN:
    #     raise Exception("warning:厨房功能区长宽不足")
    return l, w

def door_boundary(door,boundary):
    door_boun_list = door.backline.seg.intersection(boundary.polygon)
    if door_boun_list == []:
        par_list = []
        for seg in boundary.seg_list:
            if seg.line.is_parallel(door.backline.line):
                par_list.append(seg)
        dis0 = par_list[0].seg.distance(door.boundary.polygon.centroid)
        dis1 = par_list[1].seg.distance(door.boundary.polygon.centroid)
        if dis0 > dis1:
            doorboun_boun_list = door.boundary.polygon.intersection(par_list[1].seg)
        else:
            doorboun_boun_list = door.boundary.polygon.intersection(par_list[0].seg)
        if len(doorboun_boun_list) == 1:
            door.backline = DY_segment(doorboun_boun_list[0].p1, doorboun_boun_list[0].p2)
        else:
            door.backline = DY_segment(doorboun_boun_list[0], doorboun_boun_list[1])

    else:
        door.backline= door.backline
    return door.backline
# 门的backline在外墙时,将backline映射到boundary中
door_backline_list = []
def door_backline_boundary(door,boundary):
    point_flag = False
    segment_flag = False
    door_boun_list = door.boundary.polygon.intersection(boundary.polygon)
    for p in door_boun_list:
        if isinstance(p, Point2D):
            point_flag = True
        if isinstance(p, Segment2D):
            segment_flag = True
    if point_flag == True and segment_flag == False:
        backline = DY_segment(door_boun_list[0], door_boun_list[1])
    elif point_flag == True and segment_flag == True:
        for i in door_boun_list:
            if isinstance(i, Segment2D):
                seg = i
            if isinstance(i, Point2D):
                point = i
        if seg.p1.distance(point) > seg.p2.distance(point):
            door_boun_list.append(seg.p2)
        else:
            door_boun_list.append(seg.p1)
        door_boun_list.remove(seg)
        backline = DY_segment(door_boun_list[0], door_boun_list[1])
    elif point_flag == False and segment_flag == True:
        backline = DY_segment(door_boun_list[0].p1, door_boun_list[0].p2)
    door_backline_list.append(backline)
    return door_backline_list

def get_triangle_vertice(door, boundary):
    dr_center = door.boundary.polygon.centroid
    corner = sorted(boundary.polygon.vertices, key=lambda v: dr_center.distance(v))

    return corner[-1]


def get_triangle_vertice_U(door, win, boundary):
    dr_center = door.boundary.polygon.centroid
    win_center = win.boundary.polygon.centroid
    corner = sorted(boundary.polygon.vertices, key=lambda v: dr_center.distance(v))
    win_corner = sorted(corner[-2:-1], key=lambda v: win_center.distance(v), reverse=True)

    return win_corner[-1]


# U型的角点是根据窗户中心点距离角点的距离决定的,距离近的为角点
def get__U_triangle_vertice(win, u0):
    win_center = win.boundary.polygon.centroid
    corner = sorted([u0.seg.p1, u0.seg.p2], key=lambda v: win_center.distance(v))
    return corner[0]


def get_l_flag_has_border_or_anotherdoor(door, boundary, border=None, door_bal=None):
    dr_center = door.boundary.polygon.centroid
    corner = sorted(boundary.polygon.vertices, key=lambda v: dr_center.distance(v))
    change_tri_vertice = False
    if border is not None:
        if border.wall.seg.contains(corner[-1]):
            return False
    elif door_bal is not None:
        tmp_seg = DY_segment(door_bal.backline.normal.p1, door_bal.backline.normal.p2)
        parallel_dr = helpers.get_paralleled_line(tmp_seg, door_bal.boundary, type=DY_segment)
        v_dr_dis0 = parallel_dr[0].line.distance(corner[-1])
        v_dr_dis1 = parallel_dr[1].line.distance(corner[-1])
        v_dr_dis = min(v_dr_dis0, v_dr_dis1)
        door_wall = [s for s in boundary.seg_list if s.seg.is_parallel(door_bal.backline.seg) and \
                     door_bal.boundary.polygon.intersection(s.seg) is not None][0]
        if door_wall.seg.contains(corner[-1]):
            if v_dr_dis >= MAX_DIS_CORNER_SINK_RAN:
                return True
            else:
                return False
    else:
        return True


def get_doorbackline_wall_dis(boundary, door1, door2=None):
    dis0, dis1, dis2, dis3 = 0, 0, 0, 0
    if door1 is not None:
        if door1.type == settings.DOOR_TYPE[0] or settings.DOOR_TYPE[1]:
            tmp_seg = DY_segment(door1.backline.normal.p1, door1.backline.normal.p2)
            parallel_wall_dr = helpers.get_paralleled_line(tmp_seg, boundary, type=DY_segment)
            tmp_seg = parallel_wall_dr[0]
            dis0 = helpers.get_min_dis_seg_boundary(tmp_seg, door1.boundary)
            tmp_seg = parallel_wall_dr[1]
            dis1 = helpers.get_min_dis_seg_boundary(tmp_seg, door1.boundary)
    if door2 is not None:
        if door2.type == settings.DOOR_TYPE[0] or settings.DOOR_TYPE[1]:
            tmp_seg = DY_segment(door2.backline.normal.p1, door2.backline.normal.p2)
            parallel_wall_dr = helpers.get_paralleled_line(tmp_seg, boundary, type=DY_segment)
            tmp_seg = parallel_wall_dr[0]
            dis2 = helpers.get_min_dis_seg_boundary(tmp_seg, door2.boundary)
            tmp_seg = parallel_wall_dr[1]
            dis3 = helpers.get_min_dis_seg_boundary(tmp_seg, door2.boundary)
    return dis0, dis1, dis2, dis3


def get_hanging_corner_cabinet(seg1, seg2, vertice, hang_w, ele_list):
    """根据角落，和形成角落的两条线，放置转角吊柜"""
    bl_wall = None
    if seg1.p2 == vertice:
        p2 = seg1.p2
        p1 = p2 - seg1.dir.p2 * hang_w
        p1, p2 = BaseClass.DY_segment.get_p1_p2_from_normal(
            seg1.normal, p1, p2)
        backline = BaseClass.DY_segment(p1, p2)
        corner = HangingBaseConer(backline, hang_w)
        ele_list.append(corner)
        bl_wall = seg1
    elif seg2.p2 == vertice:
        p2 = seg2.p2
        p1 = p2 - seg2.dir.p2 * hang_w
        p1, p2 = BaseClass.DY_segment.get_p1_p2_from_normal(
            seg2.normal, p1, p2)
        backline = BaseClass.DY_segment(p1, p2)
        corner = HangingBaseConer(backline, hang_w)
        ele_list.append(corner)
        bl_wall = seg2
    else:
        raise Exception("要布置转角吊柜的顶点有误")
    return corner, bl_wall


def is_arrange_hanging_corner(seg1, seg2, vertice, boundary, win, hang_corner_w):
    """根据窗户到角落的距离，判断是否放置转角柜"""
    corner_seg = [seg for seg in boundary.seg_list
                  if seg.line.is_similar(seg1.line) or seg.line.is_similar(seg2.line)]
    # corner_seg取出放置转角吊柜的两条边
    res = False
    for seg in corner_seg:
        if seg.seg.contains(win.seg):
            dis = win.seg.distance(vertice)
            if dis >= hang_corner_w:
                res = True
    if win.wall.seg.contains(vertice) is False:
        res = True
    return res


def arrange_hanging_along_seg(seg, hang_w, start_pt, ele_list, boundary, res_flag=False):
    """沿一条直线布置吊柜"""
    hanging_num = int(seg.seg.length / hang_w)
    hanging_num_double = int(hanging_num / 2)
    hanging_num_single = hanging_num % 2
    res_len = seg.seg.length - hanging_num_double * hang_w * 2 \
              - hanging_num_single * hang_w
    for v in boundary.polygon.vertices:
        if v == seg.p1 or v == seg.p2:
            res_flag = True
            break
    if seg.p1 == start_pt:
        arrange_dircetion = seg.dir.p2
    elif seg.p2 == start_pt:
        arrange_dircetion = -seg.dir.p2
    else:
        raise Exception("吊柜顶点有误")
    p1 = start_pt
    for i in range(hanging_num_double):
        p2 = p1 + arrange_dircetion * hang_w * 2
        p1n, p2n = BaseClass.DY_segment.get_p1_p2_from_normal(
            seg.normal, p1, p2)
        backline = BaseClass.DY_segment(p1n, p2n)
        hang_d = DoubleHangingCabinet(backline, HANGING_CABINET_L)
        ele_list.append(hang_d)
        p1 = p2
    if hanging_num_single > 0:
        p2 = p1 + arrange_dircetion * hang_w
        p1n, p2n = BaseClass.DY_segment.get_p1_p2_from_normal(
            seg.normal, p1, p2)
        backline = BaseClass.DY_segment(p1n, p2n)
        hang_s = SingleHangingCabinet(backline, HANGING_CABINET_L)
        ele_list.append(hang_s)
        p1 = p2
    if res_flag is True and 0 < res_len < HANGING_ADJUSTING_PANEL_MAX:
        p2 = p1 + arrange_dircetion * res_len
        p1n, p2n = BaseClass.DY_segment.get_p1_p2_from_normal(
            seg.normal, p1, p2)
        backline = BaseClass.DY_segment(p1n, p2n)
        hang = HangingAdjustingPanel(backline, HANGING_CABINET_L)
        ele_list.append(hang)
        if (hanging_num_single and hanging_num_double)== 0:
            ele_list.remove(hang)

def arrange_cabinet_along_seg(seg, start_pt, ele_list, df):
    """沿一条直线布置地柜"""
    if seg.p1 == start_pt:
        arrange_dircetion = seg.dir.p2
    elif seg.p2 == start_pt:
        arrange_dircetion = -seg.dir.p2
    else:
        raise Exception("warning:地柜顶点有误")

    df0 = df.loc[df.sum_len < seg.seg.length]
    df0 = df0.ix[df0.sum_len.idxmax]
    res_len = seg.seg.length - df0['sum_len']
    p1 = start_pt
    if df0['double_cab_wid'] != 0:
        p2 = p1 + arrange_dircetion * df0['double_cab_wid']
        p1n, p2n = BaseClass.DY_segment.get_p1_p2_from_normal(
            seg.normal, p1, p2)
        backline = BaseClass.DY_segment(p1n, p2n)
        ele = DoubleCabinet(backline, CABINET_L)
        ele_list.append(ele)
        p1 = p2
    if df0['single_cab_wid'] != 0:
        p2 = p1 + arrange_dircetion * df0['single_cab_wid']
        p1n, p2n = BaseClass.DY_segment.get_p1_p2_from_normal(
            seg.normal, p1, p2)
        backline = BaseClass.DY_segment(p1n, p2n)
        ele = SingleCabinet(backline, CABINET_L)
        ele_list.append(ele)
        p1 = p2
    if df0['pull_wid'] != 0:
        p2 = p1 + arrange_dircetion * df0['pull_wid']
        p1n, p2n = BaseClass.DY_segment.get_p1_p2_from_normal(
            seg.normal, p1, p2)
        backline = BaseClass.DY_segment(p1n, p2n)
        ele = PullBasket(backline, CABINET_L)
        ele_list.append(ele)
        p1 = p2

    if res_len == 0:
        return
    elif res_len < ADJUSTING_PANEL_MAX:
        p2 = p1 + arrange_dircetion * res_len
        p1n, p2n = BaseClass.DY_segment.get_p1_p2_from_normal(
            seg.normal, p1, p2)
        backline = BaseClass.DY_segment(p1n, p2n)
        ele = AdjustingPanel(backline, CABINET_L)
        ele_list.append(ele)
        p1 = p2
        return
    else:
        p2 = p1 + arrange_dircetion * res_len
        p1n, p2n = BaseClass.DY_segment.get_p1_p2_from_normal(
            seg.normal, p1, p2)
        seg_new = BaseClass.DY_segment(p1n, p2n)
        arrange_cabinet_along_seg(seg_new, p1, ele_list, df)

# 判断是否移动start_point的
def tri_arrange_startp(start_point, endpoint, triangle_vertice):
    line_s = BaseClass.DY_segment(start_point, triangle_vertice)
    line_e = BaseClass.DY_segment(endpoint, triangle_vertice)#应该改为求距离方式比较
    if line_s.seg.length > line_e.seg.length:
        return False
    else:
        return True
