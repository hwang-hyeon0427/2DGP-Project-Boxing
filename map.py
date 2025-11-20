from pico2d import *

class Map:
    def __init__(self):
        self.image = load_image('background/boxingring.png')

    def update(self):
        pass

    def draw(self):
        self.image.draw(400, 300)
        draw_rectangle(*self.get_bb())


    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass