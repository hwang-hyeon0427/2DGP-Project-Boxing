class AttackState:
    def __init__(self, boxer, attack_type):
        self.b = boxer
        self.type = attack_type

    def enter(self, e):
        sheet = self.b.cfg.[self.type]
        self.b.use_sheet(sheet)
        self.b.frame = 0

        self.b.is_attacking = True
        self.b.current_attack_type = self.type

    def exit(self, e):
        self.b.is_attacking = False
        self.b.current_attack_type = None

    def do(self):
        if not self.done:
            self.b.frame += 1
            if self.b.frame >= self.b.cols:
                self.done = True
                self.b.state_machine.handle_state_event(('ANIMATION_END', None))

    def draw(self):
        self.b.draw_current()
