# -*- coding:utf-8 -*-
from AutoLayout.BaseModual import *
from AutoLayout.bathroom.settings import *

class WashBasin(Element):
    name = "面盆"
    def __init__(self,backline):
        super(WashBasin,self).__init__()
        self.set_pos(backline,WASHBASIN_L)
class ToiletDevice(Element):
    name = "坐便器"
    def __init__(self,backline):
        super(ToiletDevice, self).__init__()
        self.set_pos(backline,TOILET_DEV_L)
class ShowerRoom(Element):
    name = "淋浴房"
    def __init__(self):
        super(ShowerRoom,self).__init__()
        # self.set_pos(backline,SHOWER_L)
class Spray(Element):
    name = "花洒"
    def __init__(self):
        super(Spray,self).__init__()
        # self.set_pos(backline,SHOWER_L)
class WashingMachine(Element):
    name = "洗衣机"
    def __init__(self,backline):
        super(WashingMachine,self).__init__()
        self.set_pos(backline,WAHING_MAC_L)