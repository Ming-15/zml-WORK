import matplotlib
# matplotlib.use('Agg') # 不显示画图, 编译exe时候必须使用
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
import sys
import os
import shutil
import time
import AutoLayout.settings
import AutoLayout.DY_Line as DY_Line
import AutoLayout.CommonElement as CommonElement

from AutoLayout.helpers import *
from AutoLayout.main_o1 import *
import AutoLayout.main_bedroom.Base
import AutoLayout.livingroom.Base
import AutoLayout.bedroom.Base
import AutoLayout.tatami_room.Base
import AutoLayout.dining_room.Base
import AutoLayout.CommonElement
import AutoLayout.kitchen.Base
import AutoLayout.bathroom.Base
import AutoLayout.porch.Base
import AutoLayout.balcony.Base
import AutoLayout.schoolroom.Base
import AutoLayout.storeroom.Base
import AutoLayout.washroom.Base
import AutoLayout.living_dining_room.Base
import AutoLayout.hallway.Base
import AutoLayout.eldersroom.Base
import AutoLayout.cloakroom.Base
import AutoLayout.childrenroom.Base

import AutoLayout.main_bedroom.test
import AutoLayout.livingroom.test
import AutoLayout.kitchen.test

region_list = [AutoLayout.schoolroom.Base.Schoolroom.__name__, AutoLayout.storeroom.Base.Storeroom.__name__,
               AutoLayout.washroom.Base.Washroom.__name__, AutoLayout.living_dining_room.Base.LivingDiningRoom.__name__,
               AutoLayout.hallway.Base.Hallway.__name__, AutoLayout.eldersroom.Base.Eldersroom.__name__,
               AutoLayout.cloakroom.Base.Cloakroom.__name__, AutoLayout.childrenroom.Base.Childrenroom.__name__]

def read_xml_to_house(filename):
    time_str = time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))
    is_error = False

    xml = etree.parse(filename)
    root = xml.getroot()
    # if root.tag != House.__name__:
    #     raise Exception('error:xml文件根节点出错')

    house_node = [n for n in root.getchildren() if n.tag == House.__name__]

    house = House()
    for node in house_node[0].getchildren():
        if node.tag != FloorPlan.__name__:
            raise Exception('error:xml文件子节点出错')
        fp = FloorPlan()
        for k in node.keys():
            xml_set_boundary(k, fp, node)
        # 读取主卧相关参数
        for node1 in node.getchildren():
            if node1.tag == AutoLayout.main_bedroom.Base.MainBedroom.__name__:
                mainbedroom = AutoLayout.main_bedroom.Base.MainBedroom()
                # 读取边界
                for k in node1.keys():
                    xml_set_boundary(k, mainbedroom, node1)

                for node2 in node1.getchildren():
                    # 读取窗
                    if node2.tag == DY_Line.Window.__name__:
                        # for key in node2.keys():
                        #     if key == DY_Line.Window.name:
                        # if "backline" not in node2.keys():
                        #     raise Exception('error:门必须有backline')
                        xml_set_window(mainbedroom, node2)
                    # 读取门
                    if node2.tag == CommonElement.Door.__name__:
                        door = CommonElement.Door()
                        if "backline" not in node2.keys():
                            raise Exception('error:门必须有backline')
                        xml_set_door(door, node2)
                        # for key in node2.keys():
                        #     xml_set_boundary(key, door, node2)
                        #     xml_set_backline(key, door, node2)
                        #     xml_set_door_body(key, door, node2)
                        mainbedroom.add_door(door)
                try:
                    mainbedroom.run()
                    pass
                except Exception as e:
                    error_log(e, time_str)
                    get_error_replica(filename, time_str)
                fp.add_region(mainbedroom)

            # 读取客厅
            if node1.tag == AutoLayout.livingroom.Base.Livingroom.__name__:
                liv_room = AutoLayout.livingroom.Base.Livingroom()
                # 读取边界
                for k in node1.keys():
                    xml_set_boundary(k, liv_room, node1)
                # for k in node1.keys():
                #     xml_set_backline(k, liv_room, node1)
                for node2 in node1.getchildren():
                    #读取窗
                    if node2.tag == DY_Line.Window.__name__:
                        # for key in node2.keys():
                        #     if key == DY_Line.Window.name:
                        xml_set_window(liv_room, node2)
                    #读取门
                    if node2.tag == CommonElement.Door.__name__:
                        door = CommonElement.Door()
                        assert "backline" in node2.keys(), "门必须有backline"
                        xml_set_door(door, node2)
                        # for key in node2.keys():
                        #     xml_set_boundary(key, door, node2)
                        #     xml_set_backline(key, door, node2)
                        #     xml_set_door_body(key, door, node2)
                        liv_room.add_door(door)
                        #读取虚边界
                    if node2.tag == DY_Line.Border.__name__:
                        for key in node2.keys():
                            if key == DY_Line.Border.name:
                                xml_set_border(key, liv_room, node2)
                try:
                    liv_room.run()
                except Exception as e:
                    error_log(e, time_str)
                    get_error_replica(filename, time_str)
                fp.add_region(liv_room)
            # 读取次卧
            if node1.tag == AutoLayout.bedroom.Base.Bedroom.__name__:
                att = 'attribute'
                if node1.get(att) is None:
                    bed_room = AutoLayout.bedroom.Base.Bedroom()
                else:
                    if node1.get(att) == settings.BEDROOM_TYPE[0]:
                        bed_room = AutoLayout.bedroom.Base.Bedroom()
                    elif node1.get(att) == settings.BEDROOM_TYPE[1]:
                        bed_room = AutoLayout.tatami_room.Base.TatamiRoom()

                # 读取边界
                for k in node1.keys():
                    xml_set_boundary(k, bed_room, node1)

                for node2 in node1.getchildren():
                    # 读取窗户
                    if node2.tag == DY_Line.Window.__name__:
                        # for key in node2.keys():
                        #     if key == DY_Line.Window.name:
                        xml_set_window(bed_room, node2)
                    # 读取门
                    if node2.tag == CommonElement.Door.__name__:
                        door = CommonElement.Door()
                        assert "backline" in node2.keys(), "门必须有backline"
                        xml_set_door(door, node2)
                        # for key in node2.keys():
                        #     xml_set_boundary(key, door, node2)
                        #     xml_set_backline(key, door, node2)
                        #     xml_set_door_body(key, door, node2)
                        bed_room.add_door(door)
                try:
                    bed_room.run()
                    pass
                except Exception as e:
                    error_log(e, time_str)
                    get_error_replica(filename, time_str)
                fp.add_region(bed_room)

            # 读取餐厅
            if node1.tag == AutoLayout.dining_room.Base.DiningRoom.__name__:
                diningroom = AutoLayout.dining_room.Base.DiningRoom()
                # 读取边界
                for k in node1.keys():
                    xml_set_boundary(k, diningroom, node1)
                # for k in node1.keys():
                #     xml_set_backline(k, diningroom, node1)

                for node2 in node1.getchildren():
                    # 读取窗户
                    if node2.tag == DY_Line.Window.__name__:
                        # for key in node2.keys():
                        #     if key == DY_Line.Window.name:
                        xml_set_window(diningroom, node2)
                    # 读取门
                    if node2.tag == CommonElement.Door.__name__:
                        door = CommonElement.Door()
                        assert "backline" in node2.keys(), "门必须有backline"
                        xml_set_door(door, node2)
                        # for key in node2.keys():
                        #     xml_set_boundary(key, door, node2)
                        #     xml_set_backline(key, door, node2)
                        #     xml_set_door_body(key, door, node2)
                        diningroom.add_door(door)
                    # 读取虚边界
                    if node2.tag == DY_Line.Border.__name__:
                        for key in node2.keys():
                            if key == DY_Line.Border.name:
                                xml_set_border(key, diningroom, node2)
                try:
                    diningroom.run()
                    pass
                except Exception as e:
                    error_log(e, time_str)
                    get_error_replica(filename, time_str)
                # diningroom.draw()
                fp.add_region(diningroom)

            if node1.tag == AutoLayout.kitchen.Base.Kitchen.__name__:
                ktch = AutoLayout.kitchen.Base.Kitchen()
                for k in node1.keys():
                    xml_set_boundary(k, ktch, node1)
                for node2 in node1.getchildren():
                    if node2.tag == DY_Line.Window.__name__:
                        # for key in node2.keys():
                        #     if key == DY_Line.Window.name:
                        xml_set_window(ktch, node2)
                    if node2.tag == CommonElement.Door.__name__:
                        door = CommonElement.Door()
                        xml_set_door(door, node2)
                        door.set_connect_list(node2.get('connect').split(';')[0],
                                              node2.get('connect').split(';')[1])
                        ktch.add_door(door)
                    if node2.tag == DY_Line.Border.__name__:
                        for key in node2.keys():
                            if key == DY_Line.Border.name:
                                xml_set_border(key, ktch, node2)
                try:
                    ktch.run()
                    # pass
                except Exception as e:
                    error_log(e, time_str)
                    get_error_replica(filename, time_str)
                fp.add_region(ktch)
            #读取卫生间
            if node1.tag == AutoLayout.bathroom.Base.Bathroom.__name__:
                bthr = AutoLayout.bathroom.Base.Bathroom()
                for k in node1.keys():
                    xml_set_boundary(k, bthr, node1)
                for node2 in node1.getchildren():
                    if node2.tag == DY_Line.Window.__name__:
                        # for key in node2.keys():
                        #     if key == DY_Line.Window.name:
                        xml_set_window(bthr, node2)
                    if node2.tag == CommonElement.Door.__name__:
                        door = CommonElement.Door()
                        xml_set_door(door, node2)
                        bthr.add_door(door)
                    if node2.tag == DY_Line.Border.__name__:
                        for key in node2.keys():
                            if key == DY_Line.Border.name:
                                xml_set_border(key, bthr, node2)
                try:
                    bthr.run()
                    pass
                except Exception as e:
                    error_log(e, time_str)
                    get_error_replica(filename, time_str)
                fp.add_region(bthr)
            #读取过道
            if node1.tag == AutoLayout.porch.Base.Porch.__name__:
                prch = AutoLayout.porch.Base.Porch()
                for k in node1.keys():
                    xml_set_boundary(k, prch, node1)
                for node2 in node1.getchildren():
                    if node2.tag == DY_Line.Window.__name__:
                        # for key in node2.keys():
                        #     if key == DY_Line.Window.name:
                        xml_set_window(prch, node2)
                    if node2.tag == CommonElement.Door.__name__:
                        door = CommonElement.Door()
                        xml_set_door(door, node2)
                        prch.add_door(door)
                    if node2.tag == DY_Line.Border.__name__:
                        for key in node2.keys():
                            if key == DY_Line.Border.name:
                                xml_set_border(key, prch, node2)
                try:
                    prch.run()
                    pass
                except Exception as e:
                    error_log(e, time_str)
                    get_error_replica(filename, time_str)
                fp.add_region(prch)
            #读取阳台
            if node1.tag == AutoLayout.balcony.Base.Balcony.__name__:
                bal = AutoLayout.balcony.Base.Balcony()
                for k in node1.keys():
                    xml_set_boundary(k, bal, node1)
                for node2 in node1.getchildren():
                    if node2.tag == DY_Line.Window.__name__:
                        # for key in node2.keys():
                        #     if key == DY_Line.Window.name:
                        xml_set_window(bal, node2)
                    if node2.tag == CommonElement.Door.__name__:
                        door = CommonElement.Door()
                        xml_set_door(door, node2)
                        prch.add_door(door)
                    if node2.tag == DY_Line.Border.__name__:
                        for key in node2.keys():
                            if key == DY_Line.Border.name:
                                xml_set_border(key, bal, node2)
                try:
                    bal.run()
                    pass
                except Exception as e:
                    error_log(e, time_str)
                    get_error_replica(filename, time_str)
                fp.add_region(bal)

        house.add_floorplan(fp)

    return house

def test():
    assert  os.path.exists('test'), "不存在test文件夹"
    # file = 'test/'
    # file = r'D:\exe\test\\'
    file = r'E:\floorplandataset\data_set'
    scale_list = []
    if os.path.exists('finish_xml') is False:
        os.mkdir('finish_xml')
    else:
        shutil.rmtree('finish_xml')
        os.mkdir('finish_xml')
    def ana_dir_xml(dir, finish_dir=None, jpg_dir=None ):
        xml_file = listfile(dir, postfix='xml')

        for item in xml_file:
            print('开始分析: %s' % (item), end='\n')
            house, _, scale = read_o1_xml_to_house(dir + '/' + item)
            scale_list.append(scale)
            with open(file + '/' + '_scale.txt','w+') as f:
                f.write('\n'.join(scale_list))
                f.close()
            # house = read_xml_to_house(dir + '/' + item)
            save_name = finish_dir + item[:-4] + '_finish.xml'
            save_house_to_xml_o1(house, save_name)
            save_name = jpg_dir + item[:-4] + '.jpg'
            house.draw(save_name)

    sub_files = os.listdir(file)
    ana_dir_xml(file, 'finish_xml/', 'finish_xml/')
    for item in sub_files:
        if os.path.isdir(file + item):
            jpg_dir = 'finish_xml' + '/' + item + '_jpg/'
            os.mkdir('finish_xml' + '/' + item)
            os.mkdir(jpg_dir)
            ana_dir_xml(file + item, finish_dir='finish_xml' + '/' + item + '/', jpg_dir=jpg_dir)
        if os.path.isfile(file + item):
            pass

def main(file):
    # file = "test/floor_plan.xml"
    # file = "F:/test.xml"
    # file = r'C:\Users\Administrator\Desktop\201801045.xml'
    # file = r'test/livingroom.xml'
    time_str = time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))
    # try:
    #     house = read_xml_to_house(file)
    #     # house = read_xml_to_house(r"test/floor_plan.xml")
    #     house.draw()
    # except Exception as e:
    #     error_log(e, time_str)
    house = read_xml_to_house(file)
    house.draw()

    # house = read_xml_to_house(argv[1])
    # save_xml_name = argv[1][:-3] + "_finish.xml"
    save_xml_name = 'E:\\f.xml'
    save_house_to_xml(house, save_xml_name)

if __name__ == "__main__":
    # test()
    main(r'E:\floorplandataset\data_set\lianjia_chaoyang_juntanghaoyuan_001.xml')
    # main(r'test\kitchen.xml')
    # main(r'E:\jxh\subtasks\zhuc\20180109.xml')
    # read_o1_xml_to_house(r'C:\Users\zhuc\Desktop\20180104_zhuc.xml')
    # main(r'E:\jxh\subtasks\AutoLayoutTest\kitch_test\36.xml')
    # import bedroom.test
    # bedroom.test.test_411(3000, 3000, 0, 500, 1000, 1)
    # livingroom.test.batch_test()
