# animated_button.py
from pico2d import *
import game_framework


class Button:
    _mouse_x = 0
    _mouse_y = 0

    @staticmethod
    def get_mouse_position():
        events = get_events()
        for e in events:
            if e.type == SDL_MOUSEMOTION:
                Button._mouse_x = e.x
                Button._mouse_y = get_canvas_height() - 1 - e.y
        return Button._mouse_x, Button._mouse_y

    def __init__(self, x, y, w, h,
                 normal_img,
                 anim_sheet, frame_count,
                 fps,
                 on_click=None):

        self.x, self.y = x, y
        self.w, self.h = w, h

        self.normal = load_image(normal_img)

        # 애니메이션 시트
        self.sheet = load_image(anim_sheet)
        self.frame_count = frame_count
        self.frame_w = self.sheet.w // frame_count
        self.frame_h = self.sheet.h
        self.fps = fps

        self.anim_frame = 0.0
        self.anim_playing = False

        self.on_click = on_click

    def get_bb(self):
        hw, hh = self.w // 2, self.h // 2
        return self.x - hw, self.y - hh, self.x + hw, self.y + hh

    def update(self):
        mx, my = Button.get_mouse_position()
        l, b, r, t = self.get_bb()
        is_hover = (l <= mx <= r and b <= my <= t)

        # 애니메이션 재생 중
        if self.anim_playing:
            self.anim_frame += self.fps * game_framework.frame_time
            if self.anim_frame >= self.frame_count:
                # 끝
                self.anim_playing = False
                self.anim_frame = 0
                if self.on_click:
                    self.on_click()

        self.is_hover = is_hover  # hover 없어도 클릭 판정을 위해 유지

    def draw(self):
        if self.anim_playing:
            # 애니메이션 프레임 그리기
            idx = int(self.anim_frame)
            src_x = idx * self.frame_w
            self.sheet.clip_draw(src_x, 0,
                                 self.frame_w, self.frame_h,
                                 self.x, self.y,
                                 self.w, self.h)
            return

        # 평상시(normal)만 그림
        self.normal.draw(self.x, self.y, self.w, self.h)

    def handle_event(self, e):
        if e.type == SDL_MOUSEBUTTONDOWN and e.button == SDL_BUTTON_LEFT:
            if self.is_hover and not self.anim_playing:
                self.anim_playing = True
                self.anim_frame = 0.0
