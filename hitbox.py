from pico2d import *
import game_world
class HitBox:
    def __init__(self, owner, offset_x, offset_y, w, h, duration):
        self.owner = owner
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.w = w
        self.h = h
        self.end_time = get_time() + duration


    def draw(self):
        draw_rectangle(* self.get_bb())

    def update(self):
        if get_time() > self.end_time:
            game_world.remove_object(self)

    def get_bb(self):
        x = self.owner.x + self.offset_x
        y = self.owner.y + self.offset_y
        return x - self.w/2, y - self.h/2, x + self.w/2, y + self.h/2

    def handle_collision(self, other, group):
        pass