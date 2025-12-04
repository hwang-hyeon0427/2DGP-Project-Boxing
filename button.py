from pico2d import *

class Button:
    def __init__(self, x, y, w, h, image_normal, image_hover, image_click = None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.image_normal = load_image(image_normal)
        self.image_hover = load_image(image_hover)
        self.image_clicked = load_image(image_click) if image_click else None
        self.state = 'normal'  # can be 'normal', 'hover', 'clicked'

    def get_bb(self):
        half_w, half_h = self.w // 2, self.h // 2
        return self.x - half_w, self.y - half_h, self.x + half_w, self.y + half_h

    def update(self):
        mx, my = get_mouse_position()

        left, bottom, right, top = self.get_bb()
        self.is_hover = (left <= mx <= right and bottom <= my <= top)

    def draw(self):
        if self.is_hover:
            self.hover_img.draw(self.x, self.y, self.w, self.h)
        else:
            self.normal_img.draw(self.x, self.y, self.w, self.h)

        # 디버그용 bounding box
        # draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        if event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            if self.is_hover and self.on_click:
                self.on_click()  # 버튼 클릭 시 등록된 함수 실행