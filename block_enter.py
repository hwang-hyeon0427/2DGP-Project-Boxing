import game_framework

# Boxer Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8

class BlockEnter:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        self.boxer.frame = 0
        self.boxer.use_sheet(self.boxer.cfg['blocking'])

        # 이동 금지
        self.boxer.xdir = 0
        self.boxer.ydir = 0

    def exit(self, e):
        pass

    def do(self):
        # 프레임 증가
        self.boxer.frame += FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time

        if self.boxer.frame >= self.boxer.cols - 1:
            self.boxer.frame = self.boxer.cols - 1
            self.boxer.state_machine.handle_state_event(('BLOCK_ENTER_DONE', None))

    def draw(self):
        self.boxer.draw_current()