from key_events import left_down, right_down
import boxer

class Walk:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        sheet = self.boxer.cfg.get('walk_forward')
        self.b.use_sheet(sheet)
        if self.boxer.xdir != 0:
            self.boxer.face_dir = self.boxer.xdir

    def exit(self, e):
        self.boxer.dir = 0

    def do(self):
        self.boxer.frame = (self.boxer.frame + boxer.FRAMES_PER_ACTION * boxer.ACTION_PER_TIME * boxer.game_framework.frame_time) % 10
        self.boxer.x += self.boxer.xdir * boxer.RUN_SPEED_PPS * boxer.game_framework.frame_time
        self.boxer.y += self.boxer.ydir * boxer.RUN_SPEED_PPS * boxer.game_framework.frame_time

    def draw(self):
        if self.boxer.xdir == 0:  # 위 아래로 움직이는 경우
            if self.boxer.face_dir == 1:  # right
                self.boxer.image.clip_draw(int(self.boxer.frame) * 100, 100, 100, 100, self.boxer.x, self.boxer.y)
            else:
                self.boxer.image.clip_draw(int(self.boxer.frame) * 100, 0, 100, 100, self.boxer.x, self.boxer.y)
        elif self.boxer.xdir == 1:
            self.boxer.image.clip_draw(int(self.boxer.frame) * 100, 100, 100, 100, self.boxer.x, self.boxer.y)
        else:
            self.boxer.image.clip_draw(int(self.boxer.frame) * 100, 0, 100, 100, self.boxer.x, self.boxer.y)

