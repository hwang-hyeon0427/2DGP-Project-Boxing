from pico2d import *
import random

class Map:
    FRAME_W = 320
    FRAME_H = 173
    COLS = 4
    ROWS = 4

    def __init__(self, index=None):
        self.image = load_image('background/Boxing_Rings.png')

        if index is None:
            index = random.randint(0, Map.COLS * Map.ROWS - 1)

        self.index = index

        self.col = index % Map.COLS
        self.row = Map.ROWS - 1 - (index // Map.COLS)

    def update(self):
        pass

    def draw(self):


    def get_bb(self):
        return 0, 60, 800, 540

    def handle_collision(self, group, other):
        pass
