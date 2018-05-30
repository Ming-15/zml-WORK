import AutoLayout.BaseModual
import AutoLayout.settings
import AutoLayout.hard_deco.settings
from AutoLayout.BaseClass import DY_segment

CEIL_LAMP_TAG = 'test_cl'

class Ceiling_lamp(AutoLayout.BaseModual.Element):
    name = "吊灯"
    def __init__(self,backline):
        super(Ceiling_lamp, self).__init__()
        self.height = AutoLayout.settings.DEFAULT_ROOM_HEIGHT - \
                      AutoLayout.hard_deco.settings.CEILING_LAMP_W_L_H[CEIL_LAMP_TAG][2]
        self.set_pos(backline,
                     AutoLayout.hard_deco.settings.CEILING_LAMP_W_L_H[CEIL_LAMP_TAG][1])

class Wallpaper(DY_segment):
    name = "壁纸"
    def __init__(self, p1, p2):
        super(Wallpaper, self).__init__(p1, p2)
        self.ID = -1

