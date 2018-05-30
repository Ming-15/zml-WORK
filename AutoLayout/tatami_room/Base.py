# _*_ coding:utf-8 _*_
from AutoLayout.BaseModual import *
from AutoLayout.BaseClass import *
from AutoLayout.livingroom.Element import *
from AutoLayout.settings import *
from AutoLayout.tatami_room.settings import *
from AutoLayout.tatami_room.Element import *
import AutoLayout.CommonElement as CommonElement
import random
import AutoLayout.tatami_room.utility as ttm_uti
import math
import numpy as np
import pandas as pd
from AutoLayout.helpers import *
import AutoLayout.DY_Line as DY_Line

class TatamiRoom(Region):
    def __init__(self):
        super(TatamiRoom,self).__init__()
        self.main_win_wall = None
        self.__init()

    def run(self):
        arrangement_dict = {
            (4,1,1) : self.run411 #顶点，门，窗
        }
        key = (len(self.boundary.polygon.vertices),self.doors,self.windows)

        if not arrangement_dict.get(key,False):
            raise Exception("榻榻米屋暂时不支持这种户型")

        res = arrangement_dict.get(key)()

    def run411(self):
        (xmin,ymin,xmax,ymax) = self.boundary.polygon.bounds
        xlen = xmax - xmin
        ylen = ymax - ymin
        if xlen > TATAMI_M_MAX or xlen < TATAMI_M_MIN or \
            ylen > TATAMI_M_MAX or ylen < TATAMI_M_MIN:
            raise Exception("warning:此功能区作为榻榻米长度不满足")
        if abs(self.boundary.polygon.area) < TATAMI_M_MIN * TATAMI_M_MIN:
            raise Exception("warning:此功能区作为榻榻米面积不足")
        #放置窗帘并获取窗户对面以及相邻的墙
        self.win_list, self.main_curtain, self.main_win_wall = \
            ttm_uti.arrange_tatami_main_curtain(self.line_list, self.ele_list)

        door = get_eles(self.ele_list, CommonElement.Door)[0]
        door_center = door.backline.seg.midpoint
        d_m = 0
        d_s = 0
        for s in self.boundary.seg_list:
            if s.seg.contains(door.backline.seg):
               door_wall = s
               adj_walls = get_adjacent_bounds(s, self.boundary)
               d_m = s.seg.length
               d_s = adj_walls[0].seg.length
               if adj_walls[0].line.distance(door_center) < adj_walls[1].line.distance(door_center):
                   near_door_wall = adj_walls[0]
                   far_door_wall =  adj_walls[1]
               else:
                   near_door_wall = adj_walls[1]
                   far_door_wall = adj_walls[0]
        # 判断门窗相对位置然后摆放组件
        for l in self.line_list:
            if isinstance(l, DY_Line.Window):

                # 门和窗户对立面
                # if l.normal.is_parallel(door.backline.normal) and l.line.distance(door_center)!= 0:
                if l.normal.is_parallel(door.backline.normal) and \
                                len(door.boundary.polygon.intersection(l.wall.line)) == 0:
                    nearst_df1 = self.df1.loc[self.df1.sum_len_m <= d_m]
                    nearst_df1 = nearst_df1.ix[nearst_df1.sum_len_m.idxmax]
                    nearst_df2 = self.df2.loc[self.df2.sum_len_s <= d_s]
                    nearst_df2 = nearst_df2.ix[nearst_df2.sum_len_s.idxmax]

                    p_far_door =  l.wall.line.intersection(far_door_wall.seg)[0] + \
                                 far_door_wall.normal.p2 * CUSTOM_BOOKCASE_LENGTH
                    p_near_door = l.wall.line.intersection(near_door_wall.seg)[0] + \
                                 near_door_wall.normal.p2 * CUSTOM_CLOSET_LENGTH
                    bookcase_num,closet_num= self.modify_true_num(d_m,d_s,1)
                    nearst_df1['closet_num'] = closet_num
                    nearst_df1['bookcase_num'] = bookcase_num
                    if l.seg.contains(p_near_door) and not l.seg.contains(p_far_door ):
                       nearst_df1['closet_num'] = 0
                       nearst_df1['tbed_wid'] = l.wall.seg.length - CUSTOM_BOOKCASE_LENGTH * nearst_df1['bookcase_num']
                    elif l.seg.contains(p_far_door) and not l.seg.contains(p_near_door):
                       nearst_df1['bookcase_num'] = 0
                       nearst_df1['tbed_wid'] = l.wall.seg.length - CUSTOM_CLOSET_LENGTH * nearst_df1['closet_num']
                    elif l.seg.contains(p_near_door) and  l.seg.contains(p_far_door):
                       nearst_df1['bookcase_num'] = 0
                       nearst_df1['closet_num'] = 0
                       nearst_df1['tbed_wid'] = l.wall.seg.length
                    else:
                       nearst_df1['tbed_wid'] = l.wall.seg.length - CUSTOM_BOOKCASE_LENGTH * nearst_df1['bookcase_num'] \
                                                - CUSTOM_CLOSET_LENGTH * nearst_df1['closet_num']

                   #放置榻榻米/衣柜/书柜
                    p1 = l.wall.line.intersection(near_door_wall.seg)[0]
                    p2 = p1 + l.wall.normal.p2 * nearst_df1['closet_num'] * nearst_df2['tbed_len']
                    p11 = p1 + near_door_wall.normal.p2 * nearst_df1['closet_num'] * CUSTOM_CLOSET_LENGTH
                    p22 = p11 + near_door_wall.normal.p2 * nearst_df1['tbed_wid']
                    p111 = p22 + near_door_wall.normal.p2 * nearst_df1['bookcase_num'] * CUSTOM_BOOKCASE_LENGTH
                    p222 = p111 + l.wall.normal.p2 * nearst_df2['tbed_len']
                    p_desk1 = p222
                    p_desk2 = p_desk1 + l.wall.normal.p2 * (far_door_wall.seg.length - nearst_df2['tbed_len'])
                    if nearst_df1['closet_num']:
                       p1,p2 = DY_segment.get_p1_p2_from_normal(near_door_wall.normal,p1,p2)
                       closet_bl = DY_segment(p1,p2)
                       clo = CommonElement.Closet(closet_bl)
                       self.ele_list.append(clo)
                    p11 ,p22 = DY_segment.get_p1_p2_from_normal(l.wall.normal,p11,p22)
                    tbed_bl = DY_segment(p11,p22)
                    mibed = get_mibed_type(self)
                    mibed.set_pos(tbed_bl,nearst_df2['tbed_len'])
                    self.ele_list.append(mibed)
                    if nearst_df1['bookcase_num']:
                       p111,p222 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal,p111,p222)
                       bookcase_bl = DY_segment(p111,p222)
                       bookcase = BookCase(bookcase_bl)
                       self.ele_list.append(bookcase)
                   #放置写字桌套件
                    p_desk1,p_desk2 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal,p_desk1,p_desk2)
                    desk_com_bl = DY_segment(p_desk1,p_desk2)
                    desk_com = CommonElement.WritingDeskAndChair(desk_com_bl)
                    self.ele_list.append(desk_com)
                   #门和窗户在同一个墙上
                elif l.normal.is_parallel(door.backline.normal) and \
                                len(door.boundary.polygon.intersection(l.wall.line)) != 0:
                    nearst_df1 = self.df1.loc[self.df1.sum_len_m <= d_s]
                    nearst_df1 = nearst_df1.ix[nearst_df1.sum_len_m.idxmax]
                    nearst_df2 = self.df2.loc[self.df2.sum_len_s <= d_m]
                    nearst_df2 = nearst_df2.ix[nearst_df2.sum_len_s.idxmax]
                    # 放置榻榻米/衣柜
                    op_wall = get_opposite_bounds(l.wall,self.boundary)[0]
                    p1 = op_wall.line.intersection(far_door_wall.seg)[0]
                    p2 = p1 + far_door_wall.normal.p2 * nearst_df2['tbed_len']
                    p_desk1 = p2
                    p_desk2 = p_desk1 + far_door_wall.normal.p2 * (op_wall.seg.length - nearst_df2['tbed_len'])
                    p11 = p1 - l.wall.normal.p2 * nearst_df1['closet_num'] * CUSTOM_CLOSET_LENGTH
                    p22 = p11 - l.wall.normal.p2 * (far_door_wall.seg.length - CUSTOM_CLOSET_LENGTH)
                    p1, p2 = DY_segment.get_p1_p2_from_normal(op_wall.normal, p1, p2)
                    closet_bl = DY_segment(p1, p2)
                    clo = CommonElement.Closet(closet_bl)
                    self.ele_list.append(clo)
                    p11, p22 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal, p11, p22)
                    tbed_bl = DY_segment(p11, p22)
                    mibed = get_mibed_type(self)
                    mibed.set_pos(tbed_bl, nearst_df2['tbed_len'])
                    self.ele_list.append(mibed)
                    # 放置写字桌套件
                    p_desk1, p_desk2 = DY_segment.get_p1_p2_from_normal(op_wall.normal, p_desk1, p_desk2)
                    desk_com_bl = DY_segment(p_desk1, p_desk2)
                    desk_com = CommonElement.WritingDeskAndChair(desk_com_bl)
                    self.ele_list.append(desk_com)
                    #门和窗户为邻墙但在远离门的墙上
                elif l.normal.is_perpendicular(door.backline.normal) and far_door_wall.seg.contains(l.seg):
                    op_wall = get_opposite_bounds(door_wall, self.boundary)[0]
                    p_op_door = l.wall.line.intersection(op_wall.seg)[0] + \
                                 op_wall.normal.p2 * CUSTOM_CLOSET_LENGTH
                    p_door = l.wall.line.intersection(door_wall.seg)[0] - \
                                  door_wall.normal.p2 * CUSTOM_BOOKCASE_LENGTH

                    nearst_df1 = self.df1.loc[self.df1.sum_len_m <= d_s]
                    nearst_df1 = nearst_df1.ix[nearst_df1.sum_len_m.idxmax]
                    nearst_df2 = self.df2.loc[self.df2.sum_len_s <= d_m]
                    nearst_df2 = nearst_df2.ix[nearst_df2.sum_len_s.idxmax]
                    bookcase_num, closet_num = self.modify_true_num(d_m, d_s, 0)
                    nearst_df1['closet_num'] = closet_num
                    nearst_df1['bookcase_num'] = bookcase_num
                    #判断是否档窗户
                    if l.seg.contains(p_op_door) and not l.seg.contains(p_door):
                        nearst_df1['closet_num'] = 0
                        nearst_df1['tbed_wid'] = l.wall.seg.length - CUSTOM_BOOKCASE_LENGTH
                    elif l.seg.contains(p_door) and not l.seg.contains(p_op_door):
                        nearst_df1['bookcase_num'] = 0
                        nearst_df1['tbed_wid'] = l.wall.seg.length - CUSTOM_CLOSET_LENGTH
                    elif l.seg.contains(p_door) and l.seg.contains(p_op_door):
                        nearst_df1['bookcase_num'] = 0
                        nearst_df1['closet_num'] = 0
                        nearst_df1['tbed_wid'] = l.wall.seg.length
                    else:
                       nearst_df1['tbed_wid'] = l.wall.seg.length - CUSTOM_BOOKCASE_LENGTH * nearst_df1['bookcase_num'] \
                                                - CUSTOM_CLOSET_LENGTH * nearst_df1['closet_num']

                    # 放置榻榻米/衣柜/书柜
                    p1 = op_wall.line.intersection(far_door_wall.seg)[0]
                    p2 = p1 + far_door_wall.normal.p2 * nearst_df2['tbed_len']
                    p_desk1 = p2
                    p_desk2 = p_desk1 + far_door_wall.normal.p2 * (op_wall.seg.length - nearst_df2['tbed_len'])
                    p11 = p1 + op_wall.normal.p2 * nearst_df1['closet_num'] * CUSTOM_CLOSET_LENGTH
                    p22 = p11 + op_wall.normal.p2 * nearst_df1['tbed_wid']
                    p111 = door_wall.line.intersection(far_door_wall.seg)[0]
                    p222 = p111 + far_door_wall.normal.p2 * nearst_df2['tbed_len']
                    if nearst_df1['closet_num']:
                        p1, p2 = DY_segment.get_p1_p2_from_normal(op_wall.normal, p1, p2)
                        closet_bl = DY_segment(p1, p2)
                        clo = CommonElement.Closet(closet_bl)
                        self.ele_list.append(clo)
                    p11, p22 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal, p11, p22)
                    tbed_bl = DY_segment(p11, p22)
                    mibed = get_mibed_type(self)
                    mibed.set_pos(tbed_bl, nearst_df2['tbed_len'])
                    self.ele_list.append(mibed)
                    if nearst_df1['bookcase_num']:
                        p111, p222 = DY_segment.get_p1_p2_from_normal(door_wall.normal, p111, p222)
                        bookcase_bl = DY_segment(p111, p222)
                        bookcase = BookCase(bookcase_bl)
                        self.ele_list.append(bookcase)
                    # 放置写字桌套件
                    p_desk1, p_desk2 = DY_segment.get_p1_p2_from_normal(op_wall.normal, p_desk1, p_desk2)
                    desk_com_bl = DY_segment(p_desk1, p_desk2)
                    desk_com = CommonElement.WritingDeskAndChair(desk_com_bl)
                    self.ele_list.append(desk_com)
                    # 门和窗户为邻墙但在近邻门的墙上
                elif l.normal.is_perpendicular(door.backline.normal) and near_door_wall.seg.contains(l.seg):
                    nearst_df1 = self.df1.loc[self.df1.sum_len_m <= d_m]
                    nearst_df1 = nearst_df1.ix[nearst_df1.sum_len_m.idxmax]
                    nearst_df2 = self.df2.loc[self.df2.sum_len_s <= d_s]
                    nearst_df2 = nearst_df2.ix[nearst_df2.sum_len_s.idxmax]
                    op_wall = get_opposite_bounds(door_wall, self.boundary)[0]
                    p1 = op_wall.line.intersection(near_door_wall.seg)[0]
                    p2 = p1 + near_door_wall.normal.p2 * (op_wall.seg.length - CUSTOM_CLOSET_LENGTH)
                    p11 = p2 + near_door_wall.normal.p2 * CUSTOM_CLOSET_LENGTH
                    p22 = p11 + op_wall.normal.p2 * nearst_df2['tbed_len']
                    p_desk1 = p22
                    p_desk2 = p_desk1 + op_wall.normal.p2 * (far_door_wall.seg.length - nearst_df2['tbed_len'])
                    #放床
                    p1, p2 = DY_segment.get_p1_p2_from_normal(op_wall.normal, p1, p2)
                    tbed_bl = DY_segment(p1, p2)
                    mibed = get_mibed_type(self)
                    mibed.set_pos(tbed_bl, nearst_df2['tbed_len'])
                    self.ele_list.append(mibed)
                    #放衣柜
                    p11, p22 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal, p11, p22)
                    closet_bl = DY_segment(p11, p22)
                    clo = CommonElement.Closet(closet_bl)
                    self.ele_list.append(clo)
                    # 放置写字桌套件
                    p_desk1, p_desk2 = DY_segment.get_p1_p2_from_normal(far_door_wall.normal, p_desk1, p_desk2)
                    desk_com_bl = DY_segment(p_desk1, p_desk2)
                    desk_com = CommonElement.WritingDeskAndChair(desk_com_bl)
                    self.ele_list.append(desk_com)
    def __init(self):
        sum1_length_lst = []
        sum2_length_lst = []
        closet_num_lst = []
        bookcase_num_lst = []
        tbed_wid_lst = []
        tbed_len_lst = []
        writedesk_wid_lst = []
        for bed_len in TATAMI_BED_LENGTH:
            if TATAMI_S_MIN - bed_len <= S_THREASHOLD:
               sum2_len =  0
               writedesk_wid = 0
               tbed_len = 0
               sum2_length_lst.append(sum2_len)
               writedesk_wid_lst.append(writedesk_wid)
               tbed_len_lst.append(tbed_len)
            else:
                sum2_len = bed_len
                writedesk_wid = 0
                tbed_len = bed_len
                sum2_length_lst.append(sum2_len)
                writedesk_wid_lst.append(writedesk_wid)
                tbed_len_lst.append(tbed_len)
        for thr in W_THREASHOLD_DICT:
            if thr == W_THREASHOLD1:
                closet_num = 0
                bookcase_num = 0
                tbed_wid = W_THREASHOLD1
                sum1_len = W_THREASHOLD1 + CUSTOM_CLOSET_LENGTH * closet_num + CUSTOM_BOOKCASE_LENGTH * bookcase_num
                sum1_length_lst.append(sum1_len)
                closet_num_lst.append(closet_num)
                bookcase_num_lst.append(bookcase_num)
                tbed_wid_lst.append(tbed_wid)
            elif thr == W_THREASHOLD2:
                closet_num = 0
                bookcase_num = 1
                tbed_wid = W_THREASHOLD1
                sum1_len = W_THREASHOLD1 + CUSTOM_CLOSET_LENGTH * closet_num + CUSTOM_BOOKCASE_LENGTH * bookcase_num
                sum1_length_lst.append(sum1_len)
                closet_num_lst.append(closet_num)
                bookcase_num_lst.append(bookcase_num)
                tbed_wid_lst.append(tbed_wid)
            elif thr == W_THREASHOLD3:
                closet_num = 1
                bookcase_num = 0
                tbed_wid = W_THREASHOLD1
                sum1_len = W_THREASHOLD1 + CUSTOM_CLOSET_LENGTH * closet_num + CUSTOM_BOOKCASE_LENGTH * bookcase_num
                sum1_length_lst.append(sum1_len)
                closet_num_lst.append(closet_num)
                bookcase_num_lst.append(bookcase_num)
                tbed_wid_lst.append(tbed_wid)
            elif thr == W_THREASHOLD4:
                closet_num = 1
                bookcase_num = 1
                tbed_wid = W_THREASHOLD1
                sum1_len = W_THREASHOLD1 + CUSTOM_CLOSET_LENGTH * closet_num + CUSTOM_BOOKCASE_LENGTH * bookcase_num
                sum1_length_lst.append(sum1_len)
                closet_num_lst.append(closet_num)
                bookcase_num_lst.append(bookcase_num)
                tbed_wid_lst.append(tbed_wid)

        pd_dict_m = {
            "sum_len_m":sum1_length_lst,
            "closet_num":closet_num_lst,
            "bookcase_num":bookcase_num_lst,
            "tbed_wid":tbed_wid_lst,
        }
        pd_dict_s = {
            "sum_len_s":sum2_length_lst,
            "writedesk_wid":writedesk_wid_lst,
            "tbed_len":tbed_len_lst
        }
        self.df1 = pd.DataFrame(pd_dict_m)
        self.df1 = self.df1.sort_values(by="sum_len_m")

        self.df2 = pd.DataFrame(pd_dict_s)
        self.df2 = self.df2.sort_values(by="sum_len_s")

    def modify_true_num(self,d_m,d_s,flag):
        bookcase_num = 0
        closet_num = 0
        if flag == 1:
            if d_m < W_THREASHOLD1:
                bookcase_num = 0
                closet_num = 0
            elif d_m >= W_THREASHOLD1 and d_m < W_THREASHOLD2:
                bookcase_num = 0
                closet_num = 0
            elif d_m >= W_THREASHOLD2 and d_m < W_THREASHOLD3:
                bookcase_num = 1
                closet_num = 0
            elif d_m >= W_THREASHOLD3 and d_m < W_THREASHOLD4:
                bookcase_num = 0
                closet_num = 1
            elif d_m >= W_THREASHOLD4:
                bookcase_num = 1
                closet_num = 1
        if flag == 0:
            if d_s < W_THREASHOLD1:
                bookcase_num = 0
                closet_num = 0
            elif d_s >= W_THREASHOLD1 and d_s < W_THREASHOLD2:
                bookcase_num = 0
                closet_num = 0
            elif d_s >= W_THREASHOLD2 and d_s < W_THREASHOLD3:
                bookcase_num = 1
                closet_num = 0
            elif d_s >= W_THREASHOLD3 and d_s < W_THREASHOLD4:
                bookcase_num = 0
                closet_num = 1
            elif d_s >= W_THREASHOLD4:
                bookcase_num = 1
                closet_num = 1
        return  bookcase_num,closet_num








