# _*_ coding:utf-8 _*_
import random
from AutoLayout.tatami_room.settings import *
from AutoLayout.helpers import *
from AutoLayout.BaseModual import Element

class BookCase(Element):
    name = "书柜"
    def __init__(self,backline):
        super(BookCase,self).__init__()
        self.set_pos(backline,CUSTOM_BOOKCASE_LENGTH)
class TataBedLift(Element):
    name = "智能桌榻榻米"
    def __init__(self):
        super(TataBedLift, self).__init__()
        self.wid_len = TATAMI_BED_LENGTH
class TataBedFloor(Element):
    name = "平板床榻榻米"
    def __init__(self):
        super(TataBedFloor, self).__init__()
        self.wid_len = TATAMI_BED_LENGTH
def get_mibed_type(self):
        case = random.randint(0,1)
        if case == 0:
            return  TataBedLift()
        else:
            return  TataBedFloor()