class Idle:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        self.boxer.use_sheet(self.boxer.cfg['idle'])
        self.boxer.dir = 0

    def exit(self, e):
        pass

    def do(self):
        self.boxer.frame = (self.boxer.frame + 1) % self.boxer.cols

    def draw(self):
        self.boxer.draw_current()
