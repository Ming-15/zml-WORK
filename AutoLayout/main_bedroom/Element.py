from AutoLayout.BaseModual import *
from AutoLayout.main_bedroom.settings import *

class Bed(Element):
    name = "床"
    def __init__(self):
        super(Bed, self).__init__()
        self.len = MAINBED_BED_LEN

