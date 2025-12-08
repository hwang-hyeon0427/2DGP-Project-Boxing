from pico2d import *
import sound_manager


class SpriteSheetButton:
    # 스프라이트 시트 정보
    CELL_W = 64
    CELL_H = 16
    COLS = 5
    ROWS = 12

    image = None

    def __init__(self, sheet_path, row, x, y, scale=4,
                 normal_col=0, hover_col=1, on_click=None):
        if SpriteSheetButton.image is None:
            SpriteSheetButton.image = load_image(sheet_path)

        self.row = row
        self.x, self.y = x, y
        self.scale = scale

        self.normal_col = normal_col
        self.hover_col = hover_col
        self.on_click = on_click

        self.hover = False
        self.was_hover = False

    def update(self, mx, my):
        w = SpriteSheetButton.CELL_W * self.scale
        h = SpriteSheetButton.CELL_H * self.scale

        # hover 여부 판정
        is_hover_now = (self.x - w / 2 < mx < self.x + w / 2) and \
                     (self.y - h / 2 < my < self.y + h / 2)

        if is_hover_now and not self.was_hover:
            sound_manager.play("hover")

        self.was_hover = is_hover_now
        self.hover = is_hover_now

    def draw(self):
        col = self.hover_col if self.hover else self.normal_col

        left = col * SpriteSheetButton.CELL_W
        bottom = (SpriteSheetButton.ROWS - 1 - self.row) * SpriteSheetButton.CELL_H

        SpriteSheetButton.image.clip_draw(
            left, bottom,
            SpriteSheetButton.CELL_W, SpriteSheetButton.CELL_H,
            self.x, self.y,
            SpriteSheetButton.CELL_W * self.scale,
            SpriteSheetButton.CELL_H * self.scale
        )

    def click(self, mx, my):
        w = SpriteSheetButton.CELL_W * self.scale
        h = SpriteSheetButton.CELL_H * self.scale

        inside = (self.x - w / 2 < mx < self.x + w / 2) and \
                 (self.y - h / 2 < my < self.y + h / 2)

        if inside:
            sound_manager.play("click")  # ★ 클릭 사운드
            if self.on_click:
                self.on_click()

class Button:
    def __init__(self, image_path, x, y, scale=1.0, on_click=None):
        self.image = load_image(image_path)
        self.x, self.y = x, y
        self.scale = scale
        self.on_click = on_click
        self.hover = False

        self.hover = False
        self.was_hover = False

        self.w = self.image.w * scale
        self.h = self.image.h * scale

    def update(self, mx, my):
        is_hover_now = (self.x - self.w/2 < mx < self.x + self.w/2 and
                      self.y - self.h/2 < my < self.y + self.h/2)

        if is_hover_now and not self.was_hover:
            sound_manager.play("hover")

        self.hover = is_hover_now
        self.was_hover = is_hover_now

    def draw(self):
        # hover 시 약간 크게
        draw_scale = self.scale * (1.1 if self.hover else 1.0)

        self.image.draw(self.x, self.y,
                        self.image.w * draw_scale,
                        self.image.h * draw_scale)

    def click(self, mx, my):
        inside = (self.x - self.w / 2 < mx < self.x + self.w / 2 and
                  self.y - self.h / 2 < my < self.y + self.h / 2)

        if inside:
            sound_manager.play("click")
            if self.on_click:
                self.on_click()
