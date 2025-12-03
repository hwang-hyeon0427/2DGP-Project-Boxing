from pico2d import *
import game_framework

class HpUi:
    image = None

    IMG_W = 329
    IMG_H = 31

    BAR_W = 160
    BAR_H = 16

    LEFT_X  = 0
    RIGHT_X = 169

    YELLOW_Y = 0
    RED_Y = 11

    def __init__(self, p1, p2, x, y, scale=3.0):
        self.p1 = p1
        self.p2 = p2
        self.x = x
        self.y = y
        self.scale = scale

        if HpUi.image is None:
            HpUi.image = load_image('health/hp.png')

        self.p1_last_hp = p1.hp
        self.p2_last_hp = p2.hp

        self.p1_flash = 0
        self.p2_flash = 0

        self.flash_duration = 0.25
        self.blink_interval = 0.07
        self.blink_timer = 0
        self.blink = False

    def update(self):
        dt = game_framework.frame_time

        if self.p1.hp < self.p1_last_hp:
            self.p1_flash = self.flash_duration
        self.p1_last_hp = self.p1.hp

        if self.p2.hp < self.p2_last_hp:
            self.p2_flash = self.flash_duration
        self.p2_last_hp = self.p2.hp

        if self.p1_flash > 0 or self.p2_flash > 0:
            self.blink_timer += dt
            if self.blink_timer >= self.blink_interval:
                self.blink_timer = 0
                self.blink = not self.blink

        self.p1_flash = max(0, self.p1_flash - dt)
        self.p2_flash = max(0, self.p2_flash - dt)

    # -------------------
    # 전체 hp.png 그림
    # -------------------
    def draw_base(self):
        HpUi.image.clip_draw(
            0, self.YELLOW_Y,  # src_x, src_y
            self.IMG_W, self.BAR_H,  # width=전체폭, height=노란바 높이
            self.x, self.y,  # 화면 좌표
            self.IMG_W * self.scale,
            self.BAR_H * self.scale
        )

    # -------------------
    # 노란바 (항상 표시)
    # -------------------
    def draw_yellow(self, hp, src_x):
        ratio = hp / 100.0
        px = int(self.BAR_W * ratio)
        if px <= 0: return

        img_left = self.x - (self.IMG_W * self.scale)/2 + src_x * self.scale
        center_x = img_left + (px * self.scale)/2

        HpUi.image.clip_draw(
            src_x, self.YELLOW_Y,
            px, self.BAR_H,
            center_x, self.y,
            px * self.scale, self.BAR_H * self.scale
        )

    # -------------------
    # 빨간 플래시 (데미지 구간)
    # -------------------
    def draw_flash(self, last_hp, hp, src_x):
        if last_hp <= hp: return
        if not self.blink: return

        old_px = int(self.BAR_W * (last_hp / 100))
        new_px = int(self.BAR_W * (hp / 100))
        lost_px = old_px - new_px
        if lost_px <= 0: return

        img_left = self.x - (self.IMG_W * self.scale)/2 + src_x * self.scale
        center_x = img_left + ((new_px + lost_px/2) * self.scale)
        center_y = self.y + (self.BAR_H * self.scale)

        HpUi.image.clip_draw(
            src_x + new_px, self.RED_Y,
            lost_px, self.BAR_H,
            center_x, center_y,
            lost_px * self.scale, self.BAR_H * self.scale
        )

    # -------------------
    # 전체 draw()
    # -------------------
    def draw(self):
        # 1) hp.png 전체 (KO 포함)
        self.draw_base()

        # 2) 노란바
        self.draw_yellow(self.p1.hp, self.LEFT_X)
        self.draw_yellow(self.p2.hp, self.RIGHT_X)

        # 3) 빨간 플래시
        self.draw_flash(self.p1_last_hp, self.p1.hp, self.LEFT_X)
        self.draw_flash(self.p2_last_hp, self.p2.hp, self.RIGHT_X)
