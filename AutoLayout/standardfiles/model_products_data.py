# —*— coding: utf-8 _*_
from AutoLayout.bathroom.settings import *
from AutoLayout.bedroom.settings import *
from AutoLayout.dining_room.settings import *
from AutoLayout.kitchen.settings import *
from AutoLayout.livingroom.settings import *
from AutoLayout.main_bedroom.settings import *

# 模型数据的初步参考标准-分类数据
CLASSIFIER_DATA = {'主卧产品名称': ['床', '附属品', '屉柜', '床头柜', '衣柜', '躺椅', '窗帘', '写字桌', '单椅'],
                   '客房产品名称': ['床', '附属品', '屉柜', '床头柜', '衣柜', '窗帘', '单椅'],
                   '榻榻米产品名称': ['书柜', '附属品', '平板床榻榻米', '平板床榻榻米衣柜', '平板床榻榻米书柜',
                               '衣柜', '桌椅组合', '椅子'],
                   '客厅产品名称': ['一字沙发', '附属品', '长方形茶几', '正方形茶几', '圆形茶几', '电视柜', '躺椅',
                                 '边几', '左转角L型沙发(面对)', '右转角L型沙发(面对)', '窗帘', '地毯'],
                   '厨房产品名称': ['冰箱', '附属品', '烟机柜', '水槽柜', '左转角地柜(面对)', '右转角地柜(面对)',
                              '调节板', '单开门地柜','双开门地柜', '抽屉地柜', '拉篮', '烟机吊柜', '单开门吊柜',
                              '双开门吊柜', '吊柜调节板', '右转角吊柜(面对)', '窗帘'],
                   '餐厅产品名称': ['餐边柜', '附属品', '圆餐桌', '方餐桌', '餐椅', '窗帘'],
                   '卫生间产品名称': ['面盆', '附属品', '坐便器', '淋浴房', '花洒', '洗衣机', '窗帘'],
                   '儿童房产品名称':[],
                   '过道产品名称': [],
                   '阳台产品名称': [],
                   '产品类别': ['床榻类', '柜架类', '桌几类', '椅凳类', '附属类', '沙发类', '洁具五金类', '窗饰类']
                   }

# 主卧产品信息对应表
MAIN_BED = {
    '床': [MAINBED_BED_LEN, MAINBED_BED_WIDTH], '附属品': [], '屉柜': [DRAWER_LEN, DRAWER_WIDTH],
    '床头柜': [BEDSIDE_NIGHTTABLE_LEN, BEDSIDE_NIGHTTABLE_WIDTH], '衣柜': [CLOSET_LEN, CLOSET_WIDTH],
    '躺椅': [RECLINERS_WIDTH_LEN], '窗帘': [CURTAIN_LEN, (-1,)], '写字桌': [WRITING_DESK_LEN, WRITING_DESK_WIDTH],
    '单椅': [CHAIR_LEN, CHAIR_WIDTH]
}
# 客房产品信息对应表
GUEST = {
    '床': [BED_LEN, BED_WIDTH], '附属品': [], '屉柜': [DRAWER_LEN, DRAWER_WIDTH],
    '床头柜': [BEDSIDE_NIGHTTABLE_LEN, BEDSIDE_NIGHTTABLE_WIDTH], '衣柜': [CLOSET_LEN, CLOSET_WIDTH],
    '躺椅': [RECLINERS_WIDTH_LEN], '窗帘': [CURTAIN_LEN, (-1,)], '写字桌': [WRITING_DESK_LEN, WRITING_DESK_WIDTH],
    '单椅': [CHAIR_LEN, CHAIR_WIDTH]
}
# 榻榻米产品信息对应表
TATAMI = {
    '书柜': [], '附属品': [], '平板床榻榻米': [], '衣柜': []
}
# 客厅产品信息对应表
LIVING = {
    '一字沙发': [SOFA1_LEN, SOFA1_WIDTH], '附属品': [], '长方形茶几': [REC_TEA_WIDTH_LEN],
    '正方形茶几': [SQUARE_TEA_WIDTH_LEN], '圆形茶几': [CIRCLE_TEA_WIDTH_LEN],
    '电视柜': [LIVINGROOM_TV_BENCH_LEN, LIVINGROOM_TV_BENCH_WIDTH], '躺椅': [RECLINERS_WIDTH_LEN],
    '边几': [SIDE_TABLE_LEN, SIDE_TABLE_WIDTH], '左转角L型沙发(面对)': [SOFAL_L1_L2],
    '右转角L型沙发(面对)': [SOFAL_L1_L2], '窗帘':[CURTAIN_LEN, (-1,)], '地毯':[]
}
# 厨房产品信息对应表
KITCHEN = {
    '冰箱': [CABINET_L, REFRIGERATOR_W], '附属品': [], '烟机柜': [CABINET_L, RANGEHOOD_SINK_W],
    '水槽柜': [CABINET_L, RANGEHOOD_SINK_W], '左转角地柜(面对)': [CABINET_L, BASE_CORNER_W],
    '右转角地柜(面对)': [CABINET_L, BASE_CORNER_W], '调节板': [CABINET_L, ADJUSTING_PANEL_MAX],
    '单开门地柜': [CABINET_L, SINGLE_CABINET_W], '双开门地柜': [CABINET_L, SINGLE_CABINET_W_D],
    '抽屉地柜': [CABINET_L, SINGLE_CABINET_W], '拉篮': [CABINET_L, PULL_BASKET_W],
    '烟机吊柜': [HANGING_CABINET_L, RANGEHOOD_SINK_W], '单开门吊柜': [HANGING_CABINET_L, HANGING_CABINET_W],
    '双开门吊柜': [HANGING_CABINET_L, HANGING_CABINET_W_D],
    '吊柜调节板': [HANGING_CABINET_L, HANGING_ADJUSTING_PANEL_MAX],
    '右转角吊柜(面对)': [HANGING_CABINET_L, HANGING_BASE_CORNER_LW], '窗帘':[CURTAIN_LEN, (-1,)]
}
# 餐厅产品信息对应表
DINNING = {
    '餐边柜': [SIDEBOARD_CABINET_WIDTH, SIDEBOARD_CABINET_LEN], '附属品': [],
    '圆餐桌': [ROUND_DININD_TABLE_4_RADIUS + ROUND_DININD_TABLE_6_RADIUS],
    '方餐桌': [SQUARE_DININD_TABLE_4_WIDTH, SQUARE_DININD_TABLE_4_LEN + SQUARE_DININD_TABLE_6_LEN],
    '餐椅': [DINING_CHAIR],  '窗帘':[CURTAIN_LEN, (-1,)]
}
# 卫生间产品信息对应表
BATH = {
    '面盆': [WASHBASIN_L, WASHBASIN_W], '附属品': [], '坐便器': [TOILET_DEV_L, TOILET_DEV_W],
    '淋浴房': [SHOWER_L, SHOWER_W],'花洒': [SPRAY_L, SPRAY_W], '洗衣机': [WAHING_MAC_L, WAHING_MAC_W],
    '窗帘':[CURTAIN_LEN, (-1,)]
}
# 过道产品信息对应表
PORCH = {}
# 阳台产品信息对应表
BALCONY = {}
#儿童房产品信息对应表
CHILD = {}
# 模型中现有功能区列表
EXIST_RIGION = ['主卧', '客厅', '客房', '榻榻米', '餐厅', '厨房', '卫生间']
