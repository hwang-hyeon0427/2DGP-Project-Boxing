import game_framework
# Boxer Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8

class BlockExit:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        print("[ENTER] BlockExit: force stop movement")
        self.boxer.xdir = 0
        self.boxer.ydir = 0
        self.boxer.ignore_next_move_keyup = True
        self.boxer.use_sheet(self.boxer.cfg['blocking'])
        self.boxer.frame = self.boxer.cols - 1

    def exit(self, boxer, e):
        boxer.resume_move_after_action()

    def do(self):
        self.boxer.frame -= FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time

        if self.boxer.frame <= 0:
            self.boxer.frame = 0
            self.boxer.state_machine.handle_state_event(('BLOCK_EXIT_DONE', None))

    def draw(self):
        self.boxer.draw_current()