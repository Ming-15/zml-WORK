#—*— coding: utf-8 _*_
import AutoLayout.DY_Line as DY_Line
import AutoLayout.CommonElement as CommonElement
import AutoLayout.settings as settings
from  AutoLayout.BaseModual import DY_segment
import AutoLayout.helpers as helpers
import AutoLayout.BaseClass as BaseClass


def get_far_vertice(door, boundary):
    dr_center = door.boundary.polygon.centroid
    corner = sorted(boundary.polygon.vertices, key=lambda v: dr_center.distance(v))

    return corner[-1]

def get_doorbackline_wall_dis(boundary, door1):
    dis0, dis1 = 0, 0
    if door1 is not None:
        if door1.type == settings.DOOR_TYPE[0] or settings.DOOR_TYPE[1]:
            tmp_seg = DY_segment(door1.backline.normal.p1, door1.backline.normal.p2)
            parallel_wall_dr = helpers.get_paralleled_line(tmp_seg, boundary, type=DY_segment)
            tmp_seg = parallel_wall_dr[0]
            dis0 = helpers.get_min_dis_seg_boundary(tmp_seg, door1.boundary)
            tmp_seg = parallel_wall_dr[1]
            dis1 = helpers.get_min_dis_seg_boundary(tmp_seg, door1.boundary)

            return dis0, parallel_wall_dr[0], dis1, parallel_wall_dr[1]

def get_new_door(dy_line):
    #主要实例推拉门
    p3 = dy_line.seg.p1 - dy_line.normal.p2 * 240
    p4 = dy_line.seg.p2 - dy_line.normal.p2 * 240
    door = CommonElement.Door()
    door.set_type(settings.DOOR_TYPE[2])
    door.set_boundary(BaseClass.DY_boundary(dy_line.seg.p1, p3, p4, dy_line.seg.p2))
    door.set_backline(dy_line)
    return  door

def exchange_vir_door(self, vir_door, door):

    tmp = vir_door
    vir_door = door
    door = tmp
    return vir_door, door

def exchange_vir_boundary(self, vir_boundary, boundary):

    tmp = vir_boundary
    vir_boundary = boundary
    boundary = tmp
    return vir_boundary, boundary
