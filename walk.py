from key_events import left_down, right_down
import boxer

class Walk:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        sheet = self.boxer.cfg.get('walk_forward')
        self.boxer.use_sheet(sheet)

    def exit(self, e):
        self.boxer.dir = 0

    def do(self):
        self.boxer.frame = (self.boxer.frame + boxer.FRAMES_PER_ACTION * boxer.ACTION_PER_TIME * boxer.game_framework.frame_time) % 10
        self.boxer.x += self.boxer.xdir * boxer.WALK_SPEED_PPS * boxer.game_framework.frame_time
        self.boxer.y += self.boxer.ydir * boxer.WALK_SPEED_PPS * boxer.game_framework.frame_time

    def draw(self):
        frame = int(self.boxer.frame)
        fw = self.boxer.frame_w
        fh = self.boxer.frame_h

        if self.boxer.face_dir == 1:  # right
            self.boxer.image.clip_draw(frame * fw, 0, fw, fh, self.boxer.x, self.boxer.y)
        else:
            self.boxer.image.clip_composite_draw(frame * fw, 0, fw, fh, 0, 'h', self.boxer.x, self.boxer.y)

