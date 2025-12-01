from key_events import left_down, right_down
import boxer


class WalkForward:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        sheet = self.boxer.cfg.get('walk_forward')
        self.b.use_sheet(sheet)
        if self.boxer.xdir != 0:
            self.boxer.face_dir = self.boxer.xdir

    def exit(self, e):
        self.boxer.dir = 0

    def do(self):
        self.boxer.frame = (self.boxer.frame + 1) % self.boxer.cols
        self.boxer.x += self.boxer.dir * 5

    def draw(self):
        self.boxer.draw_current()
