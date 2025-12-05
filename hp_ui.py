from pico2d import *

class HpUi:
    bar_red = None
    bar_yellow = None
    ko_img = None

    WIDTH = 600
    HALF = WIDTH // 2
    HEIGHT = 13   # 너의 hp_bar PNG 높이에 맞춤

    def __init__(self, p1, p2, x=None, y=None, scale=3.0):
        self.p1 = p1
        self.p2 = p2
        self.x = x
        self.y = y
        self.scale = scale

        if HpUi.bar_red is None:
            HpUi.bar_red = load_image("resource/health/hp_bar_red.png")
        if HpUi.bar_yellow is None:
            HpUi.bar_yellow = load_image("resource/health/hp_bar_yellow.png")
        if HpUi.ko_img is None:
            HpUi.ko_img = load_image("resource/health/hp_KO_red.png")

    def update(self):
        pass

    def draw(self):
        ### 1) RED 전체 바 ###
        HpUi.bar_red.draw(
            self.x, self.y,
            HpUi.WIDTH * self.scale,
            HpUi.HEIGHT * self.scale
        )

        ### P1 / P2 HP 비율 ###
        ratio_left  = max(0, min(1, self.p1.hp / self.p1.max_hp))
        ratio_right = max(0, min(1, self.p2.hp / self.p2.max_hp))

        left_len  = int(HpUi.HALF * ratio_left)
        right_len = int(HpUi.HALF * ratio_right)

        # --------------------------------------
        # 2) LEFT HP (왼쪽 → 오른쪽)
        # --------------------------------------
        if left_len > 0:
            HpUi.bar_yellow.clip_draw(
                0, 0, left_len, HpUi.HEIGHT,
                self.x - (HpUi.WIDTH * self.scale) / 2 + (left_len * self.scale) / 2,
                self.y,
                left_len * self.scale,
                HpUi.HEIGHT * self.scale
            )

        # --------------------------------------
        # 3) RIGHT HP (오른쪽 → 왼쪽)
        # --------------------------------------
        if right_len > 0:
            src_x = HpUi.HALF - right_len  # 오른쪽 기준으로 자르기
            HpUi.bar_yellow.clip_draw(
                src_x, 0, right_len, HpUi.HEIGHT,
                self.x + (HpUi.WIDTH * self.scale) / 2 - (right_len * self.scale) / 2,
                self.y,
                right_len * self.scale,
                HpUi.HEIGHT * self.scale
            )

        # --------------------------------------
        # 4) 중앙 KO 출력
        # --------------------------------------
        HpUi.ko_img.draw(
            self.x,
            self.y + HpUi.HEIGHT * self.scale * 0.55,
            HpUi.ko_img.w * self.scale,
            HpUi.ko_img.h * self.scale
        )
