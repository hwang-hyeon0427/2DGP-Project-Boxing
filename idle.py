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
        frame = int(self.boxer.frame)

        cfg = self.boxer.cfg['idle']
        w= cfg['w']
        h= cfg['h']
        cols = cfg['cols']

        left = frame * w
        bottom = 0

        if self.boxer.face_dir == 1:
            self.boxer.image.clip_draw(left, bottom, w, h, self.boxer.x, self.boxer.y)
        else:
            self.boxer.image.clip_composite_draw(
                left, bottom,
                w, h,
                0, 'h',
                self.boxer.x, self.boxer.y,
                w, h
            )
