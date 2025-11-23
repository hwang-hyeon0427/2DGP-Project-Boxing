from pico2d import *
import game_world
class HitBox:
    def __init__(self, owner, offset_x, offset_y, w, h, duration):
        self.owner = owner
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.width = w
        self.height = h
        self.end_time = get_time() + duration


    def draw(self):
        if get_time() > self.end_time:
            game_world.remove_object(self)

    def update(self):
        pass

    def get_bb(self):
        return 0, 0, 0, 0

    def handle_collision(self, other, group):
        pass