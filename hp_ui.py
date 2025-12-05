from pico2d import *

class HpUi:
    red_img = None
    yellow_img = None

    WIDTH = 600      # 전체 HP바 길이 (원하는 값으로 조절)
    HEIGHT = 16

    def __init__(self, p1, p2, x=None, y=None, scale=2.8):
        self.p1 = p1
        self.p2 = p2
        self.x = x
        self.y = y
        self.scale = scale

        # 체력 (100 기준)
        self.hp_left  = 100   # P1
        self.hp_right = 100   # P2

        if HpUi.red_img is None:
            HpUi.red_img = load_image("resource/health/hp_red.png")
        if HpUi.yellow_img is None:
            HpUi.yellow_img = load_image("resource/health/hp_yellow.png")

    def update(self):
        self.hp_left = self.p1.hp
        self.hp_right = self.p2.hp

    # -------------------------------------------------------
    # 단일 draw() – red 1번 + yellow 1번만 사용!
    # -------------------------------------------------------
    def draw(self):

        # RED HP (전체 바)
        HpUi.red_img.clip_draw(
            0, 0, self.WIDTH, self.HEIGHT,
            self.x, self.y,
            self.WIDTH * self.scale,
            self.HEIGHT * self.scale
        )

        ratio_left = max(0, self.hp_left / self.p1.max_hp)
        ratio_right = max(0, self.hp_right / self.p2.max_hp)

        left_len = int(self.WIDTH * ratio_left)
        right_len = int(self.WIDTH * ratio_right)

        # LEFT HP (왼 → 왼)
        if left_len > 0:
            HpUi.yellow_img.clip_draw(
                0, 0, left_len, self.HEIGHT,
                self.x - (self.WIDTH * self.scale) / 2 + (left_len * self.scale) / 2,
                self.y,
                left_len * self.scale,
                self.HEIGHT * self.scale
            )

        # RIGHT HP (오 → 오)
        if right_len > 0:
            HpUi.yellow_img.clip_draw(
                self.WIDTH - right_len, 0, right_len, self.HEIGHT,
                self.x + (self.WIDTH * self.scale) / 2 - (right_len * self.scale) / 2,
                self.y,
                right_len * self.scale,
                self.HEIGHT * self.scale
            )
