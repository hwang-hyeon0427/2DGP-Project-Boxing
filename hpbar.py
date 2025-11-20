from pico2d import draw_rectangle, draw_line

class HPBar:
    def __init__(self, boxer, x, y, width = 120, height = 10):
        self.boxer = boxer
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.boxer.max_hp = 100

    def update(self):
        pass

    def draw(self):
        ratio = max(self.boxer.hp / self.boxer.max_hp, 0)
        draw_rectangle(self.x - self.width//2, self.y - self.height//2, self.x + self.width//2, self.y + self.height//2)

        life_width = int(self.width * ratio)
        draw_rectangle(self.x - self.width//2, self.y - self.height//2, self.x + self.width//2, self.y + self.height//2)
