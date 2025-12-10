import game_framework

# Boxer Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8

class Ko:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        self.boxer.frame = 0
        self.boxer.use_sheet(self.boxer.cfg['ko'])

        self.boxer.pushback_time = 0
        self.boxer.pushback_velocity_x = 0
        self.boxer.pushback_velocity_y = 0

    def exit(self, e):
        pass

    def do(self):
        max_frame = self.boxer.cols - 1
        self.boxer.frame += FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
        if self.boxer.frame > max_frame:
            self.boxer.frame = max_frame  # 프레임 고정

            if self.boxer.on_ko_end:
                self.boxer.on_ko_end()
                self.boxer.on_ko_end = None

    def draw(self):
        self.boxer.draw_current()