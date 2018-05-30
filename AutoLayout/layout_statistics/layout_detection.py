# —*— coding: utf-8 _*_
__author__ = 'jxh'

from lxml import etree
from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
from sympy.geometry import Polygon
import os


from AutoLayout.BaseClass import House

check_list = ['Floor', 'SkirtingLine', 'PlasterLine', 'Door', 'Border', 'Window']


def batch_process(dir_path, output, f):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    def ana_dir_xml(dir_path, output, f):
        xml_files = listfile(dir_path, postfix='xml')
        path = dir_path + '/'
        for file in xml_files:
            print('Analysis file: %s done!' % (file), end='\n')
            read_xml_to_get_statistics(path + file, output, f)

    ana_dir_xml(dir_path, output, f)


def get_final_results(input, output):
    res = {}
    save_dic = []
    with open(input, 'r') as fin:
        for line in fin.readlines():
            res[line.split(':')[0]] = res.get(line.split(':')[0], 0) + 1
    fin.close()
    with open(output, 'w+') as fout:
        final_res = list(res.items())
        for item in final_res:
            str_to_save = str(item[0]) + ':' + str(item[1]) + '\n'
            save_dic.append(str_to_save)
        fout.write(''.join(save_dic))
    tmp = 0
    fout.close()


def read_xml_to_get_statistics(input, output, f):
    xml = etree.parse(input)
    root = xml.getroot()
    flp_nd = [n for n in root.getchildren() if n.tag == House.__name__][0] \
        .getchildren()[0]
    room_list = flp_nd.getchildren()
    room_dict = {room: room.getchildren() for room in room_list}

    for key, node in room_dict.items():
        res = {}
        for n in node:
            res[n.tag] = res.get(n.tag, 0) + 1  # get ele and its cnt

        boundary_points = get_point_num(key)
        boundary_vertices = get_vertices(key)
        x_max = sorted(boundary_points)[-1][0] - sorted(boundary_points)[0][0]
        y_max = sorted(boundary_points)[-1][1] - sorted(boundary_points)[0][1]

        if len(res.keys()) <= len(check_list):
            room_fail = []

            statis = str(key.tag) + '(failed):' + '(floorplan_size(x,y)' + str(x_max) + '&' + str(y_max) + ')[' + \
                     str(len(boundary_vertices)) + str(res.get('Door', 0)) + str(res.get('Window', 0)) + \
                     str(res.get('Border', 0)) + '](顶点，门，窗，边界)' + os.path.basename(input) + '\n'
            room_fail.append(statis)
            f.write(''.join(room_fail))

        else:
            room_succeed = []
            statis = str(key.tag) + '(succeed):[' + str(len(boundary_vertices)) + str(res.get('Door', 0)) + \
                     str(res.get('Window', 0)) + str(res.get('Border', 0)) + '](顶点，门，窗，边界)' + \
                     os.path.basename(input) + '\n'
            room_succeed.append(statis)
            f.write(''.join(room_succeed))


def get_point_num(node):
    key = "boundary"
    if node.get(key) == None:
        return None
    p_str_list = node.get(key).split(';')
    p_list = []
    for p_str in p_str_list:
        if p_str == '':
            continue
        list0 = p_str[1:-1].split(',')
        pt = (int(list0[0]), int(list0[1]))
        p_list.append(pt)
    return p_list

def get_vertices(node):
    key = "boundary"
    if node.get(key) == None:
        return None
    p_str_list = node.get(key).split(';')
    p_list = []
    for p_str in p_str_list:
        if p_str == '':
            continue
        list0 = p_str[1:-1].split(',')
        pt = (int(list0[0]), int(list0[1]))
        p_list.append(pt)
    vertice_num = Polygon(*p_list)
    return vertice_num.vertices

def point_to_string(p):
    return str(p).split('D')[1]


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


if __name__ == "__main__":
    dir_path = r'E:\jxh\git\2018020901\finish_xml'
    # file = r'E:\jxh\git\2018020901\finish_xml\lianjia_chaoyang_baolixiangbinhuayuan_009_finish.xml'
    output = r'E:\jxh\subtasks'
    f = open(output + '/' + 'statis.txt', 'w+')
    # read_xml_to_get_statistics(file, output, f)
    batch_process(dir_path, output, f)
    f.close()
    input = r'E:\jxh\subtasks\statis.txt'
    output = r'E:\jxh\subtasks\statis_final.txt'
    get_final_results(input, output)
