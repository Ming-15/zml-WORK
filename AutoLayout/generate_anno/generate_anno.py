# —*— coding: utf-8 _*_
import cv2
import matplotlib.patches as patches
import matplotlib.pylab as plt

import main_o1
import numpy as np

import os
from os import listdir

import main_o1

BASE_PT = {"O1": ('center', (0, 0)), "DIM": ('leftup', (0, 0))}
# house_node = [n for n in root.getchildren() if n.tag == House.__name__]
# SCALE = 22.10  # mm per pixel

def gen_train_data(xml_file, img_file, base='O1', savename='f.png',
                   show_door_window = False, show_edge = False, save_edge = False ):
    house, _, SCALE = main_o1.read_o1_xml_to_house_anno(xml_file)
    # img = cv2.imread(img_file)
    img = cv2.imdecode(np.fromfile(img_file, dtype=np.uint8), -1)
    img_h, img_w, _ = img.shape
    xlim, ylim = [], []
    if base == 'O1':
        xlim = [-img_w/2 * float(SCALE), img_w/2 * float(SCALE)]
        ylim = [-img_h/2 * float(SCALE), img_h/2 * float(SCALE)]
    else:
        pass

    figure, ax = plt.subplots()
    pt_floorplan = house.floor_list[0].boundary.polygon.vertices
    ax.add_patch(patches.Polygon(pt_floorplan, True, color='#000000'))
    pt_door = ''
    tmp_point = []
    num = len(house.floor_list[0].region_list)
    for i in range(num):
        pt_floorplan_room = house.floor_list[0].region_list[i].boundary.polygon.vertices
        ax.add_patch(patches.Polygon(pt_floorplan_room, True, color='#FFFFFF'))
        
        door_num = house.floor_list[0].region_list[i].doors
        for j in range(door_num):
            pt_floorplan_door = house.floor_list[0].region_list[i].ele_list[j].boundary.polygon.vertices
            if show_door_window == True:
                ax.add_patch(patches.Polygon(pt_floorplan_door, True, color='#888888'))
            else:
                pass
            if pt_floorplan_door[1] not in tmp_point:
                p_door = str(img_file) + "," + str(img_w/2 + pt_floorplan_door[1].x/float(SCALE)) + "," + str(img_h/2 - pt_floorplan_door[1].y/float(SCALE)) + "," + \
                      str(img_w/2 + pt_floorplan_door[3].x/float(SCALE)) + "," + str(img_h/2 - pt_floorplan_door[3].y/float(SCALE)) + "," + "Door" + '\n'
                pt_door += p_door
                tmp_point.append(pt_floorplan_door[1])
            
        win_num = house.floor_list[0].region_list[i].windows
        for l in range(win_num):
            pt_floorplan_win = house.floor_list[0].region_list[i].line_list[l].boundary.polygon.vertices
            if show_door_window == True:
                ax.add_patch(patches.Polygon(pt_floorplan_win, True, color='#f46e42'))
            else:
                pass

    ax.set_aspect(1)
    ax.set_xticks([])
    ax.set_yticks([])

    plt.axis('off')
    plt.xlim(xlim[0], xlim[1])
    plt.ylim(ylim[0], ylim[1])
    if show_edge == True:
        plt.show()
    else:
        pass
    figure.tight_layout(renderer=None, pad=0)
    figure.set_size_inches(img_w/figure.dpi, img_h/figure.dpi)
    
    if save_edge == True:
        plt.savefig(savename)
    else:
        pass
    # plt.savefig(savename, bbox_inches='tight', dpi=DPI)
    #plt.savefig(savename, bbox_inches='tight', pad_inches=0, dpi=DPI)
    return str(pt_door)

def compare_images(fname1, fname2):
    # img1 = cv2.imdecode(np.fromfile(fname1, dtype=np.uint8), -1)
    # img2 = cv2.imdecode(np.fromfile(fname2, dtype=np.uint8), -1)
    img1 = cv2.imread(fname1)
    img2 = cv2.imread(fname2)
    w, h, _ = img1.shape
    img2 = cv2.resize(img2, (h, w))
    imge_mix1 = cv2.addWeighted(img1, 0.4, img2, 0.6, 1)
    cv2.imshow('image_mix1', imge_mix1)
    cv2.waitKey()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    filepath = '../test/floor_plan_list/'
    filename_list = listdir(filepath)
    savefile = filepath + 'label.txt'
    savefiletxt = []
    #是否显示门窗
    show_door_window = False
    #是否显示混合图
    show_mix = False
    #是否显示边界
    show_edge = False
    #是否保存边界图
    save_edge = True
    # 将数据写入训练文档中
    with open(savefile, "w") as f:
        for filename in filename_list:
            if filename[-3:] == 'png':
                sfile = filepath + 'boundary/' +filename
                # img_file.append(filename)
                img_file = filepath + filename
                xml_file = filepath + os.path.splitext(filename)[0] + '.xml'
                print("processing: " + os.path.splitext(filename)[0])
                savefiletxt = gen_train_data(xml_file, img_file, savename=sfile,
                                             show_door_window = False, show_edge = False, save_edge = True)
                f.write(savefiletxt)
                if show_mix == True:
                    compare_images(img_file, sfile)
                else:
                    pass

