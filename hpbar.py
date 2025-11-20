from pico2d import draw_rectangle, draw_line

class HPBar:
    def __init__(self, boxer, x, y, width = 120, height = 10):
        self.boxer = boxer
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def update(self):
        pass

    def draw(self):
        ratio = max(self.boxer.hp / self.boxer.max_hp, 0)

        half_w = self.width / 2
        half_h = self.height / 2

        left = self.x - half_w
        right = self.x + half_w
        bottom = self.y - half_h
        top = self.y + half_h

        draw_rectangle(left, top, right, bottom)

        hp_right = left + half_w * ratio
        draw_rectangle(left, bottom, hp_right, top)