class Block:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        self.boxer.use_sheet(self.boxer.cfg['blocking'])  # 가드 유지 포즈
        self.boxer.frame = self.boxer.cols - 1  # 마지막 프레임 고정
        self.boxer.xdir = 0
        self.boxer.ydir = 0

    def exit(self, e):
        pass

    def do(self):
        self.boxer.frame = self.boxer.cols - 1

    def draw(self):
        self.boxer.draw_current()