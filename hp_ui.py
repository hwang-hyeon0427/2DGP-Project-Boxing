from pico2d import *
import game_framework

class HpUi:
    red_img = None
    yellow_img = None

    WIDTH = 329
    HEIGHT = 16

    def __init__(self, p1, p2, x, y, scale=3.0):
        self.p1 = p1
        self.p2 = p2
        self.x = x
        self.y = y
        self.scale = scale

        if HpUi.red_img is None:
            HpUi.red_img = load_image('resource/health/hp_red.png')
        if HpUi.yellow_img is None:
            HpUi.yellow_img = load_image('resource/health/hp_yellow.png')

        # delayed red hp
        self.p1_red_hp = p1.hp
        self.p2_red_hp = p2.hp

        # flash
        self.flash_duration = 1.0
        self.blink_interval = 0.2

        # P1 blink
        self.p1_flash = 0.0
        self.p1_blink = True
        self.p1_blink_timer = 0.0

        # P2 blink
        self.p2_flash = 0.0
        self.p2_blink = True
        self.p2_blink_timer = 0.0

    def update(self):
        dt = game_framework.frame_time

        # 데미지 체크
        if self.p1.hp < self.p1_red_hp:
            self.p1_flash = self.flash_duration
        if self.p2.hp < self.p2_red_hp:
            self.p2_flash = self.flash_duration

        # Flash 타이머 감소 + Red bar 추적
        # ---------------------
        # P1
        if self.p1_flash > 0:
            self.p1_flash -= dt
            self.p1_blink_timer += dt
            if self.p1_blink_timer >= self.blink_interval:
                self.p1_blink_timer = 0
                self.p1_blink = not self.p1_blink
        else:
            self.p1_blink = True
            self.p1_blink_timer = 0
            if self.p1_red_hp > self.p1.hp:
                self.p1_red_hp -= dt * 20
                if self.p1_red_hp < self.p1.hp:
                    self.p1_red_hp = self.p1.hp

        # ---------------------
        # P2
        if self.p2_flash > 0:
            self.p2_flash -= dt
            self.p2_blink_timer += dt
            if self.p2_blink_timer >= self.blink_interval:
                self.p2_blink_timer = 0
                self.p2_blink = not self.p2_blink
        else:
            self.p2_blink = True
            self.p2_blink_timer = 0
            if self.p2_red_hp > self.p2.hp:
                self.p2_red_hp -= dt * 20
                if self.p2_red_hp < self.p2.hp:
                    self.p2_red_hp = self.p2.hp

    # ---------------------------------------------
    # Draw left → right HP bar (P1)
    # ---------------------------------------------
    def draw_bar_left(self, yellow_hp, red_hp, blink):
        yp = int(self.WIDTH * (yellow_hp / 100))
        rp = int(self.WIDTH * (red_hp / 100))

        center_x = self.x - self.WIDTH * self.scale / 2

        # Red bar (Delayed HP)
        if blink and rp > 0:
            HpUi.red_img.clip_draw(
                0, 0, rp, self.HEIGHT,
                center_x + rp * self.scale / 2,
                self.y,
                rp * self.scale, self.HEIGHT * self.scale
            )

        # Yellow bar (Real-time HP)
        if yp > 0:
            HpUi.yellow_img.clip_draw(
                0, 0, yp, self.HEIGHT,
                center_x + yp * self.scale / 2,
                self.y,
                yp * self.scale, self.HEIGHT * self.scale
            )

    # ---------------------------------------------
    # Draw right → left HP bar (P2)
    # ---------------------------------------------
    def draw_bar_right(self, yellow_hp, red_hp, blink):
        yp = int(self.WIDTH * (yellow_hp / 100))
        rp = int(self.WIDTH * (red_hp / 100))

        center_x = self.x + self.WIDTH * self.scale / 2

        # Red bar (Delayed HP)
        if blink and rp > 0:
            r_src = self.WIDTH - rp
            HpUi.red_img.clip_draw(
                r_src, 0, rp, self.HEIGHT,
                center_x - rp * self.scale / 2,
                self.y,
                rp * self.scale, self.HEIGHT * self.scale
            )

        # Yellow bar (Real-time HP)
        if yp > 0:
            y_src = self.WIDTH - yp
            HpUi.yellow_img.clip_draw(
                y_src, 0, yp, self.HEIGHT,
                center_x - yp * self.scale / 2,
                self.y,
                yp * self.scale, self.HEIGHT * self.scale
            )

    # ---------------------------------------------
    def draw(self):
        # P1: Left bar
        self.draw_bar_left(self.p1.hp, self.p1_red_hp, self.p1_blink)

        # P2: Right bar
        self.draw_bar_right(self.p2.hp, self.p2_red_hp, self.p2_blink)
