# hp_ui.py
from pico2d import *
import game_framework

class HPUI:
    image = None
    W = 329
    H = 31

    # hp.png 내부 바 픽셀 좌표
    LEFT_BAR_X = 0        # 0~159
    RIGHT_BAR_X = 169     # 169~328
    BAR_W = 160
    RED_Y = 0             # 빨간바 y=0~9
    YELLOW_Y = 11         # 노란바 y=11~20
    BAR_H = 10

    def __init__(self, p1, p2, x, y, scale=3.0):
        self.p1 = p1
        self.p2 = p2
        self.x = x
        self.y = y
        self.scale = scale

        if HPUI.image is None:
            HPUI.image = load_image('hp.png')

        # 플래시용
        self.p1_last_hp = p1.hp
        self.p2_last_hp = p2.hp

        self.p1_flash = 0
        self.p2_flash = 0
        self.flash_time = 0.25
        self.blink = False
        self.blink_interval = 0.07
        self.blink_timer = 0

    def update(self):
        dt = game_framework.frame_time

        # P1 데미지 감지
        if self.p1.hp < self.p1_last_hp:
            self.p1_flash = self.flash_time
        self.p1_last_hp = self.p1.hp

        # P2 데미지 감지
        if self.p2.hp < self.p2_last_hp:
            self.p2_flash = self.flash_time
        self.p2_last_hp = self.p2.hp

        # 플래시 타이머
        if self.p1_flash > 0 or self.p2_flash > 0:
            self.blink_timer += dt
            if self.blink_timer >= self.blink_interval:
                self.blink_timer = 0
                self.blink = not self.blink

        self.p1_flash = max(0, self.p1_flash - dt)
        self.p2_flash = max(0, self.p2_flash - dt)

    def draw_bar(self, cur_hp, max_hp, bar_x, direction):
        """
        direction = 1 : 왼쪽→오른쪽 (P1)
        direction = -1: 오른쪽→왼쪽 (P2)
        """
        ratio = max(0, min(1, cur_hp / max_hp))
        bar_pixel_w = int(self.BAR_W * ratio)

        if bar_pixel_w <= 0:
            return

        if direction == 1:     # P1 왼쪽바
            src_x = bar_x
        else:                  # P2 오른쪽바 (오른쪽에서 줄어듬)
            src_x = bar_x + (self.BAR_W - bar_pixel_w)

        screen_w = bar_pixel_w * self.scale
        screen_h = self.BAR_H * self.scale
        center_x = self.x - (self.W*self.scale)/2 + (src_x + bar_pixel_w/2)*self.scale
        center_y = self.y

        HPUI.image.clip_draw(
            src_x, self.YELLOW_Y,
            bar_pixel_w, self.BAR_H,
            center_x, center_y,
            screen_w, screen_h
        )

    def draw_flash(self, old_hp, new_hp, bar_x, direction):
        if old_hp <= new_hp:
            return

        old_w = int(self.BAR_W * (old_hp / 100))
        new_w = int(self.BAR_W * (new_hp / 100))
        diff = old_w - new_w
        if diff <= 0:
            return

        if not self.blink:
            return

        if direction == 1:
            src_x = bar_x + new_w
        else:
            src_x = bar_x + (self.BAR_W - old_w)

        screen_w = diff * self.scale
        screen_h = self.BAR_H * self.scale
        center_x = self.x - (self.W*self.scale)/2 + (src_x + diff/2)*self.scale
        center_y = self.y

        HPUI.image.clip_draw(
            src_x, self.RED_Y,
            diff, self.BAR_H,
            center_x, center_y,
            screen_w, screen_h
        )

    def draw(self):
        # 배경 전체(중앙 KO 포함) 먼저 그리기
        HPUI.image.draw(self.x, self.y, self.W*self.scale, self.H*self.scale)

        # ---- P1 ----
        self.draw_bar(self.p1.hp, 100, self.LEFT_BAR_X, +1)
        self.draw_flash(self.p1_last_hp, self.p1.hp, self.LEFT_BAR_X, +1)

        # ---- P2 ----
        self.draw_bar(self.p2.hp, 100, self.RIGHT_BAR_X, -1)
        self.draw_flash(self.p2_last_hp, self.p2.hp, self.RIGHT_BAR_X, -1)
