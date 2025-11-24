from pico2d import *

class HPBar:
    def __init__(self, boxer, x, y):
        self.boxer = boxer
        self.x = x
        self.y = y

        self.image = load_image('health/health-bar.png')

        self.frame_count = 6 # 0~5 프레임
        self.frame_w = self.image.w # 가로 전체 크기에서 프레임 수로 나눈 값
        self.frame_h = self.image.h // self.frame_count

        self.scale = 0.5

    def draw(self):
        ratio = self.boxer.hp / self.boxer.max_hp #

        # 체력비율 → 0~5 프레임 자동 변환
        frame = int(ratio * (self.frame_count - 1)) #

        # 안전장치
        frame = max(0, min(frame, self.frame_count - 1))

        # PNG는 위=0 프레임 아래=5 프레임
        bottom = frame * self.frame_h

        self.image.clip_draw(
            0, bottom,
            self.frame_w, self.frame_h,
            self.x, self.y, self.frame_w * self.scale, self.frame_h * self.scale
        )

    def update(self):
        pass