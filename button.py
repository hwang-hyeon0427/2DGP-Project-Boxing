# animated_button.py
from pico2d import *
import game_framework

class Button:
    def __init__(self, x, y, w, h,
                 normal_img, hover_img,
                 anim_sheet, frame_count,
                 fps,
                 on_click=None):

        self.x, self.y = x, y
        self.w, self.h = w, h

        self.normal = load_image(normal_img)
        self.hover = load_image(hover_img)

        # 애니메이션 시트
        self.sheet = load_image(anim_sheet)
        self.frame_count = frame_count
        self.frame_w = self.sheet.w // frame_count
        self.frame_h = self.sheet.h
        self.fps = fps

        self.anim_frame = 0.0
        self.anim_playing = False

        self.on_click = on_click
        self.is_hover = False

    def get_bb(self):
        hw, hh = self.w // 2, self.h // 2
        return self.x - hw, self.y - hh, self.x + hw, self.y + hh

    def update(self):
        mx, my = get_mouse_position()

        # hover 판정
        l, b, r, t = self.get_bb()
        self.is_hover = (l <= mx <= r and b <= my <= t)

        # 애니메이션 재생 중이면 frame_time 기반 진행
        if self.anim_playing:
            self.anim_frame += self.fps * game_framework.frame_time

            if self.anim_frame >= self.frame_count:
                # 애니메이션이 끝나면 ↓
                self.anim_playing = False
                self.anim_frame = 0

                # 끝나자마자 버튼 기능 실행
                if self.on_click:
                    self.on_click()

    def draw(self):
        # 애니메이션 재생 중이면 애니메이션 우선
        if self.anim_playing:
            frame_idx = int(self.anim_frame)
            src_x = self.frame_w * frame_idx
            self.sheet.clip_draw(src_x, 0,
                                 self.frame_w, self.frame_h,
                                 self.x, self.y,
                                 self.w, self.h)
            return

        # 평상시(normal, hover)
        if self.is_hover:
            self.hover.draw(self.x, self.y, self.w, self.h)
        else:
            self.normal.draw(self.x, self.y, self.w, self.h)

    def handle_event(self, e):
        if e.type == SDL_MOUSEBUTTONDOWN and e.button == SDL_BUTTON_LEFT:
            if self.is_hover and not self.anim_playing:
                self.anim_playing = True  # 클릭 → 애니메이션 시작
                self.anim_frame = 0.0
