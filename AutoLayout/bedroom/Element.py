from AutoLayout.BaseModual import *
from AutoLayout.bedroom.settings import *

class ObliqueChair(Element):
    name = "斜置单椅"
    def __init__(self, backline):
        super(ObliqueChair, self).__init__()
        self.set_pos(backline, OBLIQUE_CHAIR_WIDTH_LEN[1])

class Bed(Element):
    name = "床"

    def __init__(self):
        super(Bed, self).__init__()
        self.len = BED_LEN