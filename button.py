from pico2d import *


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

    def update(self, mx, my):
        w = SpriteSheetButton.CELL_W * self.scale
        h = SpriteSheetButton.CELL_H * self.scale

        # hover 여부 판정
        self.hover = (self.x - w / 2 < mx < self.x + w / 2) and \
                     (self.y - h / 2 < my < self.y + h / 2)

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

        if inside and self.on_click:
            self.on_click()

