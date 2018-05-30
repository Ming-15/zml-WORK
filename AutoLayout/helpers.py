# _*_ coding: utf-8 _*_
import math
import shutil

import numpy
from lxml import etree

import AutoLayout.settings
from AutoLayout.BaseModual import *
from AutoLayout.DY_Line import *


def get_inner_line_list(boundary, concave_list=[]):
    ''' 得到向内凹的线'''
    if concave_list == []:
        concave_list, _ = concave_or_convex(boundary)
    inner_line_l = []
    for i in boundary.seg_list:
        if i.p1 in concave_list and i.p2 in concave_list:
            inner_line_l.append(i)
    return inner_line_l


def concave_or_convex_point(la, lb):
    return la.cross_dir(lb)


def concave_or_convex(boundary):
    '''concave表示凹点，convex表示凸点
    返回两个列表
    '''
    concave_list = []
    convex_list = []
    for v in boundary.polygon.vertices:
        v_list = get_adj_seg(v, boundary)
        a = another_p(v_list[0], v)
        if a == v_list[0].p1:
            la = v_list[0]
            lb = v_list[1]
        else:
            la = v_list[1]
            lb = v_list[0]
        tag = concave_or_convex_point(la, lb)
        if tag == 1:
            # 凹点
            concave_list.append(v)
        else:  # tag==-1:
            # 凸出点
            convex_list.append(v)
    return concave_list, convex_list


def cover_range(seg):
    if seg.p1.x == seg.p2.x:
        if seg.p1.y > seg.p2.y:
            return (seg.p2.y, seg.p1.y)
        else:
            return (seg.p1.y, seg.p2.y)
    else:
        if seg.p1.x > seg.p2.x:
            return (seg.p2.x, seg.p1.x)
        else:
            return (seg.p1.x, seg.p2.x)


def ray_ext(a, seg_list):
    vecter = a.dir.p2
    a2 = a.p2
    ray_line = DY_segment(a2, a2 + vecter * 100000000)
    ext_list = []
    for i in seg_list:
        if ray_line.seg.intersection(i.seg) != []:
            ext_list.append((i.line.distance(a2), ray_line.seg.intersection(i.seg)[0], i))
            # 返回元组有三项，距离，交点，交点线
    if ext_list == []:
        raise Exception('传入射线和列表有问题', a.p1, a.p2, vecter)
    else:
        ext_list.sort(key=lambda x: x[0])
    if ext_list[0][0] != 0:
        raise Exception('射线起始点不在凹凸点上，这个图形有问题', a.p1, a.p2)
    return ext_list


def is_staggerd(seg, area_range, need_tag=0):
    '''  测试边， 测试范围,测试范围自己先提前调用cover——range得到
    暂时返回值只用到0,1，但是用标记表明了各种相交情况，当需要时就可以更改返回值使用
    需要标记时第三个参数设置1，返回标志
    '''
    p_l = cover_range(seg)
    ar = [area_range[0], area_range[1]]
    ar.sort()
    if p_l[1] <= ar[0] or p_l[0] >= ar[1]:
        # waimian
        tag = 'n'
        re = 0
    elif p_l[0] <= ar[0] and p_l[1] > ar[0] and p_l[1] < ar[1]:
        tag = 'l'
        re = 1
    elif p_l[0] > ar[0] and p_l[1] < ar[1]:
        tag = 'm'
        re = 1
    elif p_l[0] > ar[0] and p_l[0] < ar[1] and p_l[1] > ar[1]:
        tag = 'r'
        re = 1
    else:
        tag = 'a'  # all
        re = 1
    if need_tag:
        return tag
    else:
        return re


def squar(a, b):
    '''对角点，算面积'''
    return abs((a.x - b.x) * (a.y - b.y))


def avoid_func(seg, avo_list):
    ''' 一条边与列表中所有边，在某个坐标方向上，坐标区域的重合关系'''
    n, a, l, r, m = 0, 0, 0, 0, 0
    s_range = cover_range(seg)
    lp, rp = None, None
    m_range = []

    for i in avo_list:
        ran = cover_range(i)
        if ran[0] <= s_range[0] and s_range[0] < ran[1] and ran[1] < s_range[1]:
            l += 1
            lp = ran[1]
        elif ran[0] > s_range[0] and ran[0] < s_range[1] and ran[1] >= s_range[1]:
            r += 1
            rp = ran[0]
        elif s_range[0] < ran[0] and s_range[1] > ran[1]:
            m += 1
            m_range.append(ran)
        elif s_range[0] >= ran[0] and s_range[1] <= ran[1]:
            a += 1
        else:
            n += 1
    return [n, a, l, r, m], [lp, rp, m_range]


def cut_line(a, b, l):
    ''' 一条线，沿线方向上两个位置顶点切割'''
    if l.p1.y == l.p2.y:
        # 水平线
        y = l.p1.y
        return DY_segment(Point2D(a, y), Point2D(b, y))

    else:
        x = l.p1.x
        return DY_segment(Point2D(x, a), Point2D(x, b))


def re_shape(a, c):
    '''对角线两个点，重构四边形'''
    if a.x < c.x:
        a, c = c, a
    if a.y > c.y:
        b = Point2D(a.x, c.y)
        d = Point2D(c.x, a.y)
    else:
        b = Point2D(c.x, a.y)
        d = Point2D(a.x, c.y)

    return [a, b, c, d]


def line_ext_max_final(l, praline, boundary, concave_list):
    inside_list = []
    a_dict = {}
    global vector, np_poi
    '''同侧化praline里面的规避边'''
    # 水平线
    vector = l.normal.p2[1]
    np_poi = l.p1.y
    x_rang = cover_range(l)
    for pl in praline:
        ai = pl.p1.y - l.p1.y
        aai = abs(ai)
        if ai / aai == l.normal.p2[1] and is_staggerd(pl, x_rang):
            if a_dict.get(aai) == None:
                a_dict[aai] = []
            a_dict[aai].append(pl)

    inside_list = [(x1, a_dict[x1]) for x1 in a_dict.keys()]
    inside_list.sort(key=lambda x: x[0])

    # d_list全局答案存放
    global d_list
    d_list = []

    def max_rec(tl, inside_list):
        in_list = inside_list.copy()
        try:
            il = in_list[0]
        except:
            raise Exception('矩形曼延处，曼延线没有平行且坐标区域重合的线，区域不闭合', tl.p1, tl.p2)
        tl_range = cover_range(tl)
        true_p = np_poi + vector * il[0]
        in_list.__delitem__(0)
        af, ap = avoid_func(tl, il[1])
        if af[1] or af[2] or af[3] or af[4]:
            s = il[0] * tl.seg.length
            d_list.append((s, cover_range(tl), np_poi, true_p))
        else:
            max_rec(tl, in_list)
        '''更新下波数据,tl要更新，如果要进入递归，则要转换相应参数并且结束这个for循环'''
        if not af[1]:
            # m的情况
            cp = [tl_range[0], tl_range[1]]
            m_range = ap[2]
            for mr in m_range:
                cp.append(mr[0])
                cp.append(mr[1])
            if af[2]:
                cp.append(ap[0])
                cp.sort()
                cp.__delitem__(0)
            if af[3]:
                cp.append(ap[1])
                cp.sort()
                cp.__delitem__(-1)
            cp.sort()
            l = len(cp)
            if l % 2 == 1:
                raise Exception('位于矩形曼延处代码，检查是否有凹陷的单点线，\
                                凹陷处应该为墙而不是单线段', a.p1, a.p2)

            l = int(l / 2)
            for i in range(l):
                tl = cut_line(cp[2 * i], cp[2 * i + 1], tl)
                max_rec(tl, in_list)

    max_rec(l, inside_list)

    d_list.sort(key=lambda x: x[0], reverse=True)
    max_s = d_list[0][0]
    x_rang = d_list[0][1]
    y_rang = (d_list[0][2], d_list[0][3])
    a = Point2D(x_rang[0], y_rang[0])
    c = Point2D(x_rang[1], y_rang[1])

    p_list = [a, c]

    return max_s, p_list


def largest_trangle_final(vex, ho_line, boundary, concave_list=[]):
    horizontal_line_list = [x for x in boundary.seg_list if x.horizontal == True]
    vertical_list = [x for x in boundary.seg_list if x.vertical == True]
    an_list = []
    f_ip = []
    ip = [ho_line.p1, ho_line.p2]
    for p in range(2):
        a, b = ip[p], ip[1 - p]
        ab = DY_segment(a, b)
        while b in concave_list:
            b_l = ray_ext(ab, vertical_list)
            b = b_l[1][1]
            t_dir_l = DY_segment(b, another_p(b_l[1][2], b))
            ab = DY_segment(a, b)

            if t_dir_l.dir.p2 == ho_line.normal.p2:
                break

        f_ip.append(b)
    a, b = f_ip[0], f_ip[1]
    p1, p2 = DY_segment.get_p1_p2_from_normal(ho_line.normal, a, b)
    l = DY_segment(p1, p2)
    s, p_list = line_ext_max_final(l, horizontal_line_list, boundary, concave_list)
    an_list.append((s, p_list))
    an_list.sort(key=lambda x: x[0], reverse=True)
    return an_list[0][0], an_list[0][1]


def get_virtual_boundary(boundary):
    '''新版本的虚拟边界提取函数'''
    concave_list, convex_list = concave_or_convex(boundary)
    a_list = []

    # x_vec_line = DY_segment(Point2D(0, 0), Point2D(1, 0))
    # horizontal_line_list = get_paralleled_line(x_vec_line, boundary, DY_segment)
    horizontal_line_list = [x for x in boundary.seg_list if x.horizontal == True]
    horizontal_line = [x for x in boundary.seg_list if (x.horizontal == True and x.normal.p2.y > 0)]

    for se in horizontal_line:
        vex = se.p1
        s, p_list = largest_trangle_final(vex, se, boundary, concave_list)
        a_list.append((s, p_list))
    a_list.sort(key=lambda x: x[0], reverse=True)
    p_list = re_shape(a_list[0][1][0], a_list[0][1][1])
    virtual_boundary = DY_boundary(*[p_list[0], p_list[1], p_list[2], p_list[3]])

    return virtual_boundary


def get_virtual_boundary_all_rec(boundary):
    '''新版本的虚拟边界提取函数'''
    concave_list, convex_list = concave_or_convex(boundary)
    a_list = []

    # x_vec_line = DY_segment(Point2D(0, 0), Point2D(1, 0))
    # horizontal_line_list = get_paralleled_line(x_vec_line, boundary, DY_segment)
    horizontal_line = [x for x in boundary.seg_list if x.horizontal == True]

    for se in horizontal_line:
        vex = se.p1
        s, p_list = largest_trangle_final(vex, se, boundary, concave_list)
        a_list.append((s, p_list))
    a_list.sort(key=lambda x: x[0], reverse=True)

    return a_list[0]


def get_vector_seg(ver, boundary):
    for i in boundary.seg_list:
        if i.p1 == ver:
            return i


def get_point_belong_seg(ver, boundary):
    seg_list = []
    for seg in boundary.seg_list:
        if seg.seg.contains(ver):
            seg_list.append(seg)
    return seg_list


def divide_rec(adj_pl, not_adjpl, boundary, virtual_boundary, v_b_list=[]):
    '''考虑到第二重深度，直接用第一层的vb, 暂不考虑多个v_b_list
    因为墙是有厚度的，暂时不认为会有单条向内凹的线，即不会有要分的区是以一条边隔开的
    '''

    def seg_contain(seg, poi_list):
        con_list = []
        for poi in poi_list:
            if seg.seg.contains(poi):
                con_list.append(poi)
        return con_list

    vb_point_l = virtual_boundary.polygon.vertices
    adj_pl.extend([x for x in vb_point_l if x not in adj_pl])
    roi_list = []
    while not_adjpl != []:
        sp = not_adjpl[0]
        not_adjpl.remove(sp)
        ver0, ver1 = sp, None
        vec_line = get_vector_seg(ver0, boundary)
        ver1 = vec_line.p2
        roi_p_list = [ver0]
        while ver1 != sp:

            '''应该是先得到所在的向量线，该线沿边界走到虚拟边区，交点会有几个情况，
                    1，没有交点，最正常的走法
                    2，垂直相交，直接走到，向量线p2赋给v1直接走到v1并考虑进入虚边走法
                    3，共线相交，
                        3.1考虑p2点跑到虚拟边界上,可能在虚边界刚好的某个顶点上
                        3.2 p2跑超过了虚拟边界
                    不会是p1点交虚边界，p1交就会是上个循环的p2交，p1,p2同时在虚拟边界上的跑法是错误的
            
                射线在虚边界延伸需要另一套走法
                    1，走到虚边界点，
                    2，走的虚边界垂直实际边界
                    3，共线
            '''

            judge_list = seg_contain(vec_line, adj_pl)
            if judge_list == []:
                # 更新下一轮
                ver0 = ver1
                vec_line = get_vector_seg(ver0, boundary)
                ver1 = vec_line.p2

            elif ver0 not in adj_pl:

                if len(judge_list) == 1:
                    # 所在虚边界的p1和该点重构一条线段
                    ver0 = judge_list[0]
                    t_vector_line_list = get_point_belong_seg(ver0, virtual_boundary)
                    if len(t_vector_line_list) == 1:
                        t_vector_line = t_vector_line_list[0]
                    else:
                        # 刚好在角点
                        for seg in t_vector_line_list:
                            if seg.cross_dir(vec_line) == 0:
                                continue
                            else:
                                t_vector_line = seg
                                break
                    ver1 = t_vector_line.p1
                    vec_line = DY_segment(ver0, ver1)

                elif len(judge_list) >= 2:
                    judge_list.sort(key=lambda x: point_distance(ver0, x))
                    ver0 = judge_list[0]
                    t = ver1
                    t_vector_line_list = get_adj_seg(ver0, virtual_boundary)
                    for seg in t_vector_line_list:
                        if seg.p2 == ver0:
                            ver1 = seg.p1
                    if t == ver1:
                        raise Exception('代码让图形走错路了')
                    vec_line = DY_segment(ver0, ver1)

                else:
                    raise Exception('理论不可能，线不会从虚拟区域中穿过去的，检查一级分区')
            elif ver0 in adj_pl:
                if len(judge_list) == 1:
                    ver0 = ver1
                    vec_line = get_vector_seg(ver0, boundary)
                    ver1 = vec_line.p2
                else:

                    judge_list.sort(key=lambda x: point_distance(ver0, x))
                    # 第一点肯定是ver0本身
                    ver1 = judge_list[1]
                    t_l = DY_segment(ver0, ver1)
                    '''t_p是出去射线源点外最近的点，他可能有很多情况，将他重构成一条射线，判断延伸点情况'''
                    t_vector_line_list = get_adj_seg(ver1, boundary)
                    if t_vector_line_list == []:
                        v_line_list = get_adj_seg(ver1, virtual_boundary)
                        for seg in v_line_list:
                            if seg.line.contains(ver0):
                                continue
                            else:
                                t_vector_line = seg
                                break
                        ver0 = ver1
                        if t_vector_line.p1 == ver1:
                            ver1 = t_vector_line.p2
                        else:
                            ver1 = t_vector_line.p1
                        vec_line = DY_segment(ver0, ver1)
                    elif len(t_vector_line_list) == 1:
                        ver0 = ver1
                        ver1 = t_vector_line_list[0].p2
                        vec_line = DY_segment(ver0, ver1)

                    elif len(t_vector_line_list) == 2:
                        for seg in t_vector_line_list:
                            if seg.cross_dir(t_l) == 0:
                                continue
                            else:
                                vec_line = seg
                                break
                        ver0 = ver1
                        ver1 = vec_line.p2
                        vec_line = DY_segment(ver0, ver1)
                    else:
                        raise Exception('一点不该对应超过两条线，线段错误')
            else:
                raise Exception('unknow')
            try:
                if ver0 in not_adjpl:
                    not_adjpl.remove(ver0)
            except:
                raise Exception('矩形分割处，出现该异常应为区域边界是否有隐含点未被删除')
            roi_p_list.append(ver0)
        bd = DY_boundary(*roi_p_list)
        roi_list.append(bd)
    return roi_list


def get_n_virtual_boundary(boundary, virtual_boundary_list=[], n=2):
    '''调用这个函数就会递归的调用函数本身，直到得到第n级别的提取矩形
        在设计函数实现时暂时未考虑第三重即以上递归调用时虚边界的影响，固现在默认n=2
    '''

    n_count = len(virtual_boundary_list)
    if n_count == 0:
        virtual_boundary = get_virtual_boundary(boundary)
        virtual_boundary_list.append(virtual_boundary)
    adj_point_list = []
    not_adj_point_list = []
    for seg in virtual_boundary.seg_list:
        for i in boundary.polygon.vertices:
            if seg.seg.contains(i) and i not in adj_point_list:
                adj_point_list.append(i)
    for i in boundary.polygon.vertices:
        if i not in adj_point_list:
            not_adj_point_list.append(i)

    # 调用分区函数
    roi_list = divide_rec(adj_point_list, not_adj_point_list, boundary, virtual_boundary, virtual_boundary_list)

    a_list = []
    for roi in roi_list:
        v_list = get_virtual_boundary_all_rec(roi)
        a_list.append(v_list)
    a_list.sort(key=lambda x: x[0], reverse=True)

    p_list = re_shape(a_list[n_count][1][0], a_list[n_count][1][1])

    virtual_boundary = DY_boundary(*[p_list[0], p_list[1], p_list[2], p_list[3]])
    virtual_boundary_list.append(virtual_boundary)

    n_count = len(virtual_boundary_list)
    if n_count >= n:
        # 退出递归-
        return virtual_boundary_list

        virtual_boundary_list = get_n_virtual_boundary(boundary, n, virtual_boundary_list)
        return virtual_boundary_list


def get_virtual_boundary_old(origin_boundary):
    inner_point = []
    xmin, ymin, xmax, ymax = origin_boundary.polygon.bounds
    xlen = xmax - xmin
    ylen = ymax - ymin
    for p in origin_boundary.polygon.vertices:
        if p.x != xmin and p.x != xmax and p.y != ymin and p.y != ymax:
            inner_point.append(p)
    verti = origin_boundary.polygon.vertices
    for v in verti:
        if (v in inner_point):
            verti.remove(v)
    # verti 外点，innerpoint内点
    maxabcd = 0
    maxspoint = verti[0]
    for v in verti:
        a = v
        adj_seg = get_adj_seg(v, origin_boundary)
        ab = adj_seg[0]
        ac = adj_seg[1]
        if ab.seg.p1.x != ab.seg.p2.x:
            tem = ac
            ac = ab
            ab = tem
        if ab.seg.p1 == a:
            b = ab.seg.p2
        else:
            b = ab.seg.p1
        if ac.seg.p1 == a:
            c = ac.seg.p2
        else:
            c = ac.seg.p1
        if b in inner_point:
            bm = ab.seg.length
            bb = b
            tl0 = get_paralleled_line(ac, origin_boundary, DY_segment)
            for t0 in tl0:
                if t0.line.distance(a) > bm and ab.line.intersection(t0.seg) != []:  # 待会注意下焦点问题
                    bb = ab.line.intersection(t0.seg)[0]
                    bm = t0.line.distance(a)
            b = bb
            ab = DY_segment(a, b)
        if c in inner_point:
            cm = ac.seg.length
            cc = c
            tl1 = get_paralleled_line(ab, origin_boundary, DY_segment)
            for t1 in tl1:
                if t1.line.distance(a) > cm and ac.line.intersection(t1.seg) != []:  # 待会注意下焦点问题
                    cc = ac.line.intersection(t1.seg)[0]
                    cm = t1.line.distance(a)
            c = cc
            ac = DY_segment(a, c)

        Sabcd = (ab.seg.length) * (ac.seg.length)
        if Sabcd > maxabcd:
            maxabcd = Sabcd
            A = a
            B = b
            C = c
            AB = DY_segment(A, B)
            AC = DY_segment(A, C)
        else:
            continue
    # 去掉把
    D = C + AB.dir.p2 * (AB.seg.length)
    for v in verti:
        if (v in inner_point):
            verti.remove(v)
    # verti 外点，innerpoint内点

    if is_inner_point(D, origin_boundary) == 0:
        # 不在边上
        yma = max(A.y, B.y, C.y, D.y)
        ymi = min(A.y, B.y, C.y, D.y)
        xma = max(A.x, B.x, C.x, D.x)
        xmi = min(A.x, B.x, C.x, D.x)
        dp = D
        smj = st = 0
        for vi in origin_boundary.polygon.vertices:
            if vi.x >= xmi and vi.x <= xma and vi.y >= ymi and vi.y <= yma:
                st = abs(vi.x - A.x) * abs(vi.y - A.y)
                if st > smj:
                    smj = st
                    dp = vi
                    # 得到阶梯最大值s 和点dp
        pb = B
        pc = C
        spb = spc = 0
        pdb = D
        pdc = D
        BD = DY_segment(B, D)
        CD = DY_segment(C, D)
        for s in origin_boundary.seg_list:
            if BD.seg.intersection(s.seg) != [] and s.line.is_parallel(AB.line):
                pb = s.seg.intersection(BD.seg)[0]
                if abs(pb.x - A.x) * abs(pb.y - A.y) > spb:
                    t1 = abs(pb.x - A.x)
                    t2 = abs(pb.y - A.y)
                    spb = abs(pb.x - A.x) * abs(pb.y - A.y)
                    pdb = pb
            if CD.seg.intersection(s.seg) != [] and s.line.is_parallel(AC.line):
                pc = s.seg.intersection(CD.seg)[0]
                if abs(pc.x - A.x) * abs(pc.y - A.y) > spc:
                    spc = abs(pc.x - A.x) * abs(pc.y - A.y)
                    pdc = pc
        if spb > spc:
            D = pdb
            C = A + AC.dir.p2 * (AB.seg.distance(D))
        else:
            D = pdc
            B = A + AB.dir.p2 * (AC.seg.distance(D))
        if smj < spb or smj < spc:
            pass
        else:
            D = dp
            B = Point2D(A.x, D.y)
            C = Point2D(D.x, A.y)

    AB = DY_segment(A, B)
    AC = DY_segment(A, C)
    BD = DY_segment(B, D)
    CD = DY_segment(C, D)
    yma = max(A.y, B.y, C.y, D.y)
    ymi = min(A.y, B.y, C.y, D.y)
    xma = max(A.x, B.x, C.x, D.x)
    xmi = min(A.x, B.x, C.x, D.x)

    inner_point_list = []
    for inp in inner_point:
        x = inp.x
        y = inp.y
        if x > xmi and x < xma and y > ymi and y < yma:
            inner_point_list.append(inp)
    for inp in inner_point_list:
        x = inp.x
        y = inp.y
        inner_list = []
        innerpo = prapo = inp
        horizontal_line = AC
        if x > xmi and x < xma and y > ymi and y < yma:
            inner_list = get_adj_seg(inp, origin_boundary)
            innum = 0
            len_inner_point_list = len(inner_point_list)
            for inline in inner_list:
                if (inline.seg.p1 in inner_point_list) and (inline.seg.p2 in inner_point_list):
                    innum += 1
                    vertical_line = inline
                    if inline.seg.p1 == inp:
                        innerpo = inline.seg.p2
                    else:
                        innerpo = inline.seg.p1
                    inner_point_list.remove(inline.seg.p1)
                    inner_point_list.remove(inline.seg.p2)

                else:
                    horizontal_line = inline
                    if inline.seg.p1 == inp:
                        innerpo = inline.seg.p2
                    else:
                        innerpo = inline.seg.p1
            if innum == 1:
                hvcomp0 = 0  # 指向CD边距
                hvcomp1 = 0  # 指向AB边距
                BD = DY_segment(B, D)
                CD = DY_segment(C, D)
                if AB.line.is_parallel(horizontal_line.line):
                    if AB.line.distance(inp) > AB.line.distance(innerpo):
                        if AB.line.distance(innerpo) > CD.line.distance(inp):
                            # 更新CD
                            hvcomp0 = 1
                            hvcomp1 = AB.line.distance(innerpo)
                        else:
                            # 更新AB
                            hvcomp0 = CD.line.distance(inp)
                            hvcomp1 = 1
                    else:
                        if AB.line.distance(inp) > CD.line.distance(innerpo):
                            # 更新CD
                            hvcomp0 = 1
                            hvcomp1 = AB.line.distance(inp)
                        else:
                            # 更新AB
                            hvcomp0 = CD.line.distance(innerpo)
                            hvcomp1 = 1
                    if len_inner_point_list == 2 or len_inner_point_list == 1:
                        # 等于1这里暂时存疑
                        if AC.line.distance(inp) > BD.line.distance(inp):
                            # 更新BD
                            dis = AC.line.distance(inp)
                            B = A + AB.dir.p2 * dis
                            D = C + AB.dir.p2 * dis
                        else:
                            dis = BD.line.distance(inp)
                            A = B - AB.dir.p2 * dis
                            C = D - AB.dir.p2 * dis
                    else:
                        if hvcomp0 == 1:
                            C = A + AC.dir.p2 * hvcomp1
                            D = B + AC.dir.p2 * hvcomp1
                        elif hvcomp1 == 1:
                            A = C - AC.dir.p2 * hvcomp0
                            B = D - AC.dir.p2 * hvcomp0
                elif AC.line.is_parallel(horizontal_line.line):
                    if AC.line.distance(inp) > AC.line.distance(innerpo):
                        if AC.line.distance(innerpo) > BD.line.distance(inp):
                            # 更新BD
                            hvcomp0 = 1
                            hvcomp1 = AC.line.distance(innerpo)
                        else:
                            # 更新AC
                            hvcomp0 = BD.line.distance(inp)
                            hvcomp1 = 1
                    else:
                        if AC.line.distance(inp) > BD.line.distance(innerpo):
                            # 更新BD
                            hvcomp0 = 1
                            hvcomp1 = AC.line.distance(inp)
                        else:
                            # 更新AC
                            hvcomp0 = BD.line.distance(innerpo)
                            hvcomp1 = 1
                    if len_inner_point_list == 2 or len_inner_point_list == 1:
                        if AB.line.distance(inp) > CD.line.distance(inp):
                            dis = AB.line.distance(inp)
                            C = A + AC.dir.p2 * dis
                            D = B + AC.dir.p2 * dis
                        else:
                            dis = CD.line.distance(inp)
                            A = C - AC.dir.p2 * dis
                            B = D - AC.dir.p2 * dis
                    else:
                        if hvcomp0 == 1:
                            B = A + AB.dir.p2 * hvcomp1
                            D = C + AB.dir.p2 * hvcomp1
                        elif hvcomp1 == 1:
                            A = B - AB.dir.p2 * hvcomp0
                            C = D - AB.dir.p2 * hvcomp0
                yma = max(A.y, B.y, C.y, D.y)
                ymi = min(A.y, B.y, C.y, D.y)
                xma = max(A.x, B.x, C.x, D.x)
                xmi = min(A.x, B.x, C.x, D.x)
            else:
                continue

    a, c = A, D
    t = B
    if c.x > a.x:
        if c.y > a.y:
            if t.x == a.x:
                b = t
                d = C
            else:
                d = t
                b = C
        else:
            if t.x > a.x:
                b = t
                d = C
            else:
                d = t
                b = C
    else:
        if c.y > a.y:
            if t.x < a.x:
                b = t
                d = C
            else:
                d = t
                b = C
        else:
            if t.x == a.x:
                b = t
                d = C
            else:
                d = t
                b = C

    virtual_boundary = DY_boundary(*[a, b, c, d])

    return virtual_boundary


def get_virtual_boundary_tmp_1(origin_boundary):
    '''寻点时缺少延伸。'''

    def get_adj_seg(ver):
        tp_adj_seg_list = []
        for seg in origin_boundary.seg_list:
            if seg.seg.contains(ver):
                tp_adj_seg_list.append(seg)
        return tp_adj_seg_list

    inner_point = []
    xmin, ymin, xmax, ymax = origin_boundary.polygon.bounds
    xlen = xmax - xmin
    ylen = ymax - ymin
    for p in origin_boundary.polygon.vertices:
        if p.x != xmin and p.x != xmax and p.y != ymin and p.y != ymax:
            inner_point.append(p)
    verti = origin_boundary.polygon.vertices
    for v in verti:
        if (v in inner_point):
            verti.remove(v)

    maxabcd = 0
    maxspoint = verti[0]
    for v in verti:
        adj_seg = get_adj_seg(v)
        Ab = adj_seg[0]
        Ac = adj_seg[1]
        Sabcd = (Ab.seg.length) * (Ac.seg.length)
        if Sabcd > maxabcd:
            maxabcd = Sabcd
            A = v
            AB = adj_seg[0]
            AC = adj_seg[1]
    if AB.seg.p1.x != AB.seg.p2.x:
        AB, AC = AC, AB

    if AB.seg.p1 == A:
        B = AB.seg.p2
    else:
        B = AB.seg.p1
    if AC.seg.p1 == A:
        C = AC.seg.p2
    else:
        C = AC.seg.p1

    if B in inner_point:
        bm = 0
        bb = B
        templist0 = get_paralleled_line(AC, origin_boundary)
        for tl in templist0:
            if tl.distance(A) > bm and AB.line.intersection(tl) != None:
                bm = tl.distance(A)
                bb = AB.line.intersection(tl)[0]
            B = bb

    if C in inner_point:
        cm = 0
        cc = C
        templist1 = get_paralleled_line(AB, origin_boundary)
        for tl in templist1:
            if tl.distance(A) > cm and AC.line.intersection(tl) != None:
                cm = tl.distance(A)
                cc = AC.line.intersection(tl)[0]
            C = cc
    AB = DY_segment(A, B)
    AC = DY_segment(A, C)
    D = C + AB.dir.p2 * (AB.seg.length)

    if is_inner_point(D, origin_boundary) == 0:
        outtag = 1
        for s in origin_boundary.seg_list:
            if s.seg.contains(D):
                outtag = 0
                seg_cont_d = s
                break
        if outtag:
            pb = B
            pc = C
            spb = spc = 0
            pdb = D
            pdc = D
            BD = DY_segment(B, D)
            CD = DY_segment(C, D)
            for s in origin_boundary.seg_list:
                if BD.seg.intersection(s.seg) != [] and s.line.is_parallel(AB.line):
                    pb = s.seg.intersection(BD.seg)[0]
                    if abs(pb.x - A.x) * abs(pb.y - A.y) > spb:
                        t1 = abs(pb.x - A.x)
                        t2 = abs(pb.y - A.y)
                        spb = abs(pb.x - A.x) * abs(pb.y - A.y)
                        pdb = pb
                if CD.seg.intersection(s.seg) != [] and s.line.is_parallel(AC.line):
                    pc = s.seg.intersection(CD.seg)[0]
                    if abs(pc.x - A.x) * abs(pc.y - A.y) > spc:
                        spc = abs(pc.x - A.x) * abs(pc.y - A.y)
                        pdc = pc
            if spb > spc:
                D = pdb
                C = A + AC.dir.p2 * (AB.seg.distance(D))
            else:
                D = pdc
                B = A + AB.dir.p2 * (AC.seg.distance(D))

        else:
            pass

    yma = max(A.y, B.y, C.y, D.y)
    ymi = min(A.y, B.y, C.y, D.y)
    xma = max(A.x, B.x, C.x, D.x)
    xmi = min(A.x, B.x, C.x, D.x)

    for inp in inner_point:
        x = inp.x
        y = inp.y
        if x > xmi and x < xma and y > ymi and y < yma:
            inner_list = []
            inner_list = get_adj_seg(inp)
            for inline in inner_list:
                if (inline.seg.p1 in inner_point) and (inline.seg.p2 in inner_point):
                    if AB.line.is_parallel(inline.line):
                        move_dis = AB.line.distance(inp)
                        C = A + AC.dir.p2 * move_dis
                        D = B + AC.dir.p2 * move_dis
                    elif AC.line.is_parallel(inline.line):
                        move_dis = AC.line.distance(inp)
                        B = A + AB.dir.p2 * move_dis
                        D = C + AB.dir.p2 * move_dis
                    inner_point.remove(inline.seg.p1)
                    inner_point.remove(inline.seg.p2)
    a, c = A, D
    t = B
    if c.x > a.x:
        if c.y > a.y:
            if t.x == a.x:
                b = t
                d = C
            else:
                d = t
                b = C
        else:
            if t.x > a.x:
                b = t
                d = C
            else:
                d = t
                b = C
    else:
        if c.y > a.y:
            if t.x < a.x:
                b = t
                d = C
            else:
                d = t
                b = C
        else:
            if t.x == a.x:
                b = t
                d = C
            else:
                d = t
                b = C

    virtual_boundary = DY_boundary(*[a, b, c, d])
    return virtual_boundary


def get_op_normal(nor):
    '''取相反向量'''
    p1 = nor.p1
    p2 = nor.p2
    p2 = Point2D(-p2.x, -p2.y)
    op_normal = Ray(p1, p2)
    return op_normal


def get_mother_boundary(seg, boundary):
    '''得到线段所属的边界'''
    k = None
    for s in boundary.seg_list:
        if s.line.contains(seg.p1) and s.line.contains(seg.p2):
            k = s
            break
    return k


def get_nearest_parallel_line(seg, boundary):
    para_line = get_paralleled_line(seg, boundary, DY_segment)
    li = None
    if para_line != []:
        pl = sorted(para_line, key=lambda x: x.line.distance(seg.p1))
        li = pl[0]
        return li
    else:
        return False


def the_same_edge(vd, vw):  # vir_door_list,vir_win_list
    '''虚墙表里面是含有墙和墙中点的列表,线都是DY_S'''
    t = 0
    b_door = None
    b_win = None
    for d in vd:
        for w in vw:
            if w.line.is_parallel(d[0].line) and w.line.contains(d[1]):
                t = 1
                b_door = d
                b_win = w
                break
    return t, b_door, b_win

    pass


def get_vir_door(dr, boundary):
    '''得到门在边上的投影'''
    p = []
    adj = get_adj_seg(dr.backline.p1, dr.boundary)
    adj1 = get_adj_seg(dr.backline.p2, dr.boundary)
    for i in adj:
        if i.seg == dr.backline.seg:
            continue
        else:
            p.append(i)
    for i in adj1:
        if i.seg == dr.backline.seg:
            continue
        else:
            p.append(i)
    if len(p) == 2:
        for v in boundary.seg_list:
            if v.seg.intersection(p[0].seg) != [] \
                    and v.seg.intersection(p[1].seg) != []:
                p1 = v.seg.intersection(p[0].seg)[0]
                p2 = v.seg.intersection(p[1].seg)[0]
                break
    else:
        return False
    dr_line = DY_segment(p1, p2)
    return dr_line


def get_vir_door_list(door_list, boundary):
    '''-------  将门列表所有门，调用了help中的门映射函数，把门映射到了门墙上两个点一条线段,------ '''
    vir_door_list = []
    for i in door_list:
        dr = get_vir_door(i, boundary)
        vir_door_list.append([dr, dr.seg.midpoint])
    return vir_door_list


def get_center(boundary):
    '''规则几何中心点'''
    n = len(boundary.polygon.vertices)
    x = sum(p.x for p in boundary.polygon.vertices) / n
    y = sum(p.y for p in boundary.polygon.vertices) / n
    return Point2D(x, y)


def best_fit(alist, wanted):
    '''能放多大放多大的配适函数'''
    n = len(alist) - 1
    for i in range(n + 1):
        if alist[n - i] <= wanted:
            wanted = alist[n - i]
            break
    if wanted >= alist[0]:
        return wanted
    else:
        return alist[0]


def is_inner_point(p, boundary):
    # 判断点是否在类似矩形的边界的图形内，在边界上返回 2 在界内返回 1 在界外返回 0
    m_len = 100000
    mm_len = -10000
    plist = [Segment2D(p, Point2D(p.x, mm_len)), Segment2D(p, Point2D(p.x, m_len)), \
             Segment2D(p, Point2D(p.y, mm_len)), Segment2D(p, Point2D(p.y, m_len))]
    ptag = [0, 0, 0, 0]
    for s in boundary.seg_list:
        if s.seg.contains(p):
            return 2  # 在边界上
        for i in range(4):
            if s.seg.intersection(plist[i]) != []:
                ptag[i] += 1
    for item in ptag:
        if item == 0 or item % 2 == 0:
            return 0
    return 1


def get_inner_point(boundary):
    ''' 点列表 和边界 ，返回矩形区域内的内点'''
    inner_point = []
    xmin, ymin, xmax, ymax = boundary.polygon.bounds
    xlen = xmax - xmin
    ylen = ymax - ymin
    for p in boundary.polygon.vertices:
        if p.x != xmin and p.x != xmax and p.y != ymin and p.y != ymax:
            inner_point.append(p)
    return inner_point


def point_distance(p1, p2):
    a = numpy.square(p1.x - p2.x) + numpy.square(p1.y - p2.y)
    a = math.sqrt(a)
    return a


def get_points_seg_intersect_boundary(seg, boundary, type=Line):
    """边界与某条线相交的所有点(去除线段）"""
    l = type(seg.p1, seg.p2)
    inter_pt = boundary.polygon.intersection(l)
    inter_pt = [pt for pt in inter_pt if isinstance(pt, Point2D)]
    return inter_pt


def get_points_seg_intersect_boundary_all(seg, boundary, type=Line):
    """边界与某条线相交的所有点(包含线段上的点）"""
    inter_pt_new = []
    xmin, ymin, xmax, ymax = boundary.polygon.bounds
    xlen = xmax - xmin
    ylen = ymax - ymin
    v = boundary.polygon.vertices
    l = type(seg.p1, seg.p2)
    inter_pt = boundary.polygon.intersection(l)
    if len(inter_pt):
        for in_pt in inter_pt:
            if isinstance(in_pt, Segment2D):
                inter_pt_new.append(in_pt.p1)
                inter_pt_new.append(in_pt.p2)
            elif isinstance(in_pt, Point2D):
                inter_pt_new.append(in_pt)
        for pt in inter_pt_new:
            if not seg.seg.contains(pt) and pt.x in [xmin, xmax] or pt.y in [ymin, ymax]:
                if pt in v:
                    return pt, True
                else:
                    return pt, False
                    # return inter_pt_new
    else:
        return None


def get_intersect_line_from_boundary_without_cover(seg, boundary):
    ''' 返回与seg有交点的所有边界'''
    '''不要线段版，不可以重合'''
    intersect_line_list = []
    for l in boundary.seg_list:
        if l.seg.intersection(seg.seg) != []:
            k = l.seg.intersection(seg.seg)
            for i in k:  # 如果要线段，去除这边
                if isinstance(i, Segment2D):
                    break
                else:
                    intersect_line_list.append(l)
    return intersect_line_list


def get_intersect_line_from_boundary(seg, boundary):
    ''' 返回与seg有交点的所有边界'''
    intersect_line_list = []
    for l in boundary.seg_list:
        if l.seg.intersection(seg.seg) != []:
            intersect_line_list.append(l)
    return intersect_line_list


def get_adj_seg(ver, boundary):
    '''返回同一点的相邻边'''
    tp_adj_seg_list = []
    for seg in boundary.seg_list:
        if seg.seg.contains(ver):
            tp_adj_seg_list.append(seg)
    return tp_adj_seg_list


def another_p(line, point):
    '''返回一条边的另一个顶点'''
    if line.p1 == point:
        return line.p2
    else:
        return line.p1


def get_eles(ele_list, instance):
    """得到相应的element list"""
    targets = []
    for e in ele_list:
        if isinstance(e, instance):
            targets.append(e)
    return targets


def get_min_dis_seg_boundary(seg, boundary):
    """得到给定segment到boundary的最小距离，只计算bounary中与seg平行的线段"""
    para_line = get_paralleled_line(seg, boundary)
    dis = [l.distance(seg.p1) for l in para_line]
    return min(dis)


def get_paralleled_line(seg, boundary, type=Line):
    """得到与给定DY_segment平行的线段"""
    l_list = []
    for s in boundary.seg_list:
        if seg.line.is_parallel(s.line):
            l_list.append(type(s.p1, s.p2))
    return l_list


def get_ele_vertices_on_seg(ele, seg):
    """return组件在segment上的所有顶点"""
    vlist = []
    for v in ele.boundary.polygon.vertices:
        if seg.seg.contains(v):
            vlist.append(v)
    return vlist


def get_new_backline_with_bound(seg, bound):
    """通过boundary更新segment两点的顺序，使得seg一定沿着bound上的线段，以防反向"""
    v = bound.polygon.vertices
    assert seg.p1 in v, "backline端点不在边界上"
    assert seg.p2 in v, "backline端点不在边界上"

    for bs in bound.seg_list:
        if bs.seg.contains(seg.p1) and bs.seg.contains(seg.p2):
            if seg.normal.equals(bs.normal):
                return seg
            else:
                new_seg = DY_segment(seg.p2, seg.p1)
                return new_seg


def get_opposite_bounds(seg, boundary):
    op_list = []
    for s in boundary.seg_list:
        if seg.line.is_parallel(s.line) and seg.normal.p2.equals(s.normal.p2 * (-1)):
            op_list.append(s)
    return op_list


def get_adjacent_bounds(seg, boundary):
    adj_list = []
    for s in boundary.seg_list:
        if s.seg != seg.seg:
            if s.seg.contains(seg.p1) or s.seg.contains(seg.p2):
                adj_list.append(s)
    return adj_list


def get_adjacent_bounds_all(seg, boundary):
    adj_list = []
    for s in boundary.seg_list:
        if seg.line.is_perpendicular(s.line):
            adj_list.append(s)
    return adj_list


def get_out_door_name(in_door_name, door):
    for n in door.connect_list:
        if in_door_name is not n:
            out_door_name = n
    return out_door_name


def save_house_to_xml(house, file_name):
    root = etree.Element("XML")
    child = etree.SubElement(root, "House")
    child.set("name", house.name)
    for f in house.floor_list:
        child0 = etree.SubElement(child, "FloorPlan")
        child0.set("boundary", f.boundary.to_string())
        child0.set("name", f.name)
        for reg in f.region_list:
            child1 = etree.SubElement(child0, reg.__class__.__name__)
            child1.set("name", reg.name)
            child1.set("boundary", reg.boundary.to_string())
            child_temp = etree.SubElement(child1, 'Floor')
            child_temp.set("ID", str(reg.floor_id))
            child_temp = etree.SubElement(child1, 'SkirtingLine')
            child_temp.set("ID", str(reg.skirting_line_id))
            child_temp = etree.SubElement(child1, 'PlasterLine')
            child_temp.set("ID", str(reg.plaster_line_id))
            # child1_sub = etree.SubElement(child1, 'a')
            # child1_sub.text = ''
            for e in reg.ele_list:
                child2 = etree.SubElement(child1, e.__class__.__name__)
                child2.set("name", e.name)
                child2.set("boundary", e.boundary.to_string())
                child2.set("backline", e.backline.to_string())
                # child2.set("position", str(e.backline.p1).split('D')[1])
                child2.set("position", e.get_xyz_str())
                child2.set("angle", str(e.angle))
                child2.set("ID", str(e.ID))
                child2.set("back_len", str(int(e.backline.seg.length)))
                child2.set("front_len", str(int(e.len)))

                if e.__class__.__name__ == 'Door':
                    if e.door_body is not None:
                        child2.set("body", e.door_body.to_string())
                        child2.set("front_len", str(int(e.door_body.seg.length)))

                if e.is_multiple:
                    for ee in e.ele_list:
                        child3 = etree.SubElement(child2, ee.__class__.__name__)
                        child3.set("name", ee.name)
                        child3.set("boundary", ee.boundary.to_string())
                        child3.set("backline", ee.backline.to_string())
                        child3.set("position", ee.get_xyz_str())
                        # child3.set("position", str(ee.backline.p1).split('D')[1])
                        child3.set("angle", str(ee.angle))
            for l in reg.line_list:
                child2 = etree.SubElement(child1, l.__class__.__name__)
                child2.set("name", l.name)
                # child2.set("line", l.to_string())
                if hasattr(l, "boundary"):
                    child2.set("boundary", l.boundary.to_string())
                else:
                    child2.set("line", l.to_string())
                    child2.set("ID", str(l.ID))

    tree = etree.ElementTree(root)
    tree.write(file_name, pretty_print=True, xml_declaration=True, encoding='utf-8')
    return True


def is_boundary_intersection(b1, b2):
    """判断两个boundary是否相交，？"""
    vlist = b1.boundary.polygon.vertices

    for v in vlist:
        if b2.boundary.polygon.encloses_point(v):
            return True
    return False


def xml_set_boundary(key, region, node):
    """ 读取边界 """
    if key == DY_boundary.name:
        p_str_list = node.get(key).split(';')
        p_list = []
        for p_str in p_str_list:
            if p_str == '':
                continue
            list0 = p_str[1:-1].split(',')
            poi = Point(int(list0[0]), int(list0[1]))
            p_list.append(poi)
        eval_str = 'DY_boundary('
        for p in p_list:
            if p != p_list[-1]:
                eval_str += str(p) + ','
            else:
                eval_str += str(p)
        eval_str += ')'
        boundary = eval(eval_str)
        region.set_boundary(boundary)
    else:
        pass


def xml_get_boundary(key, node):
    """ 读取边界 """
    if key == DY_boundary.name:
        p_str_list = node.get(key).split(';')
        p_list = []
        for p_str in p_str_list:
            if p_str == '':
                continue
            list0 = p_str[1:-1].split(',')
            poi = Point(int(list0[0]), int(list0[1]))
            p_list.append(poi)
        eval_str = 'DY_boundary('
        for p in p_list:
            if p != p_list[-1]:
                eval_str += str(p) + ','
            else:
                eval_str += str(p)
        eval_str += ')'
        boundary = eval(eval_str)
        return boundary
    else:
        return None


def xml_set_window(region, node):
    boundary = xml_get_boundary("boundary", node)
    coincide_seg = boundary.polygon.intersection(region.boundary.polygon)
    coincide_seg = [seg for seg in coincide_seg if isinstance(seg, Segment2D)]

    for seg in coincide_seg:
        window = AutoLayout.DY_Line.Window(seg.p1, seg.p2)
        window.set_boundary(boundary)
        region.add_window(window)


def xml_set_border(key, region, node):
    p_str_list = node.get(key).split(';')
    p_list = []
    for p_str in p_str_list:
        list0 = p_str[1:-1].split(',')
        poi = Point(int(list0[0]), int(list0[1]))
        p_list.append(poi)
    eval_str = 'DY_Line.Border('
    for p in p_list:
        if p != p_list[-1]:
            eval_str += str(p) + ','
        else:
            eval_str += str(p)
    eval_str += ')'
    bord = eval(eval_str)
    region.add_border(bord)


def xml_set_backline(key, ele, node):
    if key == "backline":
        p_str_list = node.get(key).split(';')
        p_list = []
        for p_str in p_str_list:
            list0 = p_str[1:-1].split(',')
            poi = Point(int(list0[0]), int(list0[1]))
            p_list.append(poi)

        assert len(p_list) == 2, "backline 只能有两个点"
        backline = DY_segment(p_list[0], p_list[1])
        ele.set_backline(backline)
    else:
        pass


def xml_get_backline(key, node):
    if key == "backline":
        p_str_list = node.get(key).split(';')
        p_list = []
        for p_str in p_str_list:
            list0 = p_str[1:-1].split(',')
            poi = Point(int(list0[0]), int(list0[1]))
            p_list.append(poi)

        assert len(p_list) == 2, "backline 只能有两个点"
        backline = DY_segment(p_list[0], p_list[1])
        return backline
    else:
        pass


def xml_set_door_body(key, door, node):
    if key == "body" and node.get(key) != None:
        p_str_list = node.get(key).split(';')
        p_list = []
        for p_str in p_str_list:
            list0 = p_str[1:-1].split(',')
            poi = Point(int(list0[0]), int(list0[1]))
            p_list.append(poi)

        assert len(p_list) == 2, "body 只能有两个点"
        body = DY_segment(p_list[0], p_list[1])
        door.set_body(body)
    else:
        pass


def xml_set_door(door, node):
    att = 'attribute'
    # if node.get(att) is None:
    #     door.set_type(settings.DOOR_TYPE[0])
    # else:
    #     if node.get(att) == settings.DOOR_TYPE[0]:
    #         door.set_type(settings.DOOR_TYPE[0])
    #     elif node.get(att) == settings.DOOR_TYPE[1]:
    #         door.set_type(settings.DOOR_TYPE[1])
    #     elif node.get(att) == settings.DOOR_TYPE[2]:
    #         door.set_type(settings.DOOR_TYPE[2])
    #
    # if node.get(att) != settings.DOOR_TYPE[2]:
    #     xml_set_boundary("boundary", door, node)
    #     xml_set_door_body("body", door, node)
    # xml_set_backline("backline", door, node)

    if node.get(att) is None:
        door.set_type(AutoLayout.settings.DOOR_TYPE[0])
    xml_set_boundary("boundary", door, node)
    xml_set_door_body("body", door, node)
    xml_set_backline("backline", door, node)


import os


def listfile(dirname, postfix=''):
    filelist = []
    files = os.listdir(dirname)
    dirname = dirname + '/'
    for item in files:
        # filelist.append([dirname,item])
        if os.path.isfile(dirname + item):
            if item.endswith(postfix):
                filelist.append(item)
        else:
            if os.path.isdir(dirname + item):
                pass
                # filelist.extend(listfile(dirname+item+'/',postfix))
    return filelist


def error_log(log, time_str):
    error_log_check()

    xml = etree.parse('error.xml')
    root = xml.getroot()
    error_str = str(log).split(':')
    if error_str[0] == 'error' or error_str[0] == 'warning':
        child = etree.SubElement(root, error_str[0])
        child.set("time", time_str)
        child.text = error_str[1]
    else:
        child = etree.SubElement(root, "error")
        child.set("time", time_str)
        child.text = str(log)

    tree = etree.ElementTree(root)
    tree.write('error.xml', pretty_print=True, xml_declaration=True, encoding='utf-8')


def get_error_replica(fname, time_str):
    if os.path.exists('error_xml') is False:
        os.mkdir('error_xml')
    src = fname
    dst = 'error_xml//' + os.path.basename(fname)[:-4] + '_' + time_str + '.xml'
    shutil.copy(src, dst)


def error_log_check():
    error_file = 'error.xml'
    if os.path.exists(error_file):
        os.remove(error_file)
    root = etree.Element('ERRORANDWARNING')
    tree = etree.ElementTree(root)
    tree.write(error_file, pretty_print=True, xml_declaration=True, encoding='utf-8')
