import game_framework
import boxer

class Idle:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        self.boxer.use_sheet(self.boxer.cfg['idle'])
        if boxer.event_stop(e):
            self.boxer.face_dir = e[1]

    def exit(self, e):
        pass

    def do(self):
        self.boxer.frame = ( self.boxer.frame + boxer.FRAMES_PER_ACTION * boxer.ACTION_PER_TIME * game_framework.frame_time) % 10

    def draw(self):
        if self.boxer.face_dir == 1:  # right
            self.boxer.image.clip_draw(int(self.boxer.frame) * 100, 300, 100, 100, self.boxer.x, self.boxer.y)
        else:  # face_dir == -1: # left
            self.boxer.image.clip_draw(int(self.boxer.frame) * 100, 200, 100, 100, self.boxer.x, self.boxer.y)
