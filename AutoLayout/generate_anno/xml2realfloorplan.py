from __future__ import division
# —*— coding: utf-8 _*_


from lxml import etree
from pylab import mpl
from sympy.geometry import Point2D, Segment2D

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
import matplotlib.pylab as plt
from matplotlib.lines import Line2D
import matplotlib.patches as patches
import cv2
import numpy as np

from skimage import transform
# from PIL import Image
# from PIL import ImageDraw

from BaseClass import House, DY_segment,DY_boundary
from BaseModual import FloorPlan
from DY_Line import Window, Border
import settings
import helpers
from CommonElement import Door
import main_bedroom.Base
import livingroom.Base
import bedroom.Base
import tatami_room.Base
import dining_room.Base
import balcony.Base
import kitchen.Base
import bathroom.Base
import porch.Base
import unknow.Base



TAG = "tag"
ATT = 'attribute'
functional_zone = {
    main_bedroom.Base.MainBedroom.__name__: main_bedroom.Base.MainBedroom,
    livingroom.Base.Livingroom.__name__: livingroom.Base.Livingroom,
    bathroom.Base.Bathroom.__name__: bathroom.Base.Bathroom,
    kitchen.Base.Kitchen.__name__: kitchen.Base.Kitchen,
    porch.Base.Porch.__name__: porch.Base.Porch,
    balcony.Base.Balcony.__name__: balcony.Base.Balcony,
    dining_room.Base.DiningRoom.__name__: dining_room.Base.DiningRoom,
    bedroom.Base.Bedroom.__name__: {settings.BEDROOM_TYPE[0]: bedroom.Base.Bedroom,
                                    settings.BEDROOM_TYPE[1]: tatami_room.Base.TatamiRoom}
}


def read_o1_xml_to_house(fname):
    xml = etree.parse(fname)
    root = xml.getroot()
    flp_nd = [n for n in root.getchildren() if n.tag == House.__name__][0] \
        .getchildren()[0]
    flp = FloorPlan()
    flp.set_boundary(get_boundary(flp_nd))
    for n in flp_nd.getchildren():
        zone = get_functional_zone(n, flp)
        flp.add_region(zone)
    house = House()
    house.add_floorplan(flp)
    return house


def get_functional_zone(node, flp):
    if node.tag not in functional_zone.keys():
        zone = unknow.Base.Unknow()
    else:
        # zone = functional_zone.get(node.tag)()
        zone = functional_zone.get(node.tag)
        if isinstance(zone, dict):
            if node.get(ATT) is None:
                zone = zone.get(settings.BEDROOM_TYPE[0])
            else:
                zone = zone.get(node.get(ATT))
        zone = zone()

    zone.set_boundary(get_boundary(node))

    for subnode in node.getchildren():
        add_door_win_border(subnode, zone)

    return zone


def get_DY_segment(key, node):
    p_str_list = node.get(key).split(';')
    p_list = []
    for p_str in p_str_list:
        list0 = p_str[1:-1].split(',')
        pt = Point2D(int(list0[0]), int(list0[1]))
        p_list.append(pt)
    dy_seg = DY_segment(p_list[0], p_list[1])
    return dy_seg


def add_door_win_border(node, region):
    if node.tag == Window.__name__:
        bound = get_boundary(node)
        coin_seg = bound.polygon.intersection(region.boundary.polygon)
        coin_seg = [seg for seg in coin_seg if isinstance(seg, Segment2D)]
        for seg in coin_seg:
            window = Window(seg.p1, seg.p2)
            window.set_boundary(bound)
            region.add_window(window)
    if node.tag == Door.__name__:
        dr = Door()
        if node.get('attribute') is None:
            dr.set_type(settings.DOOR_TYPE[0])
        dr.set_boundary(get_boundary(node))
        dr.set_body(get_DY_segment("body", node))
        dr.set_backline(get_DY_segment("backline", node))
        region.add_door(dr)
    if node.tag == Border.__name__:
        bord_seg = get_DY_segment("line", node)
        bord = Border(bord_seg.p1, bord_seg.p2)
        region.add_border(bord)


def get_boundary(node):
    key = "boundary"
    if node.get(key) == None:
        return None
    p_str_list = node.get(key).split(';')
    p_list = []
    for p_str in p_str_list:
        if p_str == '':
            continue
        list0 = p_str[1:-1].split(',')
        pt = Point2D((int(list0[0])), (int(list0[1])))
        p_list.append(pt)
    eval_str = 'DY_boundary('
    for p in p_list:
        if p != p_list[-1]:
            eval_str += str(p) + ','
        else:
            eval_str += str(p)
    eval_str += ')'
    boundary = eval(eval_str)
    return boundary


def display(house, floorplanfile, savename=None):
    if savename is not None:
        name1 = savename[:-4]
    origin = cv2.imread(floorplanfile)
    for idx, f in enumerate(house.floor_list):
        figure, ax = plt.subplots()
        f.boundary.draw(ax)
        # cv2.line(origin,  )
        xylist_floorplan = f.boundary.polygon.vertices
        ax.add_patch(
            patches.Polygon(
                xylist_floorplan,
                True,
                color='#000000')
        )
        ele_list = []
        line_list = []
        bound_list = []
        # ls = '-'
        # col = '#000000'
        for r in f.region_list:
            ele_list.extend(r.ele_list)
            line_list.extend(r.line_list)
            bound_list.append(r.boundary)
        for b in bound_list:
            xylist_region = b.polygon.vertices
            ax.add_patch(
                patches.Polygon(
                    xylist_region,
                    True,
                    color='#FFFFFF')
            )
            # xmin, ymin, xmax, ymax = b.polygon.bounds
            # xlen = xmax - xmin
            # ylen = ymax - ymin
            # a = Image.new('RGB', (xlen, ylen))
            # m = ImageDraw.Draw(a)
            # m.polygon([b.polygon.vertices], fill=0xff00ff)
            # a.show()
            # for s in b.seg_list:
            #     xdata = (s.p1.x, s.p2.x)
            #     ydata = (s.p1.y, s.p2.y)
            #     ax.add_line(Line2D(xdata, ydata, linestyle=ls, color=col))
            # fill Rectangle
            # xylist = sorted(b.polygon.vertices,key=lambda v:(v.x,v.y))
            # if len(b.polygon.vertices) < 5:
            #     ax.add_patch(
            #         patches.Rectangle(
            #             xylist[0],
            #             xlen,
            #             ylen,
            #
            #         )
            #        )
            # fill Polygon

        for l in line_list:
            l.draw(ax)
        for e in ele_list:
            # if e.is_multiple:
            #     for ee in e.ele_list:
            #         ee.draw(ax)
            # e.draw(ax)
            if isinstance(e, Door):
                draw_door(e, ax)
                xylist_door = e.boundary.polygon.vertices
                ax.add_patch(
                    patches.Polygon(
                        xylist_door,
                        True,
                        color='#FFFFFF')
                )
        ax.set_aspect(1)
        ax.set_xticks([])
        ax.set_yticks([])
        xlist = sorted(f.boundary.polygon.vertices, key=lambda v: v.x)
        ylist = sorted(f.boundary.polygon.vertices, key=lambda v: v.y)
        plt.xlim(int(xlist[0].x), int(xlist[-1].x))
        plt.xlim(int(xlist[0].x) - 1000, int(xlist[-1].x) - 1000)
        plt.ylim(int(ylist[0].y), int(ylist[-1].y))
        # plt.xlim(int(xlist[0].x), int(xlist[-1].x))
        # plt.ylim(int(ylist[0].y), int(ylist[-1].y))
        # plt.axis('off')

        # length = str(float((ylist[-1].y - ylist[0].y) / 1000)) + ' m'
        # ypos = (int(ylist[0].y) + int(ylist[-1].y)) / 2
        # ax.text(int(xlist[0].x) - 300, ypos, length, rotation='vertical')
        # length = str(float((xlist[-1].x - xlist[0].x) / 1000)) + ' m'
        # xpos = (int(xlist[0].x) + int(xlist[-1].x)) / 2
        # ax.text(xpos, int(ylist[0].y) - 300, length)

        if savename is None:
            plt.show()
        if savename is not None:
            # savename1 = name1 + '_' + str(idx) + '.jpg'
            savename1 = name1 + '.png'
            plt.savefig(savename1, dpi=200, bbox_inches='tight', pad_inches=0)
        figure.clf()
        plt.clf()
        plt.close()


def draw_door(obj, ax):
    obj.boundary.draw(ax, ls='-', col='#9AFF9A')  # 门用绿色表示

    xdata = (obj.backline.p1.x, obj.backline.p2.x)
    ydata = (obj.backline.p1.y, obj.backline.p2.y)
    ax.add_line(Line2D(xdata, ydata, color='#FFFFFF'))  # 门墙结合处没有颜色
    # xdata = (self.door_body.p1.x, self.door_body.p2.x)
    # ydata = (self.door_body.p1.y, self.door_body.p2.y)
    # ax.add_line(Line2D(xdata, ydata, color='#9AFF9A'))

    # l0 = Line(self.point_list[0], self.point_list[2])
    # l1 = Line(self.point_list[1], self.point_list[3])
    # xdata = (l0.p1.x, l0.p2.x)
    # ydata = (l0.p1.y, l0.p2.y)
    # ax.add_line(Line2D(xdata, ydata, color='#9AFF9A'))
    # xdata = (l1.p1.x, l1.p2.x)
    # ydata = (l1.p1.y, l1.p2.y)
    # ax.add_line(Line2D(xdata, ydata, color='#9AFF9A'))
def compare_images(fname1, fname2):
    input_png = cv2.imread(fname1)
    output_png = cv2.imread(fname2)
    w1, h1 = output_png.shape[:2]
    center_o1 = (w1 // 2, h1 // 2)
    print(center_o1)
    # M = np.float32([[1, 0, 1.6521195 * 3*15.86], [0, 1, 3.321139 * 15.86]])

    # dst = cv2.warpAffine(output_png, M, (h,w) )#平移
    # w, h = input_png.shape[:2]
    # output_png = cv2.resize(output_png, (h*16,w*16), interpolation=cv2.INTER_CUBIC )
    w, h = input_png.shape[:2]
    center_origin = (w // 2, h // 2)
    print(center_origin)
    w_ratio = (float)(center_origin[0]) / (float)(center_o1[0])
    h_ratio = (float)(center_origin[1]) / (float)(center_o1[1])
    output_png = cv2.resize(output_png, (h, w), interpolation=cv2.INTER_CUBIC)
    # # M = np.float32([[1, 0, -w_ratio * 14.3], [0, 1, -h_ratio * 14.3]])
    # M = np.float32([[1, 0, 0], [0, 1, 0]])
    # dst = cv2.warpAffine(output_png, M, (h1, w1))  # 平移
    #
    # w2, h2 = dst.shape[:2]
    # # dst = cv2.resize(dst, (int(h2 * 1.1), int(w2 * 1.1)), interpolation=cv2.INTER_CUBIC)
    # center_warp = (w2 // 2, h2 // 2)
    # print(center_warp)
    # dst = cv2.resize(dst, (h, w), interpolation=cv2.INTER_CUBIC)
    # output_png = cv2.warpAffine(output_png, M, (h, w))  # 平移
    cv2.imwrite(r'E:\xml2floorplan.png',output_png)
    imge_mix1 = cv2.addWeighted(input_png, 0.4, output_png, 0.6, 0)
    # imge_mix2 = cv2.addWeighted(input_png, 0.4, dst, 0.6, 0)
    cv2.imshow('origin', input_png)
    cv2.imshow('o1_output', output_png)
    cv2.imshow('image_mix1', imge_mix1)
    # cv2.imshow('image_mix2', imge_mix2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    xml_file = r'F:\20180112new_bk.xml'
    # xml_file = r'E:\jxh\subtasks\zhuc\zn.xml'
    # xml_file = r'F:\天津test.xml'
    # xml_file = r'test\fp_new.xml'
    xml_gen_png = r'F:\f.png'
    floorplan_file = r'F:\保利金泉.png'
    house = read_o1_xml_to_house(xml_file)
    display(house, floorplan_file, xml_gen_png)
    save_xml_name = r'F:\f.xml'
    # helpers.save_house_to_xml(house, save_xml_name)
    # compare_images(floorplan_file,xml_gen_png)
