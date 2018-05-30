import AutoLayout.settings as settings
import math

BEDROOM_MAX_LEN = 4200
BEDROOM_MIN_LEN = 2500
# 单椅斜向60度放置
CHAIR_ANGLE = 60
rad = math.radians(60)
wid0 = int(settings.CHAIR_WIDTH * math.sin(rad) + settings.CHAIR_LEN * math.cos(rad))
len0 = int(settings.CHAIR_WIDTH * math.cos(rad) + settings.CHAIR_LEN * math.sin(rad))
OBLIQUE_CHAIR_WIDTH_LEN = (wid0, len0)
# 单椅距离床300 mm，到床尾距离600

OB_CHAIR_DIS_BED_SIDE = 300
OB_CHAIR_DIS_BED_END = 600
# 床, 1500以上为双人
BED_WIDTH = (1000, 1200, 1500, 1800)#add 1000
BED_LEN = 2100
BED_DOUBLE_THRESHOLD = 1500
BED_END_THRE_DIS = 500 #床过道预留区域



