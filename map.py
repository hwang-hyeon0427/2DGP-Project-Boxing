from pico2d import *
import random

class Map:
    FRAME_W = 317
    FRAME_H = 128
    TOTAL_FRAMES = 4

    def __init__(self):
        bg_list = [
            'background/Boxing_Ring_Blue.png',
            'background/Boxing_Ring_Green.png',
            'background/Boxing_Ring_Orange.png',
            'background/Boxing_Ring_Purple.png'
        ]
        self.image = load_image(random.choice(bg_list))

        self.frame = 0.0
        self.frame_speed = 250.0

    def update(self):
        self.frame = (self.frame + self.frame_speed) % Map.TOTAL_FRAMES

    def draw(self):
        src_x = int(self.frame) * Map.FRAME_W

        w, h = get_canvas_width(), get_canvas_height()
        self.image.clip_draw(src_x, 0, Map.FRAME_W, Map.FRAME_H, w // 2, h // 2, w, h)

    def get_bb(self):
        return 0, 0, get_canvas_width(), get_canvas_height()

    def handle_collision(self, group, other):
        pass