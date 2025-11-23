class AttackState:
    def __init__(self, boxer, key):
        self.b = boxer
        self.key = key      # ex) 'front_hand', 'rear_hand', 'uppercut'
        self.done = False

    def enter(self, e):
        sheet = self.b.cfg.get(self.key, self.b.cfg['idle'])
        self.b.use_sheet(sheet)
        self.b.frame = 0
        self.done = False

        self.b.spawn_hitbox()

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
