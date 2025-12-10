from pico2d import *
import game_framework

# Boxer Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8

class Hurt:
    DURATION = 0.25  # 피격 모션 길이

    def __init__(self, boxer):
        self.boxer = boxer
        self.start_time = 0

    def enter(self, e):
        self.start_time = get_time()
        self.boxer.frame = 0
        self.boxer.use_sheet(self.boxer.cfg['hurt'])

    def exit(self, e):
        pass

    def do(self):
        self.boxer.frame += FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time

        # 모션 끝나면 Idle로 자동 복귀
        if get_time() - self.start_time >= Hurt.DURATION:
            self.boxer.state_machine.handle_state_event(('HURT_DONE', None))

    def draw(self):
        self.boxer.draw_current()