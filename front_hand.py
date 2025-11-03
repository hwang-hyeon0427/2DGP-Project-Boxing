class FrontHand:
    def __init__(self, boxer):
        self.b = boxer
        self.done = False

    def enter(self, e):
        # 설정에 키가 없으면 idle 사용
        if 'front_hand' in self.b.cfg:
            sheet = self.b.cfg['front_hand']
        else:
            sheet = self.b.cfg['idle']
        self.b.use_sheet(sheet)
        self.b.frame = 0
        self.done = False

    def exit(self, e):
        pass

    def do(self):
        if not self.done:
            self.b.frame += 1
            if self.b.frame >= self.b.cols:
                self.done = True
                self.b.state_machine.handle_state_event(('ANIMATION_END', None))

    def draw(self):
        self.b.draw_current()
