#—*— coding: utf-8 _*_
from AutoLayout.BaseModual import *
from AutoLayout.settings import *
from AutoLayout.childrenroom.settings import *


class Bed(Element):
    name = "床"

    def __init__(self):
        super(Bed, self).__init__()
        self.len = BED_LEN


class ChildCloset(Element):
    name = "儿童衣柜"

    def __init__(self, backline):
        super(ChildCloset, self).__init__()
        self.set_pos(backline, CHILDCLOSET_LEN)


class ChildPlay(Element):
    name = "儿童玩具柜"

    def __init__(self):
        super(ChildPlay, self).__init__()
        self.len = CHILD_PLAY_LEN


class ChildTable(Element):
    name = "儿童游戏桌"

    def __init__(self):
        super(ChildTable, self).__init__()
        self.len = CHILD_TABLE


class ChildStool(Element):
    name = "凳子"

    def __init__(self):
        super(ChildStool, self).__init__()
        self.len = CHIDL_STOOL


class ChildTent(Element):
    name = "帐篷活动区"

    def __init__(self):
        super(ChildTent, self).__init__()
        self.len = CHILD_TENT


