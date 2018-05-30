from AutoLayout.BaseClass import *

class Window(DY_segment):
    name = 'line'
    # def __new__(cls, p1, p2):
    #     return super(Window, cls).__new__(cls, p1, p2)
    def __init__(self, p1, p2):
        super(Window, self).__init__(p1, p2)
        self.name = "窗户"
        self.ID = 0
        self.tag = self.__class__.__name__

        self.half_width = 20 # mm
        self.wall = None
        self.boundary = None
        # if self.p1.x == self.p2.x:
        #     pp1 = Point(self.p1.x-self.half_width, self.p1.y)
        #     pp2 = Point(self.p2.x-self.half_width, self.p2.y)
        #     pp3 = Point(self.p2.x+self.half_width, self.p2.y)
        #     pp4 = Point(self.p1.x+self.half_width, self.p1.y)
        # else:
        #     pp1 = Point(self.p1.x, self.p1.y-self.half_width)
        #     pp2 = Point(self.p2.x, self.p2.y-self.half_width)
        #     pp3 = Point(self.p2.x, self.p2.y+self.half_width)
        #     pp4 = Point(self.p1.x, self.p1.y+self.half_width)
        # self.dy_boundary = DY_boundary(pp1, pp2, pp3, pp4)

    def draw(self, ax):
        # if self.boundary != None:
        #     self.boundary.draw(ax, col='#00B2EE')

        self.boundary.draw(ax, col='#00B2EE')

        # self.dy_boundary.draw(ax, col='#00B2EE')
        # xdata = (self.p1.x, self.p2.x)
        # ydata = (self.p1.y, self.p2.y)
        # ax.add_line(Line2D(xdata, ydata, color='#00B2EE'))

        # l0 = Line(self.point_list[0], self.point_list[2])
        # l1 = Line(self.point_list[1], self.point_list[3])
        # xdata = (l0.p1.x, l0.p2.x)
        # ydata = (l0.p1.y, l0.p2.y)
        # ax.add_line(Line2D(xdata, ydata, color='#9AFF9A'))
        # xdata = (l1.p1.x, l1.p2.x)
        # ydata = (l1.p1.y, l1.p2.y)
        # ax.add_line(Line2D(xdata, ydata, color='#9AFF9A'))
    def set_boundary(self, boundary):
        self.boundary = boundary


class Border(DY_segment):
    name = 'line'
    def __init__(self, p1, p2):
        super(Border, self).__init__(p1, p2)
        self.name = "虚边界"
        self.ID = 0
        self.connect_list = []
        self.wall = None

    def set_connect_list(self, name1, name2):
        # undo: check name sting
        self.connect_list.clear()
        self.connect_list.append(name1)
        self.connect_list.append(name2)

    def draw(self, ax):
        xdata = (self.p1.x, self.p2.x)
        ydata = (self.p1.y, self.p2.y)
        ax.add_line(Line2D(xdata, ydata, color='#FFFFFF'))
        ax.add_line(Line2D(xdata, ydata, linestyle='--', color='#9AFF9A'))

