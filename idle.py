import game_framework
import boxer

class Idle:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        self.boxer.use_sheet(self.boxer.cfg['idle'])
        self.boxer.dir = 0

    def exit(self, e):
        pass

    def do(self):
        # FPS 독립 애니메이션 (시간 기반)
        self.boxer.frame = ( self.boxer.frame + boxer.FRAMES_PER_ACTION * boxer.ACTION_PER_TIME * game_framework.frame_time) % 10

        # 넘치면 0으로 순환
        if self.boxer.frame >= self.boxer.cols:
            self.boxer.frame = 0

    def draw(self):
        self.boxer.draw_current()
