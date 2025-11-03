from key_events import left_down, right_down


class WalkForward:
    def __init__(self, boxer):
        self.b = boxer

    def enter(self, e):
        sheet = self.b.cfg.get('walk_forward') or self.b.cfg.get('walk') or self.b.cfg.get('idle')
        self.b.use_sheet(sheet)
        if left_down(e):
            self.b.dir = -1
        elif right_down(e):
            self.b.dir = 1
        else:
            self.b.dir = self.b.face

    def exit(self, e):
        self.b.dir = 0

    def do(self):
        self.b.frame = (self.b.frame + 1) % self.b.cols
        self.b.x += self.b.dir * 5

    def draw(self):
        self.b.draw_current()
