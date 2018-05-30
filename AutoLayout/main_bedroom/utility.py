from AutoLayout.main_bedroom.Base import *
from AutoLayout.CommonElement import *
import AutoLayout.DY_Line as DY_Line

def get_vir_win(line_list):
    """最长的部件被认为是主虚拟窗，位于win_list[0]"""
    win_list = []
    for l in line_list:
        if isinstance(l, DY_Line.Window) or isinstance(l, DY_Line.Border):
            win_list.append(l)
    win_list = sorted(win_list, key=lambda w: w.seg.length, reverse=True)

    return win_list

def arrange_main_curtain(line_list, ele_list):
    win_list = get_win_list(line_list)
    main_win_wall = win_list[0].wall
    main_curtain = Curtain()

    full_flag = True
    for e in ele_list:
        if main_win_wall.seg.contains(e.backline.seg):
            full_flag = False

    if full_flag is True:
        backline = win_list[0].wall
        main_curtain.set_pos(backline, main_curtain.len)
    else:
        backline = DY_segment(win_list[0].p1, win_list[0].p2)
        main_curtain.set_pos(backline, main_curtain.len)

    ele_list.append(main_curtain)
    return win_list, main_curtain, main_win_wall

def arrange_sub_curtain(line_list, ele_list):
    win_list = get_win_list(line_list)
    sub_win_wall = win_list[1].wall
    sub_curtain = Curtain()

    backline = DY_segment(win_list[1].p1, win_list[1].p2)
    sub_curtain.set_pos(backline, sub_curtain.len)

    ele_list.append(sub_curtain)
    return sub_curtain, sub_win_wall

def get_win_list(line_list):
    """最长的窗户被认为是主窗，位于win_list[0]"""
    win_list = []
    for l in line_list:
        if isinstance(l, DY_Line.Window):
            win_list.append(l)
    win_list = sorted(win_list, key=lambda w: w.seg.length, reverse=True)

    return win_list


# def get_nearst_point(seg, ref_seg):
#     """以ref_seg为固定，找到seg离ref_seg最近的端点"""
#     dis1 = ref_seg.distance(seg.p1)
#     dis2 = ref_seg.distance(seg.p2)
#     if dis1 > dis2:
#         return seg.p1
#     else:
#         return seg.p2

def arrange_drawers(bed_end_midray, ele_list, boundary, bed_instance=Bed):
    # undo: 考虑沿着墙凹下情况
    assert isinstance(bed_end_midray, DY_segment), "bed_end_midray必须是DY_segment的实例"

    r = Ray(bed_end_midray.p1, bed_end_midray.p2)
    inter_list = boundary.polygon.intersection(r)
    if len(inter_list) == 0:
        return False
    mid_drawer_bl = inter_list[0]
    mid_drawer_end = mid_drawer_bl - bed_end_midray.dir.p2 * DRAWER_LEN

    dis = mid_drawer_end.distance(bed_end_midray.p1)
    if dis < MAINBED_BED_END_THRE_DIS:
        return False
    # 以屉柜端线中点心为源点，沿屉柜两条射线

    dis_min = get_min_dis_seg_boundary(bed_end_midray, boundary)
    for e in ele_list:
        if isinstance(e, Door):
            dis_min_e = get_min_dis_seg_boundary(bed_end_midray, e.boundary)
            dis_min = min(dis_min, dis_min_e)
    if dis_min * 2 < DRAWER_WIDTH[0]:
        return False
    drawers_width = get_drawers_size(dis_min)

    for e in ele_list:
        if isinstance(e, bed_instance):
            bed = e
    p1 = mid_drawer_bl + bed.backline.dir.p2 * (int(drawers_width / 2))
    p2 = mid_drawer_bl - bed.backline.dir.p2 * (int(drawers_width / 2))
    norm = Ray(bed.dir.p1, bed.dir.p2 * (-1))
    p1, p2 = DY_segment.get_p1_p2_from_normal(norm, p1, p2)
    bl = DY_segment(p1, p2)
    drawers = Drawers(bl)

    ele_list.append(drawers)
    return True

def get_drawers_size(dis):
    width2 = [l/2 for l in DRAWER_WIDTH]
    for i, l in enumerate(width2[::-1]):
        if float(dis) / float(l) >= 1. :
            idx = i
            break
    idx = len(DRAWER_WIDTH) - 1 - idx
    return DRAWER_WIDTH[idx]

def arrange_writing_desk(ele_list, boundary, main_win_wall, bed_wall):
    # undo: 考虑沿着墙凹下情况
    dra_list = get_eles(ele_list, Drawers)
    if not dra_list:
        return False
    drawers = dra_list[0]

    if drawers.dir.is_parallel(main_win_wall.normal):
        # undo: 屉柜与窗户平行，放置写字桌
        return False
    v_dis = {v:main_win_wall.line.distance(v) for v in drawers.boundary.polygon.vertices}
    pt_dis_dict = sorted(v_dis.items(), key=lambda d: d[1])

    ry0 = Ray(pt_dis_dict[0][0], pt_dis_dict[0][0] + main_win_wall.normal.p2 * (-1))
    ry1 = Ray(pt_dis_dict[1][0], pt_dis_dict[1][0] + main_win_wall.normal.p2 * (-1))

    # 靠窗侧,屉柜到边界的最小距离
    paralled_seg = get_paralleled_line(main_win_wall, boundary, type=Segment)
    dis_list = []
    for s in paralled_seg:
        dlist = s.intersection(ry0)
        if dlist:
            dis_list.append(dlist[0].distance(ry0.p1))
        dlist = s.intersection(ry1)
        if dlist:
            dis_list.append(dlist[0].distance(ry1.p1))
    dis_min_b = sorted(dis_list)[0] - CURTAIN_LEN # 考虑窗帘的长度
    # 靠窗侧,屉柜到门的最小距离
    dis_list.clear()
    door_list = get_eles(ele_list, Door)
    for d in door_list:
        for bound in d.boundary.seg_list:
            if bound.line.is_parallel(main_win_wall.line):
                dlist = bound.seg.intersection(ry0)
                if dlist:
                    dis_list.append(dlist[0].distance(ry0.p1))
                dlist = bound.seg.intersection(ry1)
                if dlist:
                    dis_list.append(dlist[0].distance(ry1.p1))
    if len(dis_list) == 0:
        dis_min_door = 100000000
    else:
        dis_min_door = sorted(dis_list)[0]

    dis_min = min(dis_min_b, dis_min_door)

    if dis_min < WRITING_DESK_WIDTH[0]:
        return False

    for i, l in enumerate(WRITING_DESK_WIDTH[::-1]):
        if float(dis_min) / float(l) >= 1. :
            idx = i
            break
    idx = len(WRITING_DESK_WIDTH) - 1 - idx

    for b in boundary.seg_list:
        if b.seg.contains(pt_dis_dict[0][0]):
            bl_p1 = pt_dis_dict[0][0]
            break
        if b.seg.contains(pt_dis_dict[1][0]):
            bl_p1 = pt_dis_dict[1][0]
            break
    bl_p2 = bl_p1 + main_win_wall.normal.p2 * (-WRITING_DESK_WIDTH[idx])
    bl_p1, bl_p2 = DY_segment.get_p1_p2_from_normal(drawers.backline.normal, bl_p1, bl_p2)
    bl = DY_segment(bl_p1, bl_p2)
    w_desk = WritingDeskAndChair(bl)
    ele_list.append(w_desk)

    return True

def normalize_zone(normal_dir, relative_pos, self):
    """
    通过翻转、旋转归一化户型，使得目标在左下角
    输入：目标的法线，目标相对位置，self
    """
    # 法线方向朝上下
    if normal_dir.p2 == Point(0, 1):
        if float(relative_pos.x) < 0 and float(relative_pos.y) < 0:
            return True
        if float(relative_pos.x) > 0 and float(relative_pos.y) < 0:
            self.fliplr()
            self.flip_dict_num['fliplr'] += 1
            return True
    if normal_dir.p2 == Point(0, -1):
        if float(relative_pos.x) > 0 and float(relative_pos.y) > 0:
            self.fliplr()
            self.flip_dict_num['fliplr'] += 1
            self.flipup()
            self.flip_dict_num['flipup'] += 1
            return True
        if float(relative_pos.x) < 0 and float(relative_pos.y) > 0:
            self.flipup()
            self.flip_dict_num['flipup'] += 1
            return True
    # 法线方向朝左右
    if normal_dir.p2 == Point(1, 0):
        if float(relative_pos.x) < 0 and float(relative_pos.y) < 0:
            self.rotate90_anticlockwise()
            self.flip_dict_num['-rot90'] += 1
            self.fliplr()
            self.flip_dict_num['fliplr'] += 1
            return True
        if float(relative_pos.x) < 0 and float(relative_pos.y) > 0:
            self.rotate90_anticlockwise()
            self.flip_dict_num['-rot90'] += 1
            return True
    if normal_dir.p2 == Point(-1, 0):
        if float(relative_pos.x) > 0 and float(relative_pos.y) < 0:
            self.rotate90_clockwise()
            self.flip_dict_num['rot90'] += 1
            return True
        if float(relative_pos.x) > 0 and float(relative_pos.y) > 0:
            self.rotate90_clockwise()
            self.flip_dict_num['rot90'] += 1
            self.fliplr()
            self.flip_dict_num['fliplr'] += 1
            return True
    return False

def inverse_normalize_zone(self):
    for key, value in self.flip_dict_num.items():
        while(value > 0):
            if key == 'fliplr':
                self.fliplr()
            if key == 'flipup':
                self.flipup()
            if key == 'rot90':
                self.rotate90_anticlockwise()
            if key == '-rot90':
                self.rotate90_clockwise()
            value -= 1


