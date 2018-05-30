# —*— coding: utf-8 _*_
__author__ = 'zhuc-jxh'
from lxml import etree
from pylab import mpl
from sympy.geometry import Point2D, Segment2D
import numpy as np
import csv
import os

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
import pandas as pd
from AutoLayout.BaseClass import House, DY_segment, DY_boundary
from AutoLayout.BaseModual import FloorPlan
from AutoLayout.DY_Line import Window, Border
from AutoLayout.CommonElement import Door, Closet, NightTable, Chair, \
    WritingDesk, Drawers, Recliner, Curtain
from AutoLayout.hard_deco.Element import Ceiling_lamp
import AutoLayout.settings

import AutoLayout.main_bedroom.Base
import AutoLayout.main_bedroom.Element as main_e
import AutoLayout.livingroom.Base
import AutoLayout.bedroom.Base
import AutoLayout.tatami_room.Base
import AutoLayout.dining_room.Base
import AutoLayout.balcony.Base
import AutoLayout.kitchen.Base
import AutoLayout.bathroom.Base
import AutoLayout.porch.Base
import AutoLayout.unknow.Base
from AutoLayout.standardfiles.model_products_data import *
import sys
sys.path.append("..")
PARENT_TAG = "parent_id"
BROTHER_TAG = "brother_id"
TAG = "tag"
ATT = 'attribute'
module_path = os.path.dirname(AutoLayout.__file__)
DATASET = module_path + r'\dataset.xlsx'
OUTFILE = module_path + r'\checkresults.csv'
FLOOR_TAG = 'Floor'
SKIRTINGLINE_TAG = 'SkirtingLine'
PLASTERLINE_TAG = 'PlasterLine'

# PRODUCT_NAME = { 'BED': '床', 'BED_SIDE': '床头柜','DRAW_CAB': '屉柜', 'CLOSET ': '衣柜',
#                       'WDESK': '写字桌','GFBED': '贵妃榻', 'LAZY_CHAIR': '休闲椅', 'CHAIR': '单椅'}
PRODUCT_NAME_MAIN_BED = (main_e.Bed, NightTable, Closet, Curtain, Chair, WritingDesk, Drawers, Recliner, Ceiling_lamp)
# PRODEUCT_CLASS = {'BED_CLASS': '床榻类', 'CLO_CLASS': '柜架类', 'STOOL_CLASS': '桌几类','DC_CLASS': '桌椅类',
#                       'SOFA_CLASS': '沙发类', }
# HEADTAG = ['空间','风格属性','产品编号','产品名称','产品类别','X','Y','产品二维图	','模型图片','模型尺寸','附属饰品']
# new dataset defined below
HEADTAG = ['风格属性', '产品编号', '产品名称', '产品类别', 'x(长)', 'y(宽)', 'z(高)',
           '产品二维图	', '模型图片', '附属饰品图片', '附属品名称', '备注']
# TODO: 其他string


functional_zone = {
    AutoLayout.main_bedroom.Base.MainBedroom.__name__: AutoLayout.main_bedroom.Base.MainBedroom,
    AutoLayout.livingroom.Base.Livingroom.__name__: AutoLayout.livingroom.Base.Livingroom,
    AutoLayout.bathroom.Base.Bathroom.__name__: AutoLayout.bathroom.Base.Bathroom,
    AutoLayout.kitchen.Base.Kitchen.__name__: AutoLayout.kitchen.Base.Kitchen,
    AutoLayout.porch.Base.Porch.__name__: AutoLayout.porch.Base.Porch,
    AutoLayout.balcony.Base.Balcony.__name__: AutoLayout.balcony.Base.Balcony,
    AutoLayout.dining_room.Base.DiningRoom.__name__: AutoLayout.dining_room.Base.DiningRoom,
    AutoLayout.bedroom.Base.Bedroom.__name__: {AutoLayout.settings.BEDROOM_TYPE[0]: AutoLayout.bedroom.Base.Bedroom,
                                    AutoLayout.settings.BEDROOM_TYPE[1]: AutoLayout.tatami_room.Base.TatamiRoom},
    AutoLayout.unknow.Base.UnKnown.__name__: AutoLayout.unknow.Base.UnKnown

}
class_tupe_dict = {
    AutoLayout.main_bedroom.Base.MainBedroom.__name__: ['主卧', PRODUCT_NAME_MAIN_BED],
    AutoLayout.livingroom.Base.Livingroom.__name__: ['客厅', ()],
    AutoLayout.bathroom.Base.Bathroom.__name__: ['卫生间', ()], AutoLayout.kitchen.Base.Kitchen.__name__: ['厨房', ()],
    AutoLayout.porch.Base.Porch.__name__: ['过道', ()], AutoLayout.dining_room.Base.DiningRoom.__name__: ['餐厅', ()],
    AutoLayout.balcony.Base.Balcony.__name__: ['阳台', ()], AutoLayout.bedroom.Base.Bedroom.__name__: ['客房', ()]
}
region_product_name = ['主卧产品名称', '客房产品名称', '榻榻米产品名称', '客厅产品名称', '厨房产品名称', '餐厅产品名称',
               '卫生间产品名称', '过道产品名称', '阳台产品名称', '产品类别']

class_tupe_dict1 = {
    AutoLayout.main_bedroom.Base.MainBedroom.__name__: ['主卧', CLASSIFIER_DATA[region_product_name[0]], MAIN_BED],
    AutoLayout.livingroom.Base.Livingroom.__name__: ['客厅', CLASSIFIER_DATA[region_product_name[3]], LIVING],
    AutoLayout.bathroom.Base.Bathroom.__name__: ['卫生间', CLASSIFIER_DATA[region_product_name[6]], BATH],
    AutoLayout.kitchen.Base.Kitchen.__name__: ['厨房', CLASSIFIER_DATA[region_product_name[4]], KITCHEN],
    AutoLayout.porch.Base.Porch.__name__: ['过道', CLASSIFIER_DATA[region_product_name[7]], PORCH],
    AutoLayout.bedroom.Base.Bedroom.__name__: ['客房', CLASSIFIER_DATA[region_product_name[1]], GUEST],
    AutoLayout.balcony.Base.Balcony.__name__: ['阳台', CLASSIFIER_DATA[region_product_name[8]], BALCONY],
    AutoLayout.dining_room.Base.DiningRoom.__name__: ['餐厅', CLASSIFIER_DATA[region_product_name[5]], DINNING],
    AutoLayout.tatami_room.Base.TatamiRoom.__name__: ['榻榻米', CLASSIFIER_DATA[region_product_name[2]], TATAMI]
}


def get_functional_zone(node, flp, uuid):
    if node.tag not in functional_zone.keys():
        zone = AutoLayout.unknow.Base.UnKnown()
    else:
        # zone = functional_zone.get(node.tag)()
        zone = functional_zone.get(node.tag)
        if isinstance(zone, dict):
            if node.get(ATT) is None:
                zone = zone.get(AutoLayout.settings.BEDROOM_TYPE[0])
            else:
                zone = zone.get(node.get(ATT))
        zone = zone()

    zone.set_boundary(get_boundary(node))
    zone.uuid = uuid

    for subnode in node.getchildren():
        add_door_win_border(subnode, zone)

    return zone


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
        pt = Point2D(int(list0[0]), int(list0[1]))
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
            dr.set_type(AutoLayout.settings.DOOR_TYPE[0])
        else:
            dr.set_type(node.get('attribute'))
        dr.set_boundary(get_boundary(node))
        if node.get('body') is not None:
            dr.set_body(get_DY_segment("body", node))
        dr.set_backline(get_DY_segment("backline", node))
        # 读取门连接的两个功能区
        conn_string = node.get('connect')
        if conn_string.find(';') == -1:
            raise "门的连接为空"
        connect_list = conn_string.split(';')
        dr.set_connect_list(connect_list[0], connect_list[1])

        region.add_door(dr)
    if node.tag == Border.__name__:
        bord_seg = get_DY_segment("line", node)
        bord = Border(bord_seg.p1, bord_seg.p2)
        region.add_border(bord)


def set_id_and_its_brother(node):
    '''
    通过判断包含父节点来设置其ID及Brother ID
    bug修改：当一个户型有多个功能区需要划分区域时：需要根据parent_id 是否相同来捆绑分类brother_id

    '''
    parent_id_dic = {}
    node_new = []
    for nd in node:
        if not PARENT_TAG in nd.attrib:
            node_new = node
            continue
        parent_id_dic[nd.get(PARENT_TAG)] = parent_id_dic.get(nd.get(PARENT_TAG), 0) + 1

    for par in parent_id_dic.keys():
        brother_id = []
        for nd in node:
            if not PARENT_TAG in nd.attrib:
                continue
            if nd.get(PARENT_TAG) == par:
                brother_id.append(nd.get(TAG))

        brother_id = ';'.join(brother_id)
        node_new = change_node_properties_brother_id(node, {BROTHER_TAG: brother_id})

    return node_new


def change_node_properties_brother_id(node, kv_map, is_delete=False):
    '''修改/增加 /删除 节点的属性及属性值
    nodelist: 节点列表
    kv_map:属性及属性值map'''
    node_new = []
    for nd in node:
        for key in kv_map:
            if is_delete:
                if key in nd.attrib:
                    del node.attrib[key]
            else:
                if PARENT_TAG in nd.attrib and nd.get(TAG) in kv_map.get(key):
                    nd.set(key, kv_map.get(key))
                node_new.append(nd)
    return node_new


def build_room(node, room_dict, connect_dict):
    """
    通过父节点和兄弟节点，找到虚边界

    """
    if node.tag not in functional_zone.keys():
        return None
    p_tag = node.get(PARENT_TAG)
    b_tag = node.get(BROTHER_TAG).split(';')

    zone = room_dict.get(node.get(TAG))
    parent = room_dict.get(p_tag)
    # 添加门窗
    for ele in parent.ele_list:
        if not isinstance(ele, Door):
            continue
        coin = ele.boundary.polygon.intersection(zone.boundary.polygon)
        if coin:
            zone.add_door(ele)
    for l in parent.line_list:
        if not isinstance(l, Window):
            continue
        coin = l.boundary.polygon.intersection(zone.boundary.polygon)
        if coin:
            zone.add_window(l)
    # 添加虚边界
    for btag in b_tag:
        if btag == node.get(TAG):
            continue
        coin = room_dict[btag].boundary.polygon.intersection(
            zone.boundary.polygon
        )
        coin = [seg for seg in coin if isinstance(seg, Segment2D)]
        for seg in coin:
            bd = Border(seg.p1, seg.p2)
            bd.set_connect_list(connect_dict.get(btag).tag,
                                node.tag)
            zone.add_border(bd)

    return zone


def check_dataset(fname=DATASET, outfile=OUTFILE):
    exception = []
    try:
        out = open(outfile, 'w', newline='')
        csv_writer = csv.writer(out, dialect='excel')
        check_res = {}
        all_data = pd.read_excel(DATASET, sheetname=None, header=0)
        for key in class_tupe_dict1.keys():
            if key == 'TatamiRoom':
                continue
            # if key != 'Kitchen':
            #     continue
            # print(key + '尺寸校对结果如下:')
            res_size_list = [key, ' 尺寸校对结果：\n']
            csv_writer.writerow(res_size_list)
            region = class_tupe_dict1[key][0]
            if region not in EXIST_RIGION:
                continue
            zone_data = all_data[class_tupe_dict1[key][0]]
            if zone_data.empty:
                exception.append(class_tupe_dict1[key][0] + 'is empty!')
                check_res[key] = False
                print(class_tupe_dict1[key][0] + ' is empty!')
            else:
                # first we check the contents of standard file whether they are complete or not
                product = {}
                for i in zone_data[HEADTAG[2]]:
                    product[i] = product.get(i, 0) + 1
                diff_pos = [ele for ele in class_tupe_dict1[key][1]
                        if ele not in product.keys()]
                diff_neg = [ele for ele in product.keys() if ele not in class_tupe_dict1[key][1]]
                if diff_pos == ['附属品']:
                    #second we check the x,y,z parameters
                    match_products = {}
                    match_products_x_y = {}
                    for ele in class_tupe_dict1[key][1]:
                        match_products[ele] = zone_data.loc[ele == zone_data.loc[:, HEADTAG[2]]]
                        x = match_products[ele].loc[:, HEADTAG[4]]
                        y = match_products[ele].loc[:, HEADTAG[5]]
                        match_products_x_y.setdefault(ele, []).append(tuple(y))
                        match_products_x_y.setdefault(ele, []).append(tuple(x))
                        if class_tupe_dict1[key][2][ele] == []:
                            continue
                        if len(class_tupe_dict1[key][2][ele]) == 1:

                            if type(class_tupe_dict1[key][2][ele][0]) == type({}):
                                # if np.mean(tuple(class_tupe_dict1[key][2][ele][0].values())) == \
                                #         np.mean(match_products_x_y[ele][0]):
                                if list(set(tuple(class_tupe_dict1[key][2][ele][0].values())) ^
                                                set(match_products_x_y[ele][0])) == []:
                                    pass
                                    # print(ele + ' ok')
                            else:
                                if ele == '躺椅' or ele == '餐椅':  # here makes the logic lower
                                    temp00 = []
                                    temp00.append(class_tupe_dict1[key][2][ele][0][1])
                                    temp01 = list(match_products_x_y[ele][0])
                                    temp02 = []
                                    temp02.append(class_tupe_dict1[key][2][ele][0][0])
                                    temp03 = list(match_products_x_y[ele][1])
                                    if list(set(temp00) ^ set(temp01)) == [] and list(set(temp02) ^ set(temp03)) == []:
                                        # print(ele + ' ok')
                                        pass
                                    else:
                                        size_res = [ele, 'not ok']
                                        csv_writer.writerow(size_res)
                                        # print(ele + ' not ok')
                                else:
                                    temp00 = []
                                    if type(class_tupe_dict1[key][2][ele][0]) == type(1):
                                        temp00.append(class_tupe_dict1[key][2][ele][0])
                                    elif type(class_tupe_dict1[key][2][ele][0]) == type((1,)):
                                        temp00 = list(class_tupe_dict1[key][2][ele][0])
                                    # temp01 = []
                                    temp01 = list(match_products_x_y[ele][0])
                                    # if np.mean(class_tupe_dict1[key][2][ele][0]) == np.mean(match_products_x_y[ele][0]):
                                    if list(set(temp00) ^ set(temp01)) == []:
                                        # print(ele + ' ok')
                                        check_res[key] = True
                                    else:
                                        check_res[key] = False
                                        # print(ele + ' not ok')
                                        size_res = [ele, 'not ok']
                                        csv_writer.writerow(size_res)

                        else:
                            temp1 = []
                            temp2 = []
                            temp4 = []
                            temp1.append(class_tupe_dict1[key][2][ele][0])
                            if type(class_tupe_dict1[key][2][ele][0]) == type((1,)):
                                temp1 = list(class_tupe_dict1[key][2][ele][0])
                            if type(class_tupe_dict1[key][2][ele][1]) == type(1):
                                temp = []
                                temp.append(class_tupe_dict1[key][2][ele][1])
                                class_tupe_dict1[key][2][ele][1] = tuple(temp)
                            temp2.append(class_tupe_dict1[key][2][ele][1])
                            temp3 = list(match_products_x_y[ele][0])
                            # temp4 = match_products_x_y[ele][1]
                            # temp3.append(match_products_x_y[ele][0])
                            temp4.append(match_products_x_y[ele][1])
                            if list(set(temp1) ^ set(temp3)) == []:
                                # if np.mean(class_tupe_dict1[key][2][ele][1]) == np.mean(match_products_x_y[ele][1]):
                                if list(set(temp2[0]) ^ set(temp4[0])) == []:
                                    # print(ele + ' ok')
                                    check_res[key] = True
                                else:
                                    check_res[key] = False
                                    # print(ele + ' not ok')
                                    size_res = [ele, 'not ok']
                                    csv_writer.writerow(size_res)
                            else:
                                # print(ele + ' not ok')
                                size_res = [ele, 'not ok']
                                csv_writer.writerow(size_res)

                else:
                    # print(key + ' is not complete for the product name! --short of '+ str(diff_pos))
                    res_list = [key,'缺少']
                    res_list.append(diff_pos)
                    csv_writer.writerow(res_list)
                    check_res[key] = False
                if diff_neg !=[]:
                    # print(key + ' has more products than expected!')
                    res_list = [key, '多出了']
                    res_list.append(diff_neg)
                    csv_writer.writerow(res_list)
        # print('check_results:' + str(check_res))
    except Exception as e:
        exception.append(e)
        return exception


def modify_element(file_name, zone=None):
    all_data = pd.read_excel(file_name, sheetname=None, header=0)
    zone_data = all_data[class_tupe_dict[zone.__class__.__name__][0]]
    for ele in zone.ele_list:
        id_to_add = ''
        if isinstance(ele, class_tupe_dict[zone.__class__.__name__][1]):
            ele_wid = ele.backline.seg.length
            ele_len = ele.len
            # match_results = zone_data.loc[(zone_data.X == ele_wid ) & (zone_data.Y == ele_len)]
            match_ele = zone_data.loc[ele.name == zone_data.loc[:, HEADTAG[2]]]
            if not match_ele.empty:
                if list(match_ele[HEADTAG[4]])[0] == -1 or list(match_ele[HEADTAG[5]])[0] == -1:
                    str1 = list(match_ele.loc[:, HEADTAG[0]])
                    str2 = list(match_ele.loc[:, HEADTAG[1]])
                    id_to_add = list(list(zip(str1, str2))[0])
                    id_to_add = '_'.join(id_to_add)
                else:
                    match_results = match_ele.loc[(zone_data[HEADTAG[4]] == ele_wid) &
                                                  (zone_data[HEADTAG[5]] == ele_len)]
                    if not match_results.empty:
                        str1 = list(match_results.loc[:, HEADTAG[0]])
                        str2 = list(match_results.loc[:, HEADTAG[1]])
                        id_to_add = list(list(zip(str1, str2))[0])
                        id_to_add = '_'.join(id_to_add)
            if id_to_add == '':
                id_to_add = '-1'
            ele.ID = id_to_add

            # else:
            #     ele.ID = -1
    return zone


def read_o1_xml_to_house(fname1, dataset=DATASET):
    xml = etree.parse(fname1)
    exception = []
    root = xml.getroot()
    flp_nd = [n for n in root.getchildren() if n.tag == House.__name__][0] \
        .getchildren()[0]
    scale = root.getchildren()[1].attrib['scale']
    ##################add by jxh######
    flp_nd_new = set_id_and_its_brother(flp_nd.getchildren())

    ##################################
    room_dict0 = {n.get(TAG): n for n in flp_nd_new}
    # room_dict0 = {n.get(TAG):n for n in flp_nd.getchildren()}
    room_dict1 = {}

    flp = FloorPlan()
    flp.set_boundary(get_boundary(flp_nd))

    for key, node in room_dict0.items():
        zone = get_functional_zone(node, flp, key)
        room_dict1[key] = zone
        if not isinstance(zone, AutoLayout.unknow.Base.UnKnown) and \
                        node.get(PARENT_TAG) is None:
            try:
                zone.run()
            except Exception as e:
                exception.append(e)
            zone = modify_element(dataset, zone)
            flp.add_region(zone)

    for key, node in room_dict0.items():
        if node.get(PARENT_TAG) is None:
            continue

        zone = build_room(node, room_dict1, room_dict0)
        if zone:
            try:
                zone.run()
                # print(zone)
                # modify_element(zone)
            except Exception as e:
                exception.append(e)
            flp.add_region(zone)

    house = House()
    house.add_floorplan(flp)
    return house, exception, scale


def read_o1_xml_to_house_anno(fname1):
    xml = etree.parse(fname1)
    exception = []
    root = xml.getroot()
    flp_nd = [n for n in root.getchildren() if n.tag == House.__name__][0] \
        .getchildren()[0]
    scale = root.getchildren()[1].attrib['scale']
    ##################add by jxh######
    flp_nd_new = set_id_and_its_brother(flp_nd.getchildren())

    ##################################
    room_dict0 = {n.get(TAG): n for n in flp_nd_new}
    # room_dict0 = {n.get(TAG):n for n in flp_nd.getchildren()}
    room_dict1 = {}

    flp = FloorPlan()
    flp.set_boundary(get_boundary(flp_nd))

    for key, node in room_dict0.items():
        zone = get_functional_zone(node, flp, key)
        room_dict1[key] = zone
        # if not isinstance(zone, unknow.Base.Unknow) and \
        #     node.get(PARENT_TAG) is None:
        #     try:
        #         zone.run()
        #     except Exception as e:
        #         exception.append(e)
        #     zone = modify_element(dataset, zone)
        #     flp.add_region(zone)
        flp.add_region(zone)

    for key, node in room_dict0.items():
        if node.get(PARENT_TAG) is None:
            continue

        zone = build_room(node, room_dict1, room_dict0)
        if zone:
            try:
                zone.run()
                # print(zone)
                # modify_element(zone)
            except Exception as e:
                exception.append(e)
            flp.add_region(zone)

    house = House()
    house.add_floorplan(flp)
    return house, exception, scale


def save_house_to_xml_o1(house, file_name):
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
            child1.set("tag", reg.uuid)
            child1.set("boundary", reg.boundary.to_string())

            child_temp = etree.SubElement(child1, FLOOR_TAG)
            child_temp.set("ID", str(reg.floor_id))
            child_temp = etree.SubElement(child1, SKIRTINGLINE_TAG)
            child_temp.set("ID", str(reg.skirting_line_id))
            child_temp = etree.SubElement(child1, PLASTERLINE_TAG)
            child_temp.set("ID", str(reg.plaster_line_id))
            for e in reg.ele_list:
                if e.is_multiple:
                    for ee in e.ele_list:
                        child3 = etree.SubElement(child1, ee.__class__.__name__)
                        child3.set("name", ee.name)
                        child3.set("boundary", ee.boundary.to_string())
                        child3.set("backline", ee.backline.to_string())
                        child3.set("position", ee.get_xyz_str())
                        child3.set("angle", str(ee.angle))
                        child3.set("ID", str(ee.ID))
                        child3.set("back_len", str(ee.backline.seg.length))
                        child3.set("front_len", str(ee.len))
                else:
                    child2 = etree.SubElement(child1, e.__class__.__name__)
                    child2.set("name", e.name)
                    child2.set("boundary", e.boundary.to_string())
                    child2.set("backline", e.backline.to_string())
                    # child2.set("position", str(e.backline.p1).split('D')[1])
                    child2.set("position", e.get_xyz_str())
                    child2.set("angle", str(e.angle))
                    child2.set("ID", str(e.ID))
                    child2.set("back_len", str(e.backline.seg.length))
                    child2.set("front_len", str(e.len))
                if e.__class__.__name__ == 'Door':
                    if e.door_body is not None:
                        child2.set("body", e.door_body.to_string())
                        child2.set("front_len", str(e.door_body.seg.length))

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


def run_o1_xml(input, output):
    """
    读取元一xml格式，自动布置软硬装，并存储在output中.
    返回异常e时，以防未知问题。
    """
    exception = []
    try:
        house, exception, _ = read_o1_xml_to_house(input)
        # house.draw()
        # helpers.save_house_to_xml(house, output)
        save_house_to_xml_o1(house, output)
        return exception
    except Exception as e:
        exception.append(e)
        return exception
def main():
    print('hi')
    file1 = r'F:\20180112new_bk.xml'
    house, exceptiion, _ = read_o1_xml_to_house(file1)
    # house.draw(r'E:\f.png')
    house.draw()
    save_xml_name = 'E:\\f.xml'
    save_house_to_xml_o1(house, save_xml_name)
    # run_o1_xml(file1, save_xml_name)


if __name__ == "__main__":
    # main()
    check_dataset()
