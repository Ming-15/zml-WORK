
DEFAULT_ROOM_HEIGHT = 2700
MAX_BOUNARY_SEG_CHANGE = 100

# WIDTH: 指垂直于Element方向的长度
# LEN: 指平行于Element方向的长度
# 多种长度时，必须按顺序输入
# 窗帘
CURTAIN_LEN = 100
# 休闲椅
RECLINERS_WIDTH_LEN = (800, 1000)#900->800
R_FRONT = 300
# 床头柜
BEDSIDE_NIGHTTABLE_WIDTH = (450, 500, 550, 600)
BEDSIDE_NIGHTTABLE_LEN = 450

# 衣柜
CLOSET_WIDTH = (1300, 1500, 1600, 1800, 2100)#want del 1300 1500 but add 2500
CLOSET_LEN = 600
C_FRONT = 450

# 屉柜，chest of drawers
DRAWER_WIDTH = (600, 750, 900, 1200, 1500)#add 600 750
DRAWER_LEN = 450

# 写字桌
WRITING_DESK_WIDTH = (800, 900, 1000, 1100, 1200, 1500)
WRITING_DESK_LEN = 600

# 单椅
CHAIR_WIDTH = 450 #与之前调换
CHAIR_LEN = 500

# 次卧类型
BEDROOM_TYPE = ('guestroom', 'tatami', 'schoolroom', 'eldersroom', 'child')

# 门类型
DOOR_TYPE = ('single', 'double', 'sliding')
DOOR_WIDTH = 900
DOOR_LENGTH = 900
DOOR_WALL_LEN = 200
#为了方便进行避开门操作

#excel中的默认值
DEFAULT_VARIABLE_VALUE = -1
DEFAULT_CONNECT_STR = '_'




