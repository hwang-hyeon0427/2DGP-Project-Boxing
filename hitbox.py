from pico2d import *

class HitBox:
    def __init__(self, owner, offset_x, offset_y, w, h, duration):
        self.owner = owner
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.width = w
        self.height = h
        self.end_time = get_time() + duration


    def draw(self):
        pass

    def update(self):
        pass

    def get_bb(self):
        return 0, 0, 0, 0

    def handle_collision(self, other, group):
        pass