from AutoLayout.CommonElement import Door
from AutoLayout.dining_room.Element import *
from AutoLayout.helpers import *
from AutoLayout.dining_room.settings import *


class DiningRoom(Region):
    def __init__(self):
        super(DiningRoom, self).__init__()

    def run(self):
        virtual_boundary = get_virtual_boundary(self.boundary)
        (xmin, ymin, xmax, ymax) = virtual_boundary.polygon.bounds
        xlen = xmax - xmin
        ylen = ymax - ymin

        if xlen > DINING_ROOM_MAX_LEN or xlen < DINING_ROOM_MIN_LEN or \
                        ylen > DINING_ROOM_MAX_LEN or ylen < DINING_ROOM_MIN_LEN:
            raise Exception("warning:此功能区作为餐厅长度不满足")
        if abs(self.boundary.polygon.area) < DINING_ROOM_MIN_LEN * DINING_ROOM_MIN_LEN:
            raise Exception("warning:此功能区作为餐厅长度不满足")

        # 判断是否有门
        door_flag = False
        table_in_mid_flag = False  # 桌子是否放在中心flag
        door_list = []
        for d in self.ele_list:
            if isinstance(d, Door):
                door = d
                door_list.append(door)
                door_flag = True
        # 实墙的个数与虚边界的个数
        border_list = []
        wall_list = []
        for boundary in virtual_boundary.seg_list:
            for ll in self.line_list:
                if boundary.line.contains(ll.p1) and boundary.line.contains(ll.p2):
                    border_list.append(boundary)
                else:
                    wall_list.append(boundary)

        num_border = len(border_list)

        # 找到四边形内部的点
        dining_len = xlen
        dining_width = ylen

        table_len, table_width, table_type = arrange_table_chair(dining_len, dining_width)

        # 餐厅四面都是虚边界，餐桌椅放在中间
        if num_border == 4:
            table_wall = border_list[0]
            table_middle = virtual_boundary.polygon.centroid - table_wall.normal.p2 * table_len / 2
            table_in_mid_flag = True

        else:
            wall_list_tmp = wall_list.copy()
            for wl in wall_list[:]:
                for dl in door_list:
                    p_its = wl.seg.intersection(dl.boundary.polygon)
                    if len(p_its) != 0 and len(wall_list_tmp) != 0:
                        if wl in wall_list_tmp:
                            wall_list_tmp.remove(wl)
                    else:
                        pass

            if len(wall_list_tmp) == 0:
                # 所有实墙都有门
                tmp_list = [x.seg.length for x in wall_list]
                id = tmp_list.index(min(tmp_list))
                table_wall = wall_list[id]
                table_middle = virtual_boundary.polygon.centroid - table_wall.normal.p2 * table_len / 2
                table_in_mid_flag = True
            else:
                # 至少有一个实墙没有门
                tmp_list = [x.seg.length for x in wall_list_tmp]
                id = tmp_list.index(max(tmp_list))
                table_wall = wall_list_tmp[id]
                for i in range(len(door_list)):
                    if door_flag and door_list[i].backline.normal.intersection(table_wall.normal):
                        if len(wall_list_tmp) == 1:
                            pass
                        else:
                            table_wall = wall_list_tmp[1 - id]
                table_middle = table_wall.seg.midpoint

        table_mid = Point2D(int(table_middle.x), int(table_middle.y))
        p1 = table_mid - table_wall.dir.p2 * int(table_width / 2)
        p2 = table_mid + table_wall.dir.p2 * int(table_width / 2)
        p1, p2 = DY_segment.get_p1_p2_from_normal(table_wall.normal, p1, p2)
        bl = DY_segment(p1, p2)
        square_table = SquareDiningTable(bl, table_len)
        self.ele_list.append(square_table)

        # 厨房够大，可以放下餐边柜
        # 餐边柜放在餐椅后面
        adj_table_walls = []
        adj_flag = True
        opposite_table_flag = False
        if len(wall_list) == 0:
            adj_flag = False
        else:
            for s in wall_list:
                if s.seg != table_wall.seg:
                    if s.seg.contains(table_wall.seg.p1) or s.seg.contains(table_wall.seg.p2):
                        adj_table_walls.append(s)
                        adj_flag = True
                    else:
                        adj_flag = False
                else:
                    adj_flag = False
        sideboard = table_wall.seg.length
        if sideboard > table_len + DINING_CHAIR[1]*2 + SIDEBOARD_CABINET_WIDTH:  # 餐椅最大尺寸，有餐边桌
            adj_table_flag = True and adj_flag
            chair_len = max(DINING_CHAIR)
        else:
            if sideboard > table_len + DINING_CHAIR[0]*2 + SIDEBOARD_CABINET_WIDTH:  # 餐椅最小尺寸，有餐边桌
                adj_table_flag = True and adj_flag
                chair_len = min(DINING_CHAIR)
            else:
                if sideboard > table_len + DINING_CHAIR[1]*2 + SIDEBOARD_CABINET_WIDTH:  # 餐椅最大尺寸，无餐边桌
                    adj_table_flag = False and adj_flag
                    chair_len = max(DINING_CHAIR)
                else:
                    if sideboard > table_len + DINING_CHAIR[0]*2 + SIDEBOARD_CABINET_WIDTH:  # 餐椅最小尺寸，无餐边桌
                        adj_table_flag = False and adj_flag
                        chair_len = min(DINING_CHAIR)
                    else:
                        adj_table_flag = False and adj_flag     # 默认，无餐边桌， 且椅子最小
                        chair_len = min(DINING_CHAIR)
                        # raise Exception("尺寸太小")
        # 餐边桌放在桌子对面
        if len(wall_list) == 0:
            pass
        else:
            for s in wall_list:
                if s.normal.p2.equals(table_wall.normal.p2 * (-1)):
                    opposite_table_walls = s
                    dd = opposite_table_walls.seg.distance(table_mid) - table_len
                    if dd > MIN_DIS_SIDEBOARD:  # 距离餐桌最近600
                        opposite_table_flag = True
                        break
                    else:
                        opposite_table_flag = False
                        break
                else:
                    opposite_table_walls = None
                    opposite_table_flag = False

        if table_type == 6:
            for i in range(3):
                chair_p1 = table_mid - table_wall.dir.p2 * int(table_width / 2 + chair_len)
                chair_p2 = table_mid - table_wall.dir.p2 * int(table_width / 2)
                chair_p1, chair_p2 = DY_segment.get_p1_p2_from_normal(table_wall.normal, chair_p1, chair_p2)
                chair_bl = DY_segment(chair_p1, chair_p2)
                chair = DiningChair(chair_bl, chair_len)
                # cf = True
                # for i in range(len(door_list)):
                #     if door_flag and door_list[i].boundary.polygon.intersection(chair.boundary.polygon):
                #         cf = False
                #         break
                # if not cf:
                #     pass
                # else:
                #     self.ele_list.append(chair)
                self.ele_list.append(chair)
                chair_p11 = table_mid + table_wall.dir.p2 * int(table_width / 2 + chair_len)
                chair_p22 = table_mid + table_wall.dir.p2 * int(table_width / 2)
                chair_p11, chair_p22 = DY_segment.get_p1_p2_from_normal(table_wall.normal, chair_p11, chair_p22)
                chair_bll = DY_segment(chair_p11, chair_p22)
                chairr = DiningChair(chair_bll, chair_len)
                # ccf = True
                # for i in range(len(door_list)):
                #     if door_flag and door_list[i].boundary.polygon.intersection(chair.boundary.polygon):
                #         ccf = False
                #         break
                # if not ccf:
                #     pass
                # else:
                #     self.ele_list.append(chairr)
                self.ele_list.append(chairr)
                table_mid = table_mid + table_wall.normal.p2 * int(table_len / 2 - chair_len / 2)
        elif table_type == 4:
            for i in range(2):
                chair_p1 = table_mid - table_wall.dir.p2 * int(table_width / 2 + chair_len)
                chair_p2 = table_mid - table_wall.dir.p2 * int(table_width / 2)
                chair_p1, chair_p2 = DY_segment.get_p1_p2_from_normal(table_wall.normal, chair_p1, chair_p2)
                chair_bl = DY_segment(chair_p1, chair_p2)
                chair = DiningChair(chair_bl, chair_len)
                self.ele_list.append(chair)
                chair_p11 = table_mid + table_wall.dir.p2 * int(table_width / 2 + chair_len)
                chair_p22 = table_mid + table_wall.dir.p2 * int(table_width / 2)
                chair_p11, chair_p22 = DY_segment.get_p1_p2_from_normal(table_wall.normal, chair_p11, chair_p22)
                chair_bll = DY_segment(chair_p11, chair_p22)
                chairr = DiningChair(chair_bll, chair_len)
                self.ele_list.append(chairr)
                table_mid = table_mid + table_wall.normal.p2 * int(table_len - chair_len)

        sideboard_width = SIDEBOARD_CABINET_WIDTH
        # 餐边桌放在桌子对面
        if opposite_table_flag and not table_in_mid_flag:
            for sideboard_len in reversed(SIDEBOARD_CABINET_LEN):
                sideboard_table_mid = opposite_table_walls.seg.midpoint
                st_p1 = sideboard_table_mid - opposite_table_walls.dir.p2 * int(sideboard_len / 2)
                st_p2 = sideboard_table_mid + opposite_table_walls.dir.p2 * int(sideboard_len / 2)
                st_p1, st_p2 = DY_segment.get_p1_p2_from_normal(opposite_table_walls.normal, st_p1, st_p2)
                st_bl = DY_segment(st_p1, st_p2)
                side_cabinet = True
                for i in range(len(door_list)):
                    if door_flag and door_list[i].boundary.polygon.intersection(st_bl.line) \
                            or door_list[i].boundary.polygon.intersection(st_bl.normal):
                        side_cabinet = False
                    else:
                        pass
                if not side_cabinet:
                    sideboard_len += 1
                else:
                    sideboard = SideboardCabinet(st_bl, sideboard_width)
                    # self.ele_list.append(sideboard)
                    break
        else:
            # raise Exception("无法安放餐边柜")
            pass

        # 餐边柜放在餐椅后面
        if adj_table_flag and not table_in_mid_flag:
            for sideboard_len in reversed(SIDEBOARD_CABINET_LEN):
                sideboard_table_mid = adj_table_walls[0].seg.midpoint
                st_p1 = sideboard_table_mid - adj_table_walls[0].dir.p2 * int(sideboard_len / 2)
                st_p2 = sideboard_table_mid + adj_table_walls[0].dir.p2 * int(sideboard_len / 2)
                st_p1, st_p2 = DY_segment.get_p1_p2_from_normal(adj_table_walls[0].normal, st_p1, st_p2)
                st_bl = DY_segment(st_p1, st_p2)
                side_cabinet = True
                for i in range(len(door_list)):
                    if door_flag and door_list[i].boundary.polygon.intersection(st_bl.line) \
                            or door_list[i].boundary.polygon.intersection(st_bl.normal):
                        side_cabinet = False
                    else:
                        pass
                if not side_cabinet:
                    sideboard_len += 1
                else:
                    sideboard = SideboardCabinet(st_bl, sideboard_width)
                    # self.ele_list.append(sideboard)
                    break
        else:
            # raise Exception("无法安放餐边柜")
            pass


def arrange_table_chair(length, width):
    table_len, table_width, table_type = 0, 0, 0
    if length * width > DINING_LEN[0] * DINING_LEN[1]:
        table_len = SQUARE_DININD_TABLE_6_LEN[0]
        table_width = SQUARE_DININD_TABLE_6_WIDTH
        table_type = 6
    else:
        if length * width > DINING_LEN[1] * DINING_LEN[3]:
            table_len = SQUARE_DININD_TABLE_4_LEN[1]
            table_width = SQUARE_DININD_TABLE_4_WIDTH[0]
            table_type = 4
        else:
            if length * width > DINING_LEN[2] * DINING_LEN[2]:
                table_len = SQUARE_DININD_TABLE_4_WIDTH[0]
                table_width = SQUARE_DININD_TABLE_4_WIDTH[1]
                table_type = 4
    return table_len, table_width, table_type

