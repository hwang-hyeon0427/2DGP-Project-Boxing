import game_framework
import boxer

class Idle:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        # Idle 상태에 진입할 때 idle 시트로 변경
        self.boxer.use_sheet(self.boxer.cfg['idle'])

        # 속도 초기화
        self.boxer.vx = 0
        self.boxer.vy = 0

    def exit(self, e):
        pass

    def do(self):
        self.boxer.frame = ( self.boxer.frame + boxer.FRAMES_PER_ACTION * boxer.ACTION_PER_TIME * game_framework.frame_time) % 10

    def draw(self):
        self.boxer.draw_current()
